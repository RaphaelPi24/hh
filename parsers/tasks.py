import asyncio

from parsers.asynk_func import main_parsing


def process_profession_data(professions: str) -> None:
    asyncio.run(main_parsing(professions))
