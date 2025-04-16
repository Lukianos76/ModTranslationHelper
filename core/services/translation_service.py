import re
import time
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal
from deep_translator import GoogleTranslator
from deepl import QuotaExceededException

from info_data import InfoData, FileInfoData
from languages.language_constants import LanguageConstants
from loguru import logger
from parsers.modern_paradox_parser import ModernParadoxParser
from shielded_values import ShieldedValues
from translators.translator_manager import TranslatorManager
from core.services.file_service import Prepper


class BasePerformer(QObject):
    info_data: InfoData
    file_info_data: FileInfoData

    info_console_value = pyqtSignal(str)
    info_label_value = pyqtSignal(str)
    progress_bar_value = pyqtSignal(float)
    finish_thread = pyqtSignal(InfoData)

    @logger.catch()
    def __init__(
            self,
            paths: Prepper,
            translator: TranslatorManager = None,
            original_language: str = None,
            target_language: str = None,
            need_translate: bool = False,
            need_translate_tuple: tuple | None = None,
            disable_original_line: bool = False,
            protection_symbol: str = "☻"
    ):
        super(BasePerformer, self).__init__()
        self._paths = paths
        self._original_language = original_language
        self._target_language = target_language
        self._translator = translator
        self._need_translate_list = need_translate_tuple if need_translate is True else tuple()
        self._disable_original_line = disable_original_line
        self._protection_symbol = protection_symbol

        self._shielded_values = ShieldedValues.get_common_pattern()

        self._start_running_time = None
        self._original_language_list = {}
        self._current_process_file: str = ''
        self._current_original_lines = []
        self._original_vanilla_dictionary = {}
        self._target_vanilla_dictionary = {}
        self._previous_version_dictionary = {}
        self._modified_values = {}
        self._translated_list = []

    @logger.catch()
    def _calculate_time_delta(self, start_time: float = None) -> str:
        if not start_time:
            start_time = self._start_running_time
        current_time = time.time()
        delta = current_time - start_time
        return time.strftime('%H:%M:%S', time.gmtime(delta))

    @logger.catch()
    def _create_directory_hierarchy(self):
        info = f"{LanguageConstants.start_forming_hierarchy} {self._calculate_time_delta()}\n"
        self.info_console_value.emit(self._change_text_style(info, 'green'))
        self.info_label_value.emit(LanguageConstants.forming_process)
        logger.debug(f'{info}')
        if not self._paths.get_target_path().exists():
            logger.debug(f'Making target directories')
            self._paths.get_target_path().mkdir(parents=True)
        logger.debug(f'Hierarchy creating start.')
        for file in self._paths.get_file_hierarchy():
            file: Path
            logger.debug(f'Creating {str(file)}')
            directory = Path(str(file).replace(self._original_language, self._target_language)).parent
            try:
                if not (self._paths.get_target_path() / directory).exists():
                    (self._paths.get_target_path() / directory).mkdir(parents=True)
                    info = f"{LanguageConstants.folder_created} {directory} - {self._calculate_time_delta()}\n"
                    self.info_console_value.emit(info)
            except Exception as error:
                error_text = f"{LanguageConstants.error_with_folder_creating} {directory}:" \
                             f"{error}"
                self.info_console_value.emit(self._change_text_style(error_text, 'red'))
                self.info_label_value.emit(self._change_text_style(f'{LanguageConstants.thread_stopped}', 'red'))
                self.finish_thread.emit()

    @logger.catch()
    def _create_original_language_dictionary(self):
        r"""Создает словарь, состоящий из номера строки, в качестве ключа и словаря, в качестве значения
        Каждый словарь содержит пару ключ-значение: key: 'key', value: 'value'
        К применру: 11: {'key': 'AI_UNIT_TOOLTIP_UNIT_STACK_NO_ORDER:0',
                        'value': '" No order."'},
        Здесь 11 - номер строки, а key - ключ(идентификатор) полной строки value.
        А также в value уже обрезаны пробелы и  символы переноса строки справа"""
        pass

    @logger.catch()
    def _create_game_localization_dictionary(self):
        pass

    @logger.catch()
    def _get_lines_dictionary(self, file: Path) -> dict:
        pass

    @logger.catch()
    def _create_previous_version_dictionary(self):
        pass

    @logger.catch()
    def _create_translated_list(self, line_number: int, key_value: dict):
        pass

    @logger.catch()
    def _compare_with_previous(self, key_value) -> str:
        pass

    @logger.catch()
    def _compare_with_vanilla(self, key_value: dict) -> str:
        pass

    @logger.catch()
    def _translate_line(self, translator: GoogleTranslator | None, key_value: dict) -> str:
        pass

    @logger.catch()
    def _modify_line(self, line: str, pattern: str | None = r"\[.*?\]", flag: str | None = None) -> str | None:
        r"""При флаге "modify" позволяет заменить некоторые части строки по шаблону на скрытую, ничего не обозначающую
        переменную. При флаге "return_normal_view" позволяет вернуть нормальный вид строки по словарю параметров"""
        match flag:
            case "modify":
                self._modified_values = {}
                shadow_number = 0
                regular_groups = re.findall(pattern=pattern, string=line)
                logger.debug(f'Found params for modify - {regular_groups}')
                if regular_groups:
                    for step in regular_groups:
                        self._modified_values[shadow_number] = step
                        if self._translator == "GoogleTranslator":
                            line = line.replace(step, f"{self._protection_symbol}_{shadow_number}")
                        elif self._translator == "DeepLTranslator":
                            line = line.replace(step, f'<span translate="no">{step}</span>')
                        shadow_number += 1
                return line
            case "return_normal_view":
                if self._translator == "GoogleTranslator":
                    for key, value in self._modified_values.items():
                        line = line.replace(f'☻_{key}', value)
                if self._translator == "DeepLTranslator":
                    tags = re.findall(pattern=r'(<[^>]*translate=\"no\"[^>]*>).*?(<[^>]*>)', string=line)
                    for open_tag, close_tag in tags:
                        line = line.replace(open_tag, '').replace(close_tag, '')
                return line
            case _:
                self.info_console_value(LanguageConstants.error_with_modification)
                self.finish_thread.emit()

    @staticmethod
    @logger.catch()
    def _change_text_style(text: str, flag):
        match flag:
            case 'red':
                return f'<span style=\" color: red;\">' + text + '</span>'
            case 'green':
                return f'<span style=\" color: green;\">' + text + '</span>'
            case 'orange':
                return f'<span style=\" color: orange;\">' + text + '</span>'

    @logger.catch()
    def _process_data(self):
        r"""Здесь происходит процесс обработки файлов. Последовательное открытие, создание и запись"""
        pass

    def run(self):
        logger.info(f'Process start')
        self._start_running_time = time.time()
        self._create_directory_hierarchy()
        self._create_game_localization_dictionary()
        if self._paths.get_previous_path_validate_result():
            self._create_previous_version_dictionary()
        self._process_data()
        info = f"{LanguageConstants.final_time} {self._calculate_time_delta()}"
        self.info_console_value.emit(self._change_text_style(info, 'orange'))
        self.info_label_value.emit(LanguageConstants.final)
        self.finish_thread.emit(self.info_data)


