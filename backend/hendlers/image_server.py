import cgi
import logging
import uuid
from pathlib import Path

from backend.config import settings
from backend.hendlers.base_handlers import BaseHandler
from backend.hendlers.handlers_server import HandlersServer
from backend.utils.parser import get_path_filename, get_path
from backend.utils.validators import get_check_file, ErrorStatus, is_validated_path_parent


class ImageAPIServer(BaseHandler):
    def __init__(self, *args, **kwargs):
        self.__handlers = HandlersServer()
        self.__logger = logging.getLogger('web_app.image_server.ImageAPIServer')
        super().__init__(*args, **kwargs)


    def do_GET(self):
        self.__logger.info(f"Received GET request for {self.path}")
        result = None

        if not is_validated_path_parent(self.path):
            self._send_error(404, "Page not found")
            return

        if str(get_path(self.path)) == settings.image_path:
            params = self.__handlers.get_query_params(self.path)
            if not params:
                self._send_error(400, "Bad Request")
                return
            result = self.__handlers.get_images(params)

        if str(get_path(self.path).parent) == settings.image_path:
            filename = get_path_filename(self.path)
            result = self.__handlers.get_image(filename)
        if result == 500:
            self._send_error(500, " Internal Server Error")
            return
        elif not result:
            self._send_error(404, "Image not found")
            return
        elif result:
            self._send_json(200, result)


    def do_POST(self):
        self.__logger.info(f"Received POST request for {self.path}")
        if not is_validated_path_parent(self.path):
            self._send_error(404, "Page not found")
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send_error(400, "Expected multipart/form-data")
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST"},
        )
        if "genre" in form:
            genre = form["genre"].value
        else:
            self._send_error(400, "Please select an image genre")
            return
        if "file" not in form:
            self._send_error(400, "No file provided")
            return

        file_item = form["file"]
        file_item.file.seek(0)
        file_bytes = file_item.file.read()

        filename = None
        result = get_check_file(file_item)
        if type(result) is str:
            ext = Path(result).suffix.lstrip('.')
            filename = f"{uuid.uuid4()}.{ext}"
        else:
            if result == ErrorStatus.invalid_file_type:
                self._send_error(400, f"Invalid file type. Allowed: {settings.allowed_file_types}")
                return
            elif result == ErrorStatus.invalid_file_size:
                self._send_error(413, f"File too large. Max: {settings.max_file_size_mb} MB")
                return
            elif result == ErrorStatus.no_file_provided:
                self._send_error(400, "No file provided")
                return

        result = self.__handlers.save_image(filename, file_item.filename, file_bytes, genre)
        if not result or result is None:
            self._send_error(500, "Internal Server Error")
            return
        self._send_json(200, result)


    def do_DELETE(self):
        self.__logger.info(f"Received DELETE request for {self.path}")

        if not is_validated_path_parent(self.path):
            self._send_error(404, "Page not found")
            return

        if str(get_path(self.path).parent) == settings.image_path:
            filename = get_path_filename(self.path)
            if not self.__handlers.delete_image(filename):
                self._send_error(500, "Internal Server Error")
                return

        elif str(get_path(self.path)) == settings.trash_path:
            result = self.__handlers.purge_db()
            if result:
                if not self.__handlers.delete_files(result):
                    self._send_error(500, "Internal Server Error")
                    return
            elif result==500:
                self._send_error(500, "Internal Server Error")
                return

        self._send_json(200, {})

