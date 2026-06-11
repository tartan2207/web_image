
import logging
import math
from pathlib import Path
from backend.database.image_repo import ImageRepository
from backend.utils.file_operation import FileOperation
from backend.utils.parser import  parser_params


class HandlersServer:

    def __init__(self, *args, **kwargs):
        self.__file_operation = FileOperation()
        self.__logger = logging.getLogger('web_app.handlers_server.HandlersServer')
        self.__repo = ImageRepository()

    def get_query_params(self,url: str) -> dict:
        default_genre:str = "all"
        query_params = parser_params(url)
        if query_params:
            genres=self.__repo.get_genres()
            if genres:
             query_params["genre"] = query_params["genre"] if query_params["genre"] in genres else default_genre
        return query_params


    def get_images(self,query_params:dict ) -> dict|int:
        result = {}
        error_bd = 500

        page=query_params["page"]
        limit = query_params["limit"]
        order = query_params["order"]
        genre=query_params["genre"]
        try:
                images = self.__repo.find_images_by_genre (genre=genre,page=page, limit=limit, order=order)
                if images:
                    total = self.__repo.count()
                    pages = max(1, math.ceil(total / limit))
                    result["items"] = images
                    result["pagination"] = {}
                    result["pagination"]["total"] = total
                    result["pagination"]["pages"] = pages
                    result["pagination"]["page"] = page
                    result["pagination"]["limit"] = limit
        except Exception as db_error:
            self.__logger.error(f"Database error {db_error}", exc_info=True)
            return error_bd
        else:
            if not result:
                self.__logger.error("Error: Image not found in db")
            return result

    def get_image(self,filename) -> dict | int:
        error_bd = 500
        images={}
        try:
            result = self.__repo.increment_views(filename)
            if result:
                images = self.__repo.get_image_by_filename(filename)
        except Exception as db_error:
            self.__logger.error(f"Database error {db_error}", exc_info=True)
            return error_bd
        else:
            if not images:
                self.__logger.error("Error: Image not found in db")
            return images

    def delete_image(self, filename) ->bool:
        try:
            result=self.__repo.soft_delete(filename)
        except Exception as ex:
            self.__logger.error(f"Image {filename} can not be updated: {ex}", exc_info=True)
            return False
        else:
            if result:
                self.__logger.info(f"Image {filename} was soft deleted from db")
                return True

    def purge_db(self) -> list[str]|int:
        error = 500
        try:
            result=self.__repo.purge_deleted()
        except Exception as ex:
            self.__logger.error(f"Images was purged and deleted failed: {ex}", exc_info=True)
            return error
        else:
            if result:
                self.__logger.info(f"Images was purged and deleted successfully")
            return result

    def delete_file(self, filename) -> bool:
        try:
            self.__file_operation.delete_file(filename)
        except Exception as ex:
            self.__logger.error(f"File {filename} can not be deleted from storage: {ex}", exc_info=True)
            return False
        else:
            self.__logger.info(f"File {filename} was deleted from storage successfully")
            return True

    def delete_files(self, files:list[str]) -> bool:
        try:
            self.__file_operation.delete_files(files)
        except Exception as ex:
            self.__logger.error(f"Files can not be deleted from storage: {ex}", exc_info=True)
            return False
        else:
            self.__logger.info(f"Files was deleted from storage successfully")
            return True

    def save_image(self,filename:str,original_name:str, data: bytes, genre:str)->dict|None:
        genre_id = None
        try:
            self.__file_operation.save_file_image(filename, data )
            self.__logger.info("File was saved")
        except Exception as ex:
            self.__logger.error(f"Error saving image to storage {ex}", exc_info=True)

        result = {}

        hash_256=self.__file_operation.create_file_hash(data)
        if self.__has_duplicate_hash(hash_256):
            self.__logger.error(f"Error There is duplicate_hash in db")
            self.__file_operation.delete_file(filename)
            return result

        try:
            genre_id=self.__repo.get_id_by_genre( genre)
        except Exception as ex:
            self.__logger.error(f"Error  image genre {ex}", exc_info=True)
            self.__file_operation.delete_file(filename)
            return genre_id

        try:
            image_id = self.__repo.insert_image(
                    filename=filename,
                    original_name=original_name,
                    size=len(data),
                    file_type=Path(original_name).suffix.lstrip('.'),
                    hash=hash_256,
                    genre_id=genre_id
                )
            result["id"]=image_id
            result["filename"] = filename
            result["hash"] = hash_256
            result["genre_id"]=genre_id
            result["url"] = f"/images/{filename}"
        except Exception as ex:
            self.__logger.error(f"Error insert image to db {ex}", exc_info=True)
            self.__file_operation.delete_file(filename)
        return result

    def __has_duplicate_hash(self, hash_file)->bool:
        try:
            file_hash = self.__repo.find_hash(hash_file)
        except Exception as ex:
            self.__logger.error(f"Error: Find duplicate file hash {ex}", exc_info=True)
            return True
        else:
            if file_hash:
                return True
            return False




