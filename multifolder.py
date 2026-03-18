import os
import re
from PIL import Image, ExifTags
import pillow_heif
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

pillow_heif.register_heif_opener()

DATE_PATTERN = re.compile(r'^\d{8}_\d{6}')
rename_lock = Lock()

def is_already_renamed(filename):
    name = os.path.splitext(filename)[0]
    return bool(DATE_PATTERN.match(name))

def convert_heic_to_jpeg_with_exif(heic_path, jpeg_path):
    with Image.open(heic_path) as heic_image:
        exif_data = heic_image.info.get("exif", None)
        icc_profile = heic_image.info.get("icc_profile", None)
        save_kwargs = {"quality": 100, "subsampling": 0}
        if exif_data:
            save_kwargs["exif"] = exif_data
        if icc_profile:
            save_kwargs["icc_profile"] = icc_profile
        heic_image.save(jpeg_path, "JPEG", **save_kwargs)
    return jpeg_path

def get_date_taken(img_path):
    with Image.open(img_path) as img:
        img_exif = img.getexif()
        if img_exif is None:
            return None
        exif_ifd = img_exif.get_ifd(0x8769)
        date = exif_ifd.get(36867)  # DateTimeOriginal
        if date is None:
            date = img_exif.get(306)  # Fallback: DateTime
        return date

def safe_rename(img_path, output_folder, date):
    new_name = date.replace(' ', '_').replace(':', '')
    file_extension = os.path.splitext(img_path)[-1]
    with rename_lock:
        full_new_name = os.path.join(output_folder, new_name + file_extension)
        counter = 1
        while os.path.exists(full_new_name):
            full_new_name = os.path.join(output_folder, f"{new_name}_{counter}{file_extension}")
            counter += 1
        os.rename(img_path, full_new_name)
    return full_new_name

def process_file(img_path, output_folder):
    file = os.path.basename(img_path)
    file_extension = os.path.splitext(file)[-1].lower()

    if is_already_renamed(file):
        return f"{file} -> déjà renommé, on skip"

    if file_extension in ['.heic', '.heif']:
        jpeg_path = img_path.rsplit(file_extension, 1)[0] + '.jpeg'
        convert_heic_to_jpeg_with_exif(img_path, jpeg_path)
        os.remove(img_path)
        date = get_date_taken(jpeg_path)
        if date is None:
            return f"Impossible de renommer {jpeg_path} : date EXIF introuvable."
        new_path = safe_rename(jpeg_path, output_folder, date)
        return f"Conversion + renommage : {img_path} -> {new_path}"

    elif file_extension in ['.jpg', '.jpeg', '.png']:
        date = get_date_taken(img_path)
        if date is None:
            return f"Impossible de renommer {img_path} : date EXIF introuvable."
        new_path = safe_rename(img_path, output_folder, date)
        return f"Renommage : {img_path} -> {new_path}"

    else:
        return f"{file} -> Ce fichier n'est pas une image valide."

def collect_files(folder):
    tasks = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            tasks.append((os.path.join(root, file), root))
    return tasks

def process_folder(folder, workers):
    tasks = collect_files(folder)
    print(f"{len(tasks)} fichiers à traiter avec {workers} threads.")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_file, img_path, output_folder): img_path
            for img_path, output_folder in tasks
        }
        for future in as_completed(futures):
            img_path = futures[future]
            try:
                print(future.result())
            except Exception as e:
                print(f"Erreur sur {img_path} : {e}")

parser = argparse.ArgumentParser()
parser.add_argument("folder", help="Dossier contenant les images", type=str)
parser.add_argument("--workers", type=int, default=os.cpu_count(), help="Nombre de threads (défaut: nombre de CPUs)")
args = parser.parse_args()

process_folder(args.folder, args.workers)
