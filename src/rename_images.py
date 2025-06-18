import os

def rename_images(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort()

    # Step 1: Rename all files to temporary names to avoid conflicts
    temp_files = []
    for index, filename in enumerate(files):
        old_path = os.path.join(directory, filename)
        temp_filename = f"temp_{index + 1}.tmp"
        temp_path = os.path.join(directory, temp_filename)
        os.rename(old_path, temp_path)
        temp_files.append(temp_path)
        print(f"Renamed {filename} to {temp_filename}")

    # Step 2: Rename temporary files to final names
    temp_files.sort(key=lambda x: int(os.path.basename(x).replace('temp_', '').replace('.tmp', '')))
    for index, temp_path in enumerate(temp_files):
        final_filename = f"{index + 1}.jpg"
        final_path = os.path.join(directory, final_filename)
        os.rename(temp_path, final_path)
        print(f"Renamed {os.path.basename(temp_path)} to {final_filename}")

if __name__ == "__main__":
    images_directory = "c:\\Users\\xyy\\Desktop\\cj\\src\\images"
    rename_images(images_directory)