import asyncio
import datetime
import discord
import cfscrape
import json
import logging
import time

from snipe_bot.workers import BaseWorker
from snipe_bot import logger


class PokeSnipers(BaseWorker):

    def initialize(self):
        pass

    def run(self):
        self.client.loop.create_task(self.scrawl())

    async def scrawl(self):
        await self.client.wait_until_ready()

        # get arrays channels id need to post
        shout_out_channels = []
        for server in self.client.servers:
            for channel in server.channels:
                if channel.name in self.config.get('scrawl_channels', []):
                    shout_out_channels.append(discord.Object(channel.id))

        if len(shout_out_channels) == 0:
            raise Exception("No channel to shout out!")

        while not self.client.is_closed:

            logger.log('Scrawling PokeSnipers..', 'green')

            # Use scraper to bypass cloudflare ddos protection
            scraper = cfscrape.create_scraper()
            json_string = scraper.get(
                'http://pokesnipers.com/api/v1/pokemon.json').content

            data = json.loads(json_string.decode('utf-8'))

            logger.log('Got {} pokemons from PokeSnipers'.format(
                len(data.get('results'))), 'blue')
            message = ''
            for pokemon in data.get('results'):
                until = time.mktime(time.strptime(pokemon.get('until'), '%Y-%m-%dT%H:%M:%S.%fZ'))
                # use utc timezone for pokesnipers
                expire_seconds = until - datetime.datetime.utcnow().timestamp()
                message += "`{}` {} - Expires in: {:.0f} seconds\n".format(pokemon.get('name'), pokemon.get('coords'), expire_seconds)

            if len(message):
                for channel in shout_out_channels:
                    await self.client.send_message(channel, message)

            await asyncio.sleep(self.config.get('delay_scrawl', 300))
