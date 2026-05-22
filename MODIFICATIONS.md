# Modifications to Frappe LMS (v2.54.2 base)

This fork is based on [frappe/lms](https://github.com/frappe/lms) `main` at tag `v2.54.2` and is licensed under **AGPL-3.0-or-later**.

## Changes

### Bilingual UI (English / 中文)

- `lms/lms/language.py` – language resolution and persistence
- `lms/lms/api.py` – `get_language`, `set_language`, enhanced `get_translations`
- `frontend/src/translation.js` – client-side language switching
- `frontend/src/components/LanguageSwitcher.vue` – UI switcher
- Layout integration in sidebar, mobile, and no-sidebar views
- `lms/www/_lms.py` – boot payload includes language metadata
- `lms/lms/translations/zh_frontend.json` – Simplified Chinese fallback
  used by the SPA. Notable terminology decisions:
  - `Batch / Batches` is consistently rendered as **班级**
    (English `class` style) instead of the literal **批次**.
    The English term `batch` matches Frappe's own docs page title
    "Create a Class" (https://docs.frappelms.com/batch-creation/create-a-batch.html).
  - `Class:` / "Attendance for Class" / "Your class on …" / "This class
    has ended" all refer to live class sessions and are translated as
    **直播课** to avoid colliding with `Course → 课程`.
  - `Batch Evaluator` is rendered as **班级评估人** (consistent with
    the existing site-wide `Evaluator → 评估人` translation).

#### C-side language lock (forced Chinese)

- The C-side portal (`frontend/src/components/Sidebar/AppSidebar.vue`,
  `frontend/src/components/Layouts/MobileLayout.vue`,
  `frontend/src/components/Layouts/NoSidebarLayout.vue`) no longer renders
  `LanguageSwitcher.vue`. The component file is kept for reference.
- `frontend/src/translation.js` forces the active language to `zh`,
  resets the `lms_preferred_language` localStorage key on app boot, and
  ignores `window.boot.language` for switching purposes.
- `lms/lms/language.py` defaults to `zh` when no language is provided or
  when the `System Settings.language` value is empty.

### Tencent Cloud COS file storage

- `lms/lms/cos_storage/handler.py` – S3-compatible upload/delete for `File` attachments
- `lms/hooks.py` – `File` document hooks
- `pyproject.toml` – `boto3` dependency
- `frontend/src/components/UploadPlugin.vue` – extended courseware file types
- `frontend/src/utils/upload.js` – render/download support for office archives

### AGPL compliance

- `frontend/src/components/AboutDialog.vue` – modal that exposes app
  version, AGPL notice, upstream link, license link, and the deployment's
  `lms_source_code_url` (with a visible warning if not configured).
- `frontend/src/components/Sidebar/AppSidebar.vue` – `Info` icon next to
  the "Powered by Frappe Learning" icon opens the About dialog.
- `frontend/src/components/Layouts/MobileLayout.vue` – the `More` menu
  exposes an `About` entry that opens the same dialog.
- `frontend/src/components/Layouts/NoSidebarLayout.vue` – login page
  shows a discreet `About` link bottom-right.
- `frontend/src/components/SourceCodeLink.vue` is no longer rendered
  (kept on disk as an inline-banner fallback).
- Configure `lms_source_code_url` in site config (see deployment docs).

## Corresponding source

Publish this repository (or your fork) and set `lms_source_code_url` to that public URL so network users can obtain the corresponding source under AGPL section 13.

Do not point `lms_source_code_url` at the upstream `frappe/lms` repository after adding local modifications such as COS integration or custom translations. The link should resolve to the exact corresponding source for the deployed version.
