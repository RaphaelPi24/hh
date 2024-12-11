import base64
from pathlib import Path

from log import logger


class Image:  # DiagramFile FileManager
    path = Path("static/image_diagram")  # Относительный путь как объект Path
    extension = "png"

    @classmethod
    def delete(cls, names_cache):
        logger.info("Процесс удаления изображений...")

        # Перебираем файлы в директории
        for file in cls.path.iterdir():
            if not file.is_file():
                continue

            name_file = file.stem  # Получаем имя файла без расширения
            if name_file in names_cache:
                continue

            try:
                file.unlink()  # Удаляем файл
                logger.info(f'Удалено изображение: {file.name}')
            except Exception as e:
                logger.info(f'Ошибка при удалении {file.name}: {e}')

    @classmethod
    def save(cls, filename: str, image: base64):
        directory = filename.parent
        filename.write_bytes(image)

    @classmethod
    def get_path(cls, title: str) -> Path:
        return cls.path / f"{title}.{cls.extension}"
