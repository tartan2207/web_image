import enum
import logging
from pathlib import Path

from backend.config import settings
from backend.utils.parser import get_path


class ErrorStatus(enum.IntEnum):
    invalid_file_type = 1
    invalid_file_size = 2
    no_file_provided = 3


logger = logging.getLogger('web_app.backend.utils.validators')

def is_validated_extension(original_filename: str) -> bool:
    ext = Path(original_filename).suffix.lstrip('.')
    return ext in settings.allowed_file_types


def is_validated_size(size_bytes: int) -> bool:
    return size_bytes <= settings.max_file_size_mb * 1024 * 1024

def get_check_file(file_item)->str|int:
        if hasattr(file_item, "filename") and file_item.filename:
            # Здесь мы уверены, что это полноценный cgi.FieldStorage с файлом внутри
            original_name: str = file_item.filename
            data: bytes = file_item.file.read()
            if not is_validated_extension(original_name):
                logger.error(f"Invalid file type. Allowed: {settings.allowed_file_types}")
                return ErrorStatus.invalid_file_type

            if not is_validated_size(len(data)):
                logger.error(f"File too large. Max: {settings.max_file_size_mb} MB")
                return ErrorStatus.invalid_file_size
            return original_name
        else:
            logger.error(f"File was not provided.")
            return ErrorStatus.no_file_provided

def is_validated_path_parent(url:str)->bool:
        # parsed_url = urlparse(url)
        if str(get_path(url))==settings.image_path or str(get_path(url).parent)==settings.image_path:
            return True
        elif str(get_path(url))==settings.upload_path:
            return True
        elif str(get_path(url))==settings.trash_path:
            return True
        else:
            logger.info(f"Url is not valid")
            return False


