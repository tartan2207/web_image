import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.config import settings


class HostLogger:
    def __init__(self, name_modul: str):
        self.__logger = logging.getLogger(name_modul)

    def create_logger(self):
        if not self.__logger.handlers:
            self.__logger.setLevel(logging.INFO)
            self.__logger.addHandler(self.__get_file_handler())
            self.__logger.addHandler(self.__get_stream_handler())
        return self.__logger

    def _create_log_file(self) -> Path:
        logs_dir = Path(settings.logs_dir)
        logs_dir.mkdir(exist_ok=True, parents=True)
        return logs_dir / "app.log"

    def __get_file_handler(self):
        log_file = self._create_log_file()
        file_handler = RotatingFileHandler(
            filename=log_file,
            encoding="utf-8",
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s"))
        return file_handler

    def __get_stream_handler(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s"))
        return stream_handler
