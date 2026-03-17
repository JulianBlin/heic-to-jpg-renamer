import os
import re
from PIL import Image, ExifTags
import pillow_heif
import argparse

pillow_heif.register_heif_opener()

DATE_PATTERN = re.compile(r'^\d{8}_\d{6}')

def is_already_renamed(filename):
    name = os.path.splitext(filename)[0]
    return bool(DATE_PATTERN.match(name))

def convert_heic_to_jpeg_with_exif(heic_path, jpeg_path):
    try:
        heic_image = Image.open(heic_path)
        exif_data = heic_image.info.get("exif", None)
        heic_image.save(jpeg_path, "JPEG", quality=100, subsampling=0, exif=exif_data)
        print(f"Conversion réussie avec EXIF : {heic_path} -> {jpeg_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de la conversion : {e}")
        return False

def rename_jpeg(img_path, output_folder):
    try:
        img = Image.open(img_path)
        img_exif = img.getexif()
        if img_exif is None:
            print(f"Aucune donnée EXIF trouvée pour {img_path}.")
            return
        exif_found = False
        for key, val in img_exif.items():
            tag_name = ExifTags.TAGS.get(key, key)
            if tag_name == "DateTimeOriginal" or key == 306:
                exif_found = True
                new_name = val.replace(' ', '_').replace(':', '')
                file_extension = os.path.splitext(img_path)[-1]
                full_new_name = os.path.join(output_folder, new_name + file_extension)
                counter = 1
                while os.path.exists(full_new_name):
                    full_new_name = os.path.join(output_folder, f"{new_name}_{counter}{file_extension}")
                    counter += 1
                os.rename(img_path, full_new_name)
                print(f"Renommage : {img_path} -> {full_new_name}")
                break
        if not exif_found:
            print(f"Impossible de renommer {img_path} : date EXIF introuvable.")
    except Exception as e:
        print(f"Erreur lors du renommage de {img_path} : {e}")

def process_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            img_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[-1].lower()

            if is_already_renamed(file):
                print(f"{file} -> déjà renommé, on skip")
                continue

            if file_extension in ['.heic', '.heif']:
                img_path_jpg = img_path.rsplit(file_extension, 1)[0] + '.jpeg'
                if convert_heic_to_jpeg_with_exif(img_path, img_path_jpg):
                    os.remove(img_path)
                    print(f"Fichier HEIC supprimé : {img_path}")
                    rename_jpeg(img_path_jpg, root)
                else:
                    print(f"Conversion échouée pour {img_path}. Le fichier source est conservé.")
            elif file_extension in ['.jpg', '.jpeg', '.png']:
                rename_jpeg(img_path, root)
            else:
                print(f"{file} -> Ce fichier n'est pas une image valide.")

parser = argparse.ArgumentParser()
parser.add_argument("folder", help="Dossier contenant les images", type=str)
args = parser.parse_args()

process_folder(args.folder)
