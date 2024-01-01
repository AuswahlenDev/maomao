from maomao import MaomaoClient
from rich.logging import RichHandler 

import logging 

if __name__ == '__main__':
    logger = logging.getLogger("disnake")
    logger.setLevel(logging.INFO)
    logger.addHandler(RichHandler(markup=True))

    client = MaomaoClient()
    client.ok()