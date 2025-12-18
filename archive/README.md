# Archive Folder

This folder contains legacy files from the refactoring process. These files are kept for reference but are no longer used in the production codebase.

## Contents

### `old_entry_points/`
Legacy entry point files that have been superseded by `run.py`:
- `app.py` - Old Streamlit-only entry point
- `app_legacy.py` - Even older version
- `main.py` - Original CLI entry point

### Legacy Folders
Old directory structures that have been consolidated into `src/`:
- `models_old/` - Superseded by `src/models.py`
- `utils_old/` - Superseded by `src/utils/`
- `scrapers_old/` - Superseded by `src/scrapers/`
- `config_old/` - Superseded by `config.py` (if present)

## Why Keep These?

These files are archived (not deleted) for:
1. **Reference** - If you need to check old implementation details
2. **Comparison** - To see how the refactoring improved the code
3. **Safety** - In case any edge-case logic needs to be recovered

## Can I Delete This Folder?

Yes, if you're confident the new codebase is working properly. The production code doesn't depend on anything in this folder.

---

*Created during refactoring on December 18, 2025*

