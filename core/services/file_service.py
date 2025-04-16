from pathlib import Path
import re

from loguru import logger

from core.services.validation_service import Validator


class Prepper:

    @logger.catch()
    def __init__(self, game_path: Path = None, original_mode_path: Path = None,
                 target_path: Path = None, previous_path: Path = None):
        self._game_path = game_path
        self._original_mode_path = original_mode_path
        self._target_path = target_path
        self._previous_path = previous_path

        self._file_hierarchy = []
        self._previous_files = []
        self._original_files_size = 0

        self.validator = Validator()

        self._game_path_validate_result = False
        self._original_mode_path_validate_result = False
        self._previous_path_validate_result = False
        self._target_path_validate_result = False

    @logger.catch()
    def set_game_path(self, game_path: str):
        r"""Должен формировать путь до папки с локализациями (game/localization, localisation и т.п.)"""
        self._game_path = Path(game_path)
        self._game_path_validate_result = self.validator.validate_game_path(self._game_path)

    @logger.catch()
    def get_game_path(self) -> Path:
        return self._game_path

    @logger.catch()
    def get_game_path_validate_result(self) -> bool:
        return self._game_path_validate_result

    @logger.catch()
    def set_original_mode_path(self, original_mode_path: str, original_language: str):
        if original_mode_path == '':
            self._original_mode_path_validate_result = self.validator.validate_original_path(Path(original_mode_path),
                                                                                             original_language)
            self._original_mode_path = Path(original_mode_path)
        else:
            self._original_mode_path = Path(original_mode_path)
            self._original_mode_path_validate_result = self.validator.validate_original_path(self._original_mode_path,
                                                                                             original_language)
            if self.get_original_mode_path_validate_result():
                self._create_localization_hierarchy(original_language=original_language)

    def get_original_mode_path(self) -> Path:
        return self._original_mode_path

    def get_original_files_size(self) -> int:
        return self._original_files_size

    def get_original_mode_path_validate_result(self) -> bool:
        return self._original_mode_path_validate_result

    @logger.catch()
    def set_previous_path(self, previous_path: str, target_language: str):
        if previous_path:
            self._previous_path = Path(previous_path)
            self._previous_path_validate_result = self.validator.validate_previous_path(
                self._previous_path / target_language)
        else:
            self._previous_path = Path('.')
            self._previous_path_validate_result = False

    def get_previous_path(self) -> Path:
        return self._previous_path

    def get_previous_path_validate_result(self) -> bool:
        return self._previous_path_validate_result

    @logger.catch()
    def set_target_path(self, target_path: str):
        self._target_path = Path(target_path)
        self._target_path_validate_result = self.validator.validate_target_path(self._target_path)

    def get_target_path(self) -> Path:
        return self._target_path

    def get_target_path_validate_result(self) -> bool:
        return self._target_path_validate_result

    @logger.catch()
    def _create_localization_hierarchy(self, original_language=None):
        r"""Создает иерархию файлов из директории _original_mode_path, а также считает размер всех файлов в сумме"""
        self._original_files_size = 0
        self._file_hierarchy = []
        for step in self._original_mode_path.rglob(f'*l_{original_language}*'):
            if step.is_file() and step.suffix in ['.yml', '.txt', ]:
                self._file_hierarchy.append(step.relative_to(self._original_mode_path))
                self._original_files_size += step.stat().st_size

    def get_file_hierarchy(self) -> list:
        r"""Возвращается путь ко всем файлам, относительно пути, расположения локализации основного мода.
                Названия файлов не изменены под новый(target_language) язык"""
        return self._file_hierarchy

    @logger.catch()
    def get_previous_files(self, target_language: str):
        self._previous_files = []
        replace_path = self._previous_path / 'replace' / target_language
        target_path = self._previous_path / target_language
        if replace_path.exists():
            for file in replace_path.rglob('*'):
                self._previous_files.append(file)
        for step in target_path.rglob('*'):
            if step.is_file():
                self._previous_files.append(step)
        return self._previous_files
