# Modifications to Frappe LMS (v2.52.1 base)

This fork is based on [frappe/lms](https://github.com/frappe/lms) tag `v2.52.1` and is licensed under **AGPL-3.0-or-later**.

## Changes

### Bilingual UI (English / 中文)

- `lms/lms/language.py` – language resolution and persistence
- `lms/lms/api.py` – `get_language`, `set_language`, enhanced `get_translations`
- `frontend/src/translation.js` – client-side language switching
- `frontend/src/components/LanguageSwitcher.vue` – UI switcher
- Layout integration in sidebar, mobile, and no-sidebar views
- `lms/www/_lms.py` – boot payload includes language metadata

### Tencent Cloud COS file storage

- `lms/lms/cos_storage/handler.py` – S3-compatible upload/delete for `File` attachments
- `lms/hooks.py` – `File` document hooks
- `pyproject.toml` – `boto3` dependency
- `frontend/src/components/UploadPlugin.vue` – extended courseware file types
- `frontend/src/utils/upload.js` – render/download support for office archives

### AGPL compliance

- `frontend/src/components/SourceCodeLink.vue` – prominent source offer in UI
- Configure `lms_source_code_url` in site config (see deployment docs)

## Corresponding source

Publish this repository (or your fork) and set `lms_source_code_url` to that public URL so network users can obtain the corresponding source under AGPL section 13.