class ModernParadoxGamesPerformer(BasePerformer):

    def __init__(self, *args, **kwargs):
        super(ModernParadoxGamesPerformer, self).__init__(*args, **kwargs)
        self._default_padding = 1

    @logger.catch()
    def _create_original_language_dictionary(self, filename):
        r"""Создает словарь, состоящий из номера строки, в качестве ключа и словаря, в качестве значения
        Каждый словарь содержит пару ключ-значение: key: 'key', value: 'value'
        К применру: 11: {'key': 'AI_UNIT_TOOLTIP_UNIT_STACK_NO_ORDER:0',
                        'value': " No order."'},
        Здесь 11 - номер строки, а key - ключ(идентификатор) полной строки value.
        А также в value уже обрезаны пробелы и  символы переноса строки справа"""
        self._original_language_list = []
        self._original_language_list = ModernParadoxParser(filename=filename).parse_file(get_list=True)
        logger.info(f'List with key_value: {self._original_language_list}')
        self._translated_list = ['' for _ in range(len(self._original_language_list))]

    @logger.catch()
    def _create_game_localization_dictionary(self):
        self.info_console_value.emit(f'{LanguageConstants.localization_dict_creating_started}'
                                     f' - {self._calculate_time_delta()}\n')
        self.info_label_value.emit(LanguageConstants.game_localization_processing)
        original_vanilla_path = self._paths.get_game_path() / self._original_language
        target_vanilla_path = self._paths.get_game_path() / self._target_language
        for file in original_vanilla_path.rglob('*'):
            lines_dictionary = ModernParadoxParser(filename=file).parse_file()
            self._original_vanilla_dictionary |= lines_dictionary
        for file in target_vanilla_path.rglob('*'):
            lines_dictionary = ModernParadoxParser(filename=file).parse_file()
            self._target_vanilla_dictionary |= lines_dictionary

    @logger.catch()
    def _create_previous_version_dictionary(self):
        self.info_console_value.emit(f'{LanguageConstants.previous_localization_dict_creating_started} -'
                                     f' {self._calculate_time_delta()}\n')
        self.info_label_value.emit(LanguageConstants.previous_localization_processing)
        self._previous_version_dictionary = {"lang": "l_" + self._target_language + ":\n"}
        for file in self._paths.get_previous_files(target_language=self._target_language):
            file: Path
            self._previous_version_dictionary |= ModernParadoxParser(filename=file).parse_file()

    @logger.catch()
    def _create_translated_list(self, key_value: dict):
        if self._current_line_number == 0:
            self._translated_list[0] = "l_" + self._target_language + ":\n"
        else:
            match self._paths.get_previous_path_validate_result():
                case True:
                    self._translated_list[self._current_line_number] = " " * self._default_padding \
                                                         + self._compare_with_previous(key_value=key_value) + "\n"
                case False:
                    self._translated_list[self._current_line_number] = " " * self._default_padding \
                                                         + self._compare_with_vanilla(key_value=key_value) + "\n"

    @logger.catch()
    def _compare_with_previous(self, key_value) -> str:
        previous_line = self._previous_version_dictionary.get(key_value['key'], '')
        if not previous_line.strip():
            previous_line = None
        logger.debug(f'Key - Value: {key_value}')
        if previous_line is None:
            if not key_value['value'] in ["", None]:
                self.file_info_data.add_new_line(self._current_line_number)
            logger.debug(f'Previous is {previous_line} if line is {key_value["value"]}')
            return self._compare_with_vanilla(key_value=key_value)
        else:
            self.file_info_data.add_line_from_previous_version(self._current_line_number)
            return " ".join((key_value['key'], previous_line))

    @logger.catch()
    def _compare_with_vanilla(self, key_value: dict) -> str:
        original_vanilla_value = self._original_vanilla_dictionary.get(key_value["key"], None)
        target_vanilla_value = self._target_vanilla_dictionary.get(key_value["key"], None)
        logger.debug(f'Original value - {"found" if original_vanilla_value is not None else None}, '
                     f'Target value - {"found" if target_vanilla_value is not None else None} ')
        if original_vanilla_value is not None and target_vanilla_value is not None:
            if original_vanilla_value == key_value["value"]:
                logger.debug(f'Return vanilla value')
                self.file_info_data.add_line_from_vanilla_loc(self._current_line_number)
                return " ".join((key_value["key"], target_vanilla_value))
        if key_value["value"] in ["", None]:
            logger.debug('String is empty')
            return " ".join((key_value["key"], key_value["value"]))
        else:
            return self._translate_line(translator=self._translator, key_value=key_value)

    @logger.catch()
    def _translate_line(self, translator: TranslatorManager | None, key_value: dict) -> str:
        r"""На вход должна подаваться строка с уже обрезанным символом переноса строки"""
        if self._current_process_file in self._need_translate_list:
            translate_flag = True
            logger.debug(f'Current file is checked for translating')
        else:
            translate_flag = False
            logger.debug(f'Current file is not checked for translating')
        if translate_flag is False:
            return " ".join((key_value["key"], key_value["value"], "#NT!"))
        else:
            localization_value = key_value["value"]
            logger.debug(f'Only text from line - {localization_value}')
            if localization_value[1:-1].strip() == "":
                return " ".join((key_value["key"], key_value["value"]))
            else:
                try:
                    modified_line = self._modify_line(line=localization_value, flag="modify",
                                                      pattern=self._shielded_values)
                    translated_line = translator.translate(text=modified_line[1:-1])
                    normal_string = self._modify_line(line=translated_line, flag="return_normal_view")
                    self.file_info_data.add_translated_line(self._current_line_number)
                    self.info_data.add_translated_chars(len(modified_line[1:-1]))
                    self.file_info_data.add_api_service(translator.get_api_name())
                    if self._disable_original_line:
                        return " ".join((key_value["key"],
                                         key_value["value"].replace(localization_value, f'\"{normal_string}\"'),
                                         '#NT!'))
                    return " ".join((key_value["key"], key_value["value"], f" <\"{normal_string}\">", " #NT!"))
                except QuotaExceededException as error_text:
                    error_text = f'{LanguageConstants.error_quota_exceeded} - {error_text}'
                    logger.warning(error_text)
                    translator.set_new_api_service(api_service='GoogleTranslator',
                                                   last_source=translator.get_source_language(),
                                                   last_target=translator.get_target_language())
                    self.info_console_value.emit(f'{LanguageConstants.api_service_changed}{translator.get_api_name()}')
                    self.file_info_data.add_api_service('GoogleTranslator')
                    self.info_data.add_api_service('GoogleTranslator')
                    self.info_console_value.emit(self._change_text_style(error_text, 'red'))
                    return self._translate_line(translator=translator, key_value=key_value)
                except Exception as error:
                    self.file_info_data.add_line_with_error(self._current_line_number)
                    error_text = f"{LanguageConstants.error_with_translation}\n{key_value['value']} {key_value['value']}\n{error}\n"
                    logger.error(f'{error_text}')
                    self.info_console_value.emit(self._change_text_style(error_text, 'red'))
                    return " ".join((key_value['key'], key_value['value'], "#Translation Error!"))

    @logger.catch()
    def _process_data(self):
        r"""Здесь происходит процесс обработки файлов. Последовательное открытие, создание и запись"""
        self.info_console_value.emit(f'{LanguageConstants.start_file_processing} - {self._calculate_time_delta()}\n')
        self.info_data = InfoData(self._paths.get_target_path().name)
        for file in self._paths.get_file_hierarchy():
            start_time = time.time()

            logger.info(f'Started file {file}')
            self._current_process_file = file
            original_file_full_path = self._paths.get_original_mode_path() / file
            changed_file_full_path = self._paths.get_target_path() / str(file).replace(self._original_language,
                                                                                       self._target_language)
            self.file_info_data = FileInfoData(filename=changed_file_full_path)
            with changed_file_full_path.open(mode='w', encoding='utf-8-sig') as target_file:
                info = f"{LanguageConstants.file_opened} {file} - {self._calculate_time_delta()}\n"
                self.info_console_value.emit(info)

                self._create_original_language_dictionary(original_file_full_path)
                amount_lines = len(self._original_language_list)
                self.file_info_data.set_lines_in_files(amount_lines)
                self.info_data.add_api_service(self._translator.get_api_name())
                for line_number, key_value in enumerate(self._original_language_list):
                    self._current_line_number = line_number
                    self._create_translated_list(key_value=key_value)
                    info = f"{LanguageConstants.process_string} {line_number + 1}/{amount_lines}\n" \
                           f"{LanguageConstants.of_file} {str(original_file_full_path.name)}"
                    self.info_label_value.emit(info)
                    self.progress_bar_value.emit(original_file_full_path.stat().st_size /
                                                 amount_lines /
                                                 self._paths.get_original_files_size())
                print(*self._translated_list, file=target_file, sep='', end='')
            self.file_info_data.set_process_time(self._calculate_time_delta(start_time=start_time))
            self.info_data.add_file_info(self.file_info_data)
            self.info_data.add_translated_files()
