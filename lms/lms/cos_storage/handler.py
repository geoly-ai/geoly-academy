"""Upload Frappe File attachments to Tencent Cloud COS (S3-compatible API)."""

from __future__ import annotations

import mimetypes
import os
import shutil

import frappe
from frappe.utils import cint


def is_cos_enabled() -> bool:
	return bool(frappe.conf.get("cos_enabled"))


def get_cos_config() -> dict | None:
	if not is_cos_enabled():
		return None

	required = ("cos_bucket", "cos_region", "cos_access_key", "cos_secret_key")
	missing = [key for key in required if not frappe.conf.get(key)]
	if missing:
		frappe.log_error(
			title="COS configuration incomplete",
			message=f"Missing keys: {', '.join(missing)}",
		)
		return None

	return {
		"bucket": frappe.conf.cos_bucket,
		"region": frappe.conf.cos_region,
		"endpoint": frappe.conf.get("cos_endpoint"),
		"access_key": frappe.conf.cos_access_key,
		"secret_key": frappe.conf.cos_secret_key,
		"folder_prefix": (frappe.conf.get("cos_folder_prefix") or "lms-files").strip("/"),
		"public_base_url": frappe.conf.get("cos_public_base_url"),
		"delete_local": cint(frappe.conf.get("cos_delete_local_after_upload")),
	}


def get_s3_client(config: dict):
	import boto3
	from botocore.client import Config

	endpoint = config["endpoint"] or f"https://cos.{config['region']}.myqcloud.com"
	return boto3.client(
		"s3",
		endpoint_url=endpoint,
		aws_access_key_id=config["access_key"],
		aws_secret_access_key=config["secret_key"],
		region_name=config["region"],
		config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
	)


def get_object_key(doc) -> str:
	config = get_cos_config()
	prefix = config["folder_prefix"]
	site = frappe.local.site
	# Keep keys stable and namespaced per site.
	return f"{prefix}/{site}/{doc.name}/{doc.file_name}"


def get_public_url(config: dict, key: str) -> str:
	if config.get("public_base_url"):
		return f"{config['public_base_url'].rstrip('/')}/{key}"

	bucket = config["bucket"]
	region = config["region"]
	return f"https://{bucket}.cos.{region}.myqcloud.com/{key}"


def get_file_content(doc) -> bytes:
	file_path = doc.get_full_path()
	if file_path and os.path.exists(file_path):
		with open(file_path, "rb") as file_obj:
			return file_obj.read()

	if not doc.get("cos_uploaded"):
		raise FileNotFoundError(f"Local file not found for File {doc.name}")

	config = get_cos_config()
	if not config:
		raise FileNotFoundError(f"COS is not configured for File {doc.name}")

	client = get_s3_client(config)
	response = client.get_object(Bucket=config["bucket"], Key=get_object_key(doc))
	return response["Body"].read()


def copy_file_to_path(doc, destination_path: str) -> str:
	file_path = doc.get_full_path()
	if file_path and os.path.exists(file_path):
		shutil.copyfile(file_path, destination_path)
		return destination_path

	if not doc.get("cos_uploaded"):
		raise FileNotFoundError(f"Local file not found for File {doc.name}")

	config = get_cos_config()
	if not config:
		raise FileNotFoundError(f"COS is not configured for File {doc.name}")

	client = get_s3_client(config)
	client.download_file(config["bucket"], get_object_key(doc), destination_path)
	return destination_path


def upload_file_to_cos(doc, method=None):
	"""Hook: push newly created File records to COS and update file_url."""
	if doc.get("cos_uploaded"):
		return

	config = get_cos_config()
	if not config:
		return

	if doc.file_url and str(doc.file_url).startswith(("http://", "https://")):
		# Already remote (e.g. re-save).
		return

	file_path = doc.get_full_path()
	if not file_path or not os.path.exists(file_path):
		return

	key = get_object_key(doc)
	client = get_s3_client(config)
	extra_args = {}
	content_type = mimetypes.guess_type(doc.file_name)[0]
	if content_type:
		extra_args["ContentType"] = content_type

	# Keep access control at the bucket/CDN layer. The deployment uses a
	# public-read/private-write bucket, and protected course videos are handled
	# by CDN URL authentication on read.

	with open(file_path, "rb") as file_obj:
		client.upload_fileobj(file_obj, config["bucket"], key, ExtraArgs=extra_args)

	public_url = get_public_url(config, key)
	doc.file_url = public_url
	doc.cos_uploaded = 1
	frappe.db.set_value(
		"File",
		doc.name,
		{
			"file_url": public_url,
			"cos_uploaded": 1,
		},
		update_modified=False,
	)

	if config["delete_local"]:
		try:
			os.remove(file_path)
		except OSError:
			frappe.log_error(title="COS local cleanup failed", message=file_path)


def delete_file_from_cos(doc, method=None):
	if not doc.get("cos_uploaded"):
		return

	config = get_cos_config()
	if not config:
		return

	try:
		client = get_s3_client(config)
		client.delete_object(Bucket=config["bucket"], Key=get_object_key(doc))
	except Exception:
		frappe.log_error(title="COS delete failed", message=frappe.get_traceback())
