"""CDN URL authentication helpers for protected lesson media playback."""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from urllib.parse import quote, urlsplit, urlunsplit

import frappe
from frappe.utils import cint


VIDEO_FILE_TYPES = {"mov", "mp4", "avi", "mkv", "webm"}


def get_cdn_auth_config() -> dict | None:
	if not cint(frappe.conf.get("cdn_auth_enabled")):
		return None

	key = frappe.conf.get("cdn_auth_key")
	base_url = frappe.conf.get("cdn_auth_base_url") or frappe.conf.get("cos_public_base_url")
	if not key or not base_url:
		frappe.log_error(
			title="CDN auth configuration incomplete",
			message="Missing cdn_auth_key or cdn_auth_base_url",
		)
		return None

	return {
		"base_url": str(base_url).rstrip("/"),
		"key": str(key),
		"sign_param": frappe.conf.get("cdn_auth_sign_param") or "sign",
		"uid": frappe.conf.get("cdn_auth_uid") or "0",
		"ttl": cint(frappe.conf.get("cdn_auth_ttl_seconds")) or 21600,
	}


def sign_lesson_media_urls(content: str | None) -> str | None:
	if not content:
		return content

	config = get_cdn_auth_config()
	if not config:
		return content

	try:
		data = json.loads(content)
	except Exception:
		frappe.log_error(title="CDN auth content parse failed", message=frappe.get_traceback())
		return content

	if not isinstance(data, dict):
		return content

	blocks = data.get("blocks")
	if not isinstance(blocks, list):
		return content

	for block in blocks:
		if not isinstance(block, dict):
			continue
		if block.get("type") != "upload":
			continue

		block_data = block.get("data") or {}
		file_url = block_data.get("file_url")
		file_type = _get_video_file_type(block_data.get("file_type"), file_url)
		if file_type not in VIDEO_FILE_TYPES or not file_url:
			continue

		play_url = get_cdn_auth_url(file_url, config)
		if play_url:
			block_data["play_url"] = play_url
			block_data["play_url_expires_in"] = config["ttl"]

	return json.dumps(data, ensure_ascii=False)


def get_cdn_auth_url(file_url: str, config: dict | None = None) -> str | None:
	config = config or get_cdn_auth_config()
	if not config:
		return None

	cdn_url = _to_cdn_url(file_url, config["base_url"])
	if not cdn_url:
		return None

	parsed = urlsplit(cdn_url)
	if parsed.query:
		# Tencent CDN TypeA does not support signing URLs that already contain
		# query parameters.
		frappe.log_error(
			title="CDN auth skipped for URL with query",
			message=file_url,
		)
		return None

	timestamp = int(time.time()) + config["ttl"]
	rand = secrets.token_hex(4)
	uid = config["uid"]
	path = parsed.path or "/"
	md5hash = hashlib.md5(
		f"{path}-{timestamp}-{rand}-{uid}-{config['key']}".encode()
	).hexdigest()
	sign_value = f"{timestamp}-{rand}-{uid}-{md5hash}"
	query = f"{config['sign_param']}={sign_value}"

	return urlunsplit((parsed.scheme, parsed.netloc, path, query, ""))


@frappe.whitelist()
def get_signed_media_url(file_url: str, file_type: str | None = None) -> dict:
	video_file_type = _get_video_file_type(file_type, file_url)
	if video_file_type not in VIDEO_FILE_TYPES:
		return {"play_url": None, "play_url_expires_in": 0}

	config = get_cdn_auth_config()
	if not config:
		return {"play_url": None, "play_url_expires_in": 0}

	return {
		"play_url": get_cdn_auth_url(file_url, config),
		"play_url_expires_in": config["ttl"],
	}


def _to_cdn_url(file_url: str, base_url: str) -> str | None:
	parsed = urlsplit(file_url)
	if parsed.scheme not in {"http", "https"} or not parsed.netloc:
		return None

	base = urlsplit(base_url if "://" in base_url else f"https://{base_url}")
	path = quote(parsed.path or "/", safe="/-_.~%")
	return urlunsplit((base.scheme or "https", base.netloc, path, parsed.query, ""))


def _get_video_file_type(file_type: str | None, file_url: str | None) -> str:
	value = str(file_type or "").lower().strip().lstrip(".")
	if "/" in value:
		value = value.rsplit("/", 1)[-1]
	if value in VIDEO_FILE_TYPES:
		return value

	path = urlsplit(file_url or "").path
	value = path.rsplit(".", 1)[-1].lower() if "." in path else ""
	return value if value in VIDEO_FILE_TYPES else ""
