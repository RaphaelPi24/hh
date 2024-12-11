from pathlib import Path
import base64

from aiohttp.web_fileresponse import extension


class Image: # DiagramFile FileManager
    path = Path("static/image_diagram")  # Относительный путь как объект Path
    extension = "png"

    @classmethod
    def delete(cls, names_cache):
        print("Процесс удаления изображений...")

        # Перебираем файлы в директории
        for file in cls.path.iterdir():
            if not file.is_file():
                continue

            name_file = file.stem  # Получаем имя файла без расширения
            if name_file in names_cache:
                continue

            try:
                file.unlink()  # Удаляем файл
                print(f'Удалено изображение: {file.name}')
            except Exception as e:
                print(f'Ошибка при удалении {file.name}: {e}')

    @classmethod
    def save(cls, filename: str, image: base64):

        directory = filename.parent
        if directory.exists() and not directory.is_dir():
            raise FileExistsError(f"Невозможно создать директорию: {directory} уже существует как файл")

        directory.mkdir(parents=True, exist_ok=True)

        filename.write_bytes(image)

    @classmethod
    def get_path(cls, title: str) -> Path:
        return cls.path / f"{title}.{cls.extension}"
