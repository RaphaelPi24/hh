from pathlib import Path
import base64

class Image:
    path = Path("static/image_diagram")  # Относительный путь как объект Path

    def delete(self, names_cache):
        print("Процесс удаления изображений...")

        # Перебираем файлы в директории
        for file in self.path.iterdir():
            if file.is_file():
                name_file = file.stem  # Получаем имя файла без расширения
                if name_file not in names_cache:
                    try:
                        file.unlink()  # Удаляем файл
                        print(f'Удалено изображение: {file.name}')
                    except Exception as e:
                        print(f'Ошибка при удалении {file.name}: {e}')

    def save(self, pathfile: str, image: base64):
        # Преобразуем путь в абсолютный
        full_pathfile = Path(pathfile).resolve()  # Полный путь файла
        directory = full_pathfile.parent

        # Проверяем, существует ли элемент, и если да, это директория
        if directory.exists() and not directory.is_dir():
            raise FileExistsError(f"Невозможно создать директорию: {directory} уже существует как файл")

        # Создаём директорию, если она не существует
        directory.mkdir(parents=True, exist_ok=True)

        # Сохраняем файл
        with full_pathfile.open('wb') as f:
            f.write(image)

    def get_path(self, title: str) -> Path:
        return self.path / f"{title}.png"
