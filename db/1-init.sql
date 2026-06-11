CREATE TABLE public.genres (
    id SERIAL PRIMARY KEY,
    genre TEXT NOT NULL

);


CREATE TABLE public.images (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    original_name TEXT NOT NULL,
	id_genre int NOT NULL,
    size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
	upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	deleted_at TIMESTAMP NULL,
	hash TEXT NOT NULL UNIQUE,
    views int DEFAULT 0,
	 CONSTRAINT fk_genres
      FOREIGN KEY(id_genre)
        REFERENCES genres(id)
		ON DELETE CASCADE
);


INSERT INTO public.genres(genre)
VALUES('animal'),
       ('nature'),
	   ('people'),
	   ('abstract'),
	   ('space')