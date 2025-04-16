import json
from pathlib import Path
import re
import time
from typing import KeysView

from PyQt5.QtCore import QObject, pyqtSignal
from deep_translator import GoogleTranslator
from deepl import QuotaExceededException

from info_data import InfoData, FileInfoData
from languages.language_constants import LanguageConstants

from loguru import logger

from parsers.modern_paradox_parser import ModernParadoxParser
from settings import BASE_DIR
from shielded_values import ShieldedValues
from translators.translator_manager import TranslatorManager

# Import refactored modules
from core.services.file_service import Prepper
from core.services.validation_service import Validator
from core.services.translation_service import BasePerformer, ModernParadoxGamesPerformer
from core.models.translator_account import TranslatorAccount
from config.settings_manager import Settings

# Main code that uses these classes can go here
