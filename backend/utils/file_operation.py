import hashlib
import logging
import os

from backend.config import settings


class FileOperation:

    def __init__(self) -> None:
        self.__logger = logging.getLogger('web_app.file_operation.FileOperation')

    def __create_file_path(self, filename: str) -> str:
        return os.path.join(settings.images_dir, filename)

    def save_file_image(self, filename: str, data: bytes) -> None:
        try:
            os.makedirs(settings.images_dir, exist_ok=True)
            with open(self.__create_file_path(filename), "wb") as f:
                f.write(data)
        except OSError as ex:
            raise OSError("Error save file") from ex

    def delete_file(self, filename) -> None:
        full_path = self.__create_file_path(filename)
        try:
            os.remove(full_path)
        except OSError as ex:
            raise OSError("Error delete file") from ex

    def delete_files(self, files: list[str]) -> None:
        for file in files:
            full_path = self.__create_file_path(file)
            try:
                os.remove(full_path)
            except OSError as ex:
                raise OSError("Error delete files") from ex

    def create_file_hash(self, file_bytes: bytes) -> str:
        try:
            hash256 = hashlib.sha256(file_bytes).hexdigest()
        except TypeError as ex:
            pass
        else:
            return hash256
