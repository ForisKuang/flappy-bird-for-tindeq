import asyncio

from tindeq_progressor.progressor_client import ProgressorClient
from settings.settings import Settings


class GameClient:

    def __init__(self, settings):

async def connect(client):
    tindeq = ProgressorClient(client)
    try:
        await tindeq.connect()
    except Exception as err:
        client.doc.add_next_tick_callback(lambda: client.btn.update(label="Connect Failed"))
        print("Connection Failed ... check tindeq and restart app")
    else:
        client.tindeq = tindeq
        await client.tindeq.soft_tare()
        await asyncio.sleep(5)

if __name__ == '__main__':
    settings = Settings()
    user_settings = settings.get_settings()

