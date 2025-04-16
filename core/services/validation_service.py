from pathlib import Path
import re

from loguru import logger


class Validator:

    def __init__(self):
        pass

    @staticmethod
    @logger.catch()
    def __path_existence(path: Path) -> bool:
        return path.exists()

    @staticmethod
    @logger.catch()
    def __drive_existence(path: Path) -> bool:
        drive_existence = Path(path.drive).exists() and bool(re.findall('.+:.+', str(path)))
        return drive_existence

    @logger.catch()
    def validate_game_path(self, path: Path):
        drive_existence = self.__drive_existence(path)
        path_existence = self.__path_existence(path)
        logger.debug(f'{path} - Full path: {path_existence}, Drive: {drive_existence}')
        return path_existence and drive_existence

    @logger.catch()
    def validate_original_path(self, path: Path, original_language: str):
        drive_existence = False
        path_existence = False
        if original_language is not None:
            path_existence = self.__path_existence(path / original_language)
            drive_existence = self.__drive_existence(path)
        logger.debug(f'{path}/{original_language} - Full path: {path_existence}, Drive: {drive_existence}')
        return path_existence and drive_existence

    @logger.catch()
    def validate_previous_path(self, path: Path):
        path_existence = self.__path_existence(path) and self.__drive_existence(path)
        logger.debug(f'{path} - Full path: {path_existence}')
        return path_existence

    @logger.catch()
    def validate_target_path(self, path: Path):
        path_existence = self.__drive_existence(path)
        logger.debug(f'drive - Full path: {path_existence}')
        return path_existence
