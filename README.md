# AlbumPhoto

Script Python pour organiser automatiquement des photos en les renommant selon leur date EXIF et en convertissant les fichiers HEIC en JPEG.

## Fonctionnalités

- Parcours récursif des sous-dossiers
- Conversion HEIC/HEIF vers JPEG (qualité 100, métadonnées EXIF préservées)
- Renommage automatique au format `YYYYMMDD_HHMMSS.ext` à partir de la date EXIF
- Gestion des doublons (ajout d'un suffixe `_1`, `_2`, etc.)
- Ignore les fichiers déjà renommés

## Prérequis

- Python 3
- [Pillow](https://pillow.readthedocs.io/)
- [pillow-heif](https://github.com/bigcat88/pillow_heif)

```bash
pip install Pillow pillow-heif
```

## Utilisation

```bash
python multifolder.py /chemin/vers/les/photos
```

Le script va :
1. Parcourir récursivement le dossier indiqué
2. Convertir les fichiers `.heic` / `.heif` en `.jpeg` (puis supprimer l'original)
3. Renommer les fichiers `.jpg`, `.jpeg`, `.png` selon la date de prise de vue EXIF

## Formats supportés

| Format | Action |
|---|---|
| `.heic`, `.heif` | Conversion en JPEG + renommage |
| `.jpg`, `.jpeg`, `.png` | Renommage uniquement |
