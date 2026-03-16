import logging
import os
import socket
import uvicorn

from src.app import app
from src.config import settings

logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(name)s: %(message)s",
    level=logging.INFO
)
_logger = logging.getLogger(__name__)
RUNTIME_PORT_FILE = "/tmp/chatgpt-tarot-divination.port"

_logger.info(f"settings: {settings.model_dump_json(indent=2)}")


def _find_available_port(host: str, preferred_port: int, max_attempts: int = 50) -> int:
    for port in range(preferred_port, preferred_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex((host, port)) != 0:
                return port
    return preferred_port


if __name__ == "__main__":
    bind_host = settings.host
    preferred_port = int(settings.port)
    probe_host = "127.0.0.1" if bind_host == "0.0.0.0" else bind_host
    bind_port = _find_available_port(probe_host, preferred_port)
    if bind_port != preferred_port:
        _logger.warning(
            "Preferred port %s is occupied. Fallback to %s.",
            preferred_port,
            bind_port
        )
    os.environ["CHATGPT_TAROT_RUNTIME_PORT"] = str(bind_port)
    with open(RUNTIME_PORT_FILE, "w", encoding="utf-8") as f:
        f.write(str(bind_port))
    _logger.info("Runtime port: %s", bind_port)
    uvicorn.run(app, host=bind_host, port=bind_port)
