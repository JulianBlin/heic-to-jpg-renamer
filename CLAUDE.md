# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Script Python pour renommer en batch des photos à partir de leurs métadonnées EXIF, avec conversion HEIC vers JPEG.

## Dependencies

- `Pillow` (PIL) — image opening and EXIF extraction
- `pillow-heif` — HEIC/HEIF format support (registered via `pillow_heif.register_heif_opener()`)

Install: `pip install Pillow pillow-heif`

## Running

```bash
python multifolder.py /path/to/photos              # threads = nombre de CPUs
python multifolder.py /path/to/photos --workers 8   # 8 threads
```

Recursively walks all subfolders, converts HEIC to JPEG (quality=100, preserving EXIF), renames images to `YYYYMMDD_HHMMSS{.ext}` from EXIF date, skips already-renamed files, handles filename collisions with `_N` suffix, deletes HEIC source after conversion.

## Architecture

- **Collecte** : `collect_files()` liste tous les fichiers via `os.walk`
- **Traitement** : `ThreadPoolExecutor` dispatche chaque fichier individuellement (`process_file`)
- **Thread safety** : un `Lock` global protège uniquement le bloc `exists` + `rename` dans `safe_rename()` — la conversion et la lecture EXIF tournent en parallèle sans contention

## Key Conventions

- Naming format: `YYYYMMDD_HHMMSS{.ext}` derived from EXIF `DateTimeOriginal` or tag 306
- HEIC files are converted to JPEG then deleted
- All user-facing messages are in French
