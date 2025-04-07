import logging

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат вывода
    handlers=[
        logging.FileHandler("app.log"),  # Запись логов в файл
        logging.StreamHandler()          # Вывод логов в консоль
    ]
)

# Используем логгер
logger = logging.getLogger(__name__) # в каждый файл __name__ названия файла
