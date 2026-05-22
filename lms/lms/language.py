"""Language helpers for LMS bilingual UI."""

from __future__ import annotations

import frappe

SUPPORTED_LANGUAGES = (
	{"code": "en", "label": "English"},
	{"code": "zh", "label": "中文"},
)

# Map UI codes to Frappe language codes used by Translation / User.language.
FRAPPE_LANGUAGE_BY_CODE = {
	"en": "en",
	"zh": "zh",
}


def normalize_language(language: str | None) -> str:
	"""Return a supported UI language code (`en` or `zh`)."""
	if not language:
		return "zh"

	value = str(language).strip().lower().replace("_", "-")
	if value in {"zh", "zh-cn", "zh-hans", "chinese", "中文"}:
		return "zh"
	if value in {"en", "en-us", "en-gb", "english"}:
		return "en"
	return "zh"


def frappe_language(code: str) -> str:
	"""Language code used by Frappe translation APIs."""
	return FRAPPE_LANGUAGE_BY_CODE.get(normalize_language(code), "zh")


def user_language_field(code: str) -> str:
	"""Value stored on User.language (Language master name when available)."""
	code = normalize_language(code)
	lang_name = frappe.db.get_value("Language", {"enabled": 1, "language_code": code}, "name")
	if lang_name:
		return lang_name
	return "Chinese" if code == "zh" else "English"


def get_current_language() -> str:
	"""Resolve the active UI language for the current request/session."""
	if frappe.session.user and frappe.session.user != "Guest":
		user_language = frappe.db.get_value("User", frappe.session.user, "language")
		if user_language:
			lang_code = frappe.db.get_value("Language", user_language, "language_code") or user_language
			return normalize_language(lang_code)

	cookie_language = frappe.request.cookies.get("preferred_language") if frappe.request else None
	if cookie_language:
		return normalize_language(cookie_language)

	system_language = frappe.db.get_single_value("System Settings", "language") or "zh"
	return normalize_language(system_language)


def set_current_language(language: str) -> str:
	"""Persist language for logged-in users or guests."""
	code = normalize_language(language)
	frappe_lang = frappe_language(code)
	user_lang = user_language_field(code)

	if frappe.session.user and frappe.session.user != "Guest":
		frappe.db.set_value("User", frappe.session.user, "language", user_lang, update_modified=False)
	else:
		frappe.local.cookie_manager.set_cookie("preferred_language", code)

	frappe.local.lang = frappe_lang
	return code


def get_language_payload() -> dict:
	code = get_current_language()
	return {
		"language": code,
		"frappe_language": frappe_language(code),
		"supported_languages": list(SUPPORTED_LANGUAGES),
	}
