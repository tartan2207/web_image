import logging
from pathlib import PurePosixPath
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger('web_app.backend.utils.parser')

def get_path(url: str) -> PurePosixPath:
    parsed_url = urlparse(url)
    return PurePosixPath(parsed_url.path)


def get_path_filename(url: str) -> str:
    parsed_url = urlparse(url)
    return PurePosixPath(parsed_url.path).name


def parser_params(url: str) -> dict:
    default_limit: int = 10
    default_page: int = 1
    default_order: str = "desc"
    query_params = {}

    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    try:
        query_params['page'] = int(params['page'][0]) if params['page'][0].isdigit() else default_page
        query_params['limit'] = int(params['limit'][0]) if params['limit'][0].isdigit() else default_limit
        query_params['order'] = params['order'][0].lower() if (params['order'][0].lower() == "asc"
                                                               or params['order'][
                                                                   0].lower() == "desc") else default_order
        query_params['genre'] = params['genre'][0].lower()
    except KeyError as ex:
        logger.error(f"Error query params: {ex}")
    return query_params
