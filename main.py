# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from tindeq_progressor.progressor_client import ProgressorClient

class FlappyBirdClient:

    def __init__(self):


async def connect(cft):
    tindeq = ProgressorClient(cft)
    try:
        await tindeq.connect()
    except Exception as err:
        cft.doc.add_next_tick_callback(lambda: cft.btn.update(label="Connect Failed"))
        print("Connection Failed ... check tindeq and restart app")
    else:
        cft.tindeq = tindeq
        await cft.tindeq.soft_tare()
        await asyncio.sleep(5)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
