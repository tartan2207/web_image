from http.server import HTTPServer
from backend.hendlers.image_server import ImageAPIServer
from backend.utils.host_logger import HostLogger

if __name__ == "__main__":
    host_logger = HostLogger('web_app')
    logger = host_logger.create_logger('web_app')
    server = HTTPServer(("0.0.0.0", 8000), ImageAPIServer)
    try:
        print("Server is run...")
        logger.info("Server is run...")
        server.serve_forever()
    except Exception as e:
        logger.error("Server failed")
