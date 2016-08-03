import asyncio
import cfscrape
import discord
import itertools
import json
import logging
import os.path
import re
import requests
import sys
import time

from enums import Pokemon
from snipe_bot import logger, workers
from snipe_bot.workers import ChannelManagement
from multiprocessing.dummy import Pool as ThreadPool

class SnipeBot(object):

    def __init__(self, client, config):
        # config logging
        logging.basicConfig(filename='messages.log', level=logging.WARNING)

        self.client = client
        self.config = config
        self.session = self.init_session()

    def init_session(self):
        session = requests.session()
        user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
        headers = {
            "User-Agent": user_agent,
            'Cache-Control': 'max-age=0, private, must-revalidate'
        }
        session.headers.update(headers)

        return session

    def run_worker(self, name):
        class_ = getattr(workers, name)
        worker = class_(self, self.config)
        worker.run()

    def on_message(self, message):
        worker = ChannelManagement(self, self.config)

        return worker.need_to_delete(message)
            
        