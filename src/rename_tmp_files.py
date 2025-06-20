import os

def rename_tmp_to_jpg(directory):
    for filename in os.listdir(directory):
        if filename.startswith('temp_') and filename.endswith('.tmp'):
            old_path = os.path.join(directory, filename)
            new_filename = filename.replace('temp_', '').replace('.tmp', '.jpg')
            new_path = os.path.join(directory, new_filename)
            try:
                os.rename(old_path, new_path)
                print(f"Renamed {filename} to {new_filename}")
            except OSError as e:
                print(f"Error renaming {filename}: {e}")

if __name__ == "__main__":
    images_directory = "c:\\Users\\xyy\\Desktop\\cj\\src\\images"
    rename_tmp_to_jpg(images_directory)