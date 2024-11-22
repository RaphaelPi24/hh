import base64
import os


class Image:
    path = r"C:\papka\net\_hh\static\image_diagram" # относителььный путь petlib

    def delete(self, names_cache):
        print("Процесс удаления изображений...")

        files = os.listdir(self.path)
        for file in files:
            name_file = file.split('.')[0]
            full_file_path = os.path.join(self.path, file)
            if name_file not in names_cache:
                try:
                    os.remove(full_file_path)
                    print(f'Удалено изображение: {file}') # ????
                except Exception as e:
                    print(f'Ошибка при удалении {file}: {e}')

    def save(self, name_file: str, image: base64):
        pathfile = os.path.join(self.path, name_file)
        with open(pathfile, 'wb') as f:
            f.write(image)
