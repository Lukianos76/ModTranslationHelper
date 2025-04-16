import json
from pathlib import Path
from typing import KeysView

from loguru import logger

from settings import BASE_DIR


class Settings:
    __settings = {
        'last_game_directory': "",
        'last_original_mode_directory': "",
        'last_previous_directory': "",
        'last_target_directory': "",
        'last_supported_source_language': 'english',
        'last_supported_target_language': 'english',
        'last_original_language': "english",
        'last_target_language': "russian",

        'translator_api': "GoogleTranslator",
        'protection_symbol': "☻",

        'app_language': "Русский",
        'games': {},
        'selected_game': 'Crusader Kings 3',
        'app_size': [1300, 700],
        'app_position': [100, 50],
    }

    @logger.catch()
    def __init__(self, local_data_path: Path | None):
        self.__local_data_path = local_data_path
        if self.__local_data_path:
            if self.__local_data_path.exists() and (self.__local_data_path / 'settings.json').exists():
                with (self.__local_data_path / 'settings.json').open(mode='r', encoding='utf-8-sig') as settings:
                    self.__settings = self.__settings | json.load(settings)
            else:
                Path.mkdir(self.__local_data_path, exist_ok=True)
                logger.debug(f'Settings directory - created: {local_data_path}')
                self.save_settings_data()
            self.disable_original_line = False
        else:
            logger.warning(f'settings storage: {local_data_path}: not exists')

        self.__init_games()

    @logger.catch()
    def __init_games(self):
        game_supported_languages = BASE_DIR / 'game_supported_languages.json'
        with game_supported_languages.open(mode='r', encoding='utf-8-sig') as file:
            self.__settings['games'] = json.load(file)

    def get_games(self) -> KeysView:
        return self.__settings.get('games').keys()

    def set_selected_game(self, game: str):
        self.__settings['selected_game'] = game

    def get_selected_game(self):
        return self.__settings.get('selected_game')

    def get_game_languages(self, game: str):
        return self.__settings.get('games').get(game, [])

    def set_last_game_directory(self, value: Path):
        self.__settings['last_game_directory'] = str(value)

    def get_last_game_directory(self) -> str:
        return self.__settings.get('last_game_directory', '')

    def set_last_original_mode_directory(self, value: Path):
        self.__settings['last_original_mode_directory'] = str(value)

    def get_last_original_mode_directory(self) -> str:
        return self.__settings.get('last_original_mode_directory', '')

    def set_last_previous_directory(self, value: Path):
        self.__settings['last_previous_directory'] = str(value)

    def get_last_previous_directory(self) -> str:
        return self.__settings.get('last_previous_directory', '')

    def set_last_target_directory(self, value: Path):
        self.__settings['last_target_directory'] = str(value)

    def get_last_target_directory(self) -> str:
        return self.__settings.get('last_target_directory', '')

    def set_last_languages(self, original, target):
        self.__settings['last_original_language'] = original
        self.__settings['last_target_language'] = target

    def set_last_supported_source_language(self, source):
        self.__settings['last_supported_source_language'] = source

    def set_last_supported_target_language(self, target):
        self.__settings['last_supported_target_language'] = target

    def set_translator_api(self, translator_api):
        self.__settings['translator_api'] = translator_api

    def set_protection_symbol(self, symbol):
        self.__settings['protection_symbol'] = symbol

    def set_app_language(self, value):
        self.__settings['app_language'] = value

    def set_app_size(self, width, height):
        self.__settings['app_size'] = [width, height]

    def set_app_position(self, x, y):
        self.__settings['app_position'] = [x, y]

    def get_last_original_language(self):
        return self.__settings.get('last_original_language', 'english')

    def get_last_target_language(self):
        return self.__settings.get('last_target_language', 'russian')

    def get_last_supported_source_language(self):
        return self.__settings.get('last_supported_source_language', 'english')

    def get_last_supported_target_language(self):
        return self.__settings.get('last_supported_target_language', 'english')

    def get_translator_api(self):
        return self.__settings.get('translator_api', None)

    def get_protection_symbol(self):
        return self.__settings.get('protection_symbol', None)

    def get_app_language(self):
        return self.__settings.get('app_language', 0)

    def get_app_size(self):
        return self.__settings.get('app_size', None)

    def get_app_position(self) -> [int, int]:
        return self.__settings.get('app_position', None)

    def save_settings_data(self):
        if self.__local_data_path is not None:
            with (self.__local_data_path / 'settings.json').open(mode='w', encoding='utf-8-sig') as settings:
                json.dump(self.__settings, settings, indent=4)
