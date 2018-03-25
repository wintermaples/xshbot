from xshbot import APIConnector
import threading
import datetime
import time
import asyncio

class FullMoonParty():

    def __init__(self, client):
        self.rain_event_start_thread = RainEventStartScheduler()
        self.rain_event_start_thread.start()
        self.rain_event_thread = RainEventScheduler()
        client.loop.create_task(self.rain_event_thread.task(client))

class RainEventStartScheduler(threading.Thread):
    def __init__(self):
        super(RainEventStartScheduler, self).__init__()
        self.start_date_time = datetime.datetime(2018, 3, 31, 22, 0, 0)

    def run(self):
        while True:
            if datetime.datetime.now() > self.start_date_time:
                self.rain()
                break
            time.sleep(1)

    def rain(self):
        wallet_list = APIConnector.list('')
        balance_0_wallet_list = [wallet for wallet in wallet_list if wallet['balance'] == 0]
        for wallet in balance_0_wallet_list:
            APIConnector.tip('', 'RAIN_WALLET', wallet['name'], 1, 0)


class RainEventScheduler():
    def __init__(self):
        self.start_date_time = datetime.datetime(2018, 3, 31, 22, 0, 20)
        self.excluded_users = set()

    async def task(self, client):
        await client.wait_until_ready()
        while not client.is_closed:
            if datetime.datetime.now() > self.start_date_time:
                wallets = APIConnector.list('')
                newUserWallets = [wallet for wallet in wallets if
                                  not wallet['name'] in self.excluded_users and wallet['balance'] < 0.001]
                for newUserWallet in newUserWallets:
                    APIConnector.tip('', 'RAIN_WALLET', newUserWallet['name'], 1, 0)
                for wallet in wallets:
                    self.excluded_users.add(wallet['name'])

            await asyncio.sleep(60)