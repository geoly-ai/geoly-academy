"""Load SPA translation fallbacks for Chinese UI."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import frappe


@lru_cache(maxsize=8)
def _load_zh_frontend_translations(mtime_ns: int) -> dict[str, str]:
	path = Path(__file__).with_name("zh_frontend.json")
	if not path.exists():
		return {}
	return json.loads(path.read_text(encoding="utf-8"))


def get_zh_frontend_translations() -> dict[str, str]:
	path = Path(__file__).with_name("zh_frontend.json")
	if not path.exists():
		return {}
	return _load_zh_frontend_translations(path.stat().st_mtime_ns)


def merge_translations(language_code: str, translations: dict | None) -> dict:
	"""Merge Frappe gettext dict with bundled zh fallback for LMS SPA."""
	merged = dict(translations or {})
	if language_code in {"zh", "zh-CN", "zh-cn", "Chinese"}:
		merged.update(get_zh_frontend_translations())
	return merged


def resolve_translation_language(code: str) -> str:
	"""Try common Frappe language codes until we get a non-empty catalog."""
	from frappe.translate import get_all_translations

	candidates = []
	for item in (code, "zh", "zh-CN", "zh_CN", "Chinese"):
		if item and item not in candidates:
			candidates.append(item)

	for lang in candidates:
		catalog = get_all_translations(lang) or {}
		if catalog:
			return lang
	return code
