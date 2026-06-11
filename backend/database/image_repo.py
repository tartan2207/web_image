from backend.database.db_connect import DBConnect


class ImageRepository:

    def insert_image(self, filename, original_name: str, size: int, file_type: str, hash: str, genre_id: int) -> int:
        with DBConnect.get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO images (filename,original_name, size, file_type, hash, id_genre  )
                VALUES (%s, %s, %s, %s, %s, %s )
                RETURNING id
                """,
                (filename, original_name, size, file_type, hash, genre_id)
            )
            image_id = cur.fetchone()[0]
            return image_id

    def get_image_by_filename(self, filename: str) -> dict:
        with DBConnect.get_cursor(dict_rows=True) as cur:
            cur.execute(
                """
                    SELECT id, filename, original_name, size, file_type, upload_time, views
                    FROM images
                    WHERE filename = %s 
                          AND deleted_at IS NULL 
                """,
                (filename,)
            )
            raw_row = cur.fetchone()
            result = dict(raw_row) if raw_row is not None else {}
            return result

    def find_hash(self, file_hash: str) -> tuple:
        with DBConnect.get_cursor() as cur:
            cur.execute(
                """
                    SELECT id FROM images
                    WHERE hash = %s 
                          AND deleted_at IS NULL 
                """,
                (file_hash,)
            )
            row = cur.fetchone()
            result = row if row is not None else ()
            return result

    def soft_delete(self, filename: str) -> tuple:
        with DBConnect.get_cursor() as cur:
            cur.execute(
                """
                    UPDATE images
                    set deleted_at  =  NOW()
                    WHERE filename = %s
                    RETURNING id
                """,
                (filename,)
            )
            updated_row = cur.fetchone()
            result = updated_row if updated_row is not None else ()
            return result

    def purge_deleted(self) -> list[str]:
        with DBConnect.get_cursor() as cur:
            cur.execute(
                """
                    DELETE FROM images
                    WHERE deleted_at IS NOT NULL
                    RETURNING filename
                """,
            )
            deleted_files = cur.fetchall()
            result_list = [row[0] for row in deleted_files]
            return result_list

    def count(self) -> int:
        with DBConnect.get_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM images")
            return cur.fetchone()[0]

    def get_id_by_genre(self, genre: str) -> int | None:
        with DBConnect.get_cursor() as cur:
            cur.execute(
                """
                   SELECT id
                   FROM genres
                   WHERE genre =  %s    
                """,
                (genre,)
            )
            row = cur.fetchone()
            return row[0]

    def get_genres(self) -> list[str]:
        with DBConnect.get_cursor() as cur:
            cur.execute(
                """
                   SELECT genre
                   FROM genres
                """
            )
            raw_rows = cur.fetchall()
            result_list = [row[0] for row in raw_rows]
            return result_list

    def find_images_by_genre(self, genre: str, page: int = 1, limit: int = 10, order: str = "desc") -> list[dict]:
        with DBConnect.get_cursor(dict_rows=True) as cur:
            offset = (page - 1) * limit
            order = "DESC" if order.lower() == "desc" else "ASC"
            if genre == "all":
                query = f"""
                   SELECT id, filename, original_name, size, file_type, upload_time
                   FROM images
                   WHERE deleted_at IS NULL    
                   ORDER BY upload_time {order}
                   LIMIT %s OFFSET %s"""
                cur.execute(query, (limit, offset))
            else:
                query = f"""
                    SELECT i.id, i.filename, i.original_name, i.size, i.file_type, i.upload_time
                    FROM images i
                    INNER JOIN genres g ON g.id = i.id_genre
                    WHERE deleted_at IS NULL  
                          AND g.genre= %s 
                    ORDER BY upload_time {order}
                    LIMIT %s OFFSET %s"""
                cur.execute(query, (genre, limit, offset))

            raw_rows = cur.fetchall()
            result_list = [dict(row) for row in raw_rows]
            return result_list

    def increment_views(self, filename: str) -> tuple:
        with DBConnect.get_cursor() as cur:
            cur.execute(
                """
                    UPDATE images
                    set views  =  views+1
                    WHERE filename = %s
                    RETURNING id
                """,
                (filename,)
            )
            updated_row = cur.fetchone()
            result = updated_row if updated_row is not None else ()
            return result
