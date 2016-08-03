import asyncio
import discord
import itertools
import json
import logging
import re
import time

from multiprocessing.dummy import Pool as ThreadPool
from snipe_bot.workers import BaseWorker
from snipe_bot import logger
from snipe_bot.enums import Pokemon


class Trackemon(BaseWorker):

    def initialize(self):
        self.session_id = None

    def run(self):
        self.client.loop.create_task(self.scrawl())

    async def scrawl(self, threads=5):

        logger.log('Scrawling Trackemon..', 'green')
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
            logger.log('Scrawling Trackemon..', 'green')

            if not self.session_id:
                # get trackemon session
                session_id = self._get_trackemon_session()

                if not session_id:
                    logger.log(
                        'Cannot retrieve session id for Trackemon', 'red')
                    return
                else:
                    self.session_id = session_id

            # use multiprocessing
            if 'pokemons' in self.config.get('scrawl_trackemon'):
                pokemon_names = self.config.get('scrawl_trackemon')['pokemons']

                pool = ThreadPool(threads)
                messages = pool.starmap(self.scrawl_trackemon, zip(
                    pokemon_names, itertools.repeat(self.session_id)))

                for message in messages:
                    if len(message):
                        for channel in shout_out_channels:
                            await self.client.send_message(channel, message)

            # increase delay to finish task
            await asyncio.sleep(self.config.get('delay_scrawl', 300))

    def _get_trackemon_session(self):
        session = self.bot.session
        # get session_id by fetching root
        first_response = session.get('http://www.trackemon.com/')

        pattern = re.compile(r'sessionId\s=\s\'\w+\'')
        session_id_string = re.search(
            pattern, first_response.content.decode('utf-8'))
        if session_id_string:
            # Found string, split session id
            session_id = session_id_string.group().replace(
                'sessionId = ', '').replace('\'', '')
        else:
            logger.log(
                'Can\'t retrieve session id for api. Waiting for next scrawl..')
            # init session again
            return None

        return session_id

    def scrawl_trackemon(self, pokemon_name, session_id):
        """ Scrawl api from trackemon.com """

        session = self.bot.session
        api_root = 'http://www.trackemon.com/'

        # get pokemon id
        try:
            pokemon_id = getattr(Pokemon, pokemon_name.upper()).value

        except AttributeError:
            logger.log('Wrong pokemon name', 'red')
            sys.exit()

        api_endpoint = '{}fetch/rare?pokedexTypeId={}&sessionId={}'

        endpoint = api_endpoint.format(api_root, pokemon_id, session_id)
        logger.log(endpoint)
        try:
            response = session.get(endpoint)

            data = response.json()
        except:
            logger.log('Api is busy')
            return ''

        if not data:
            logger.log('There is no {}'.format(pokemon_name), 'yellow')
        else:
            logger.log('There are {} {}(s)'.format(
                len(data), pokemon_name), 'blue')

        message = ''
        for pokemon in data:
            expire_seconds = int(pokemon['expirationTime']) - time.time()
            # format message
            message += '`{}` {},{} - Expires in: {:.0f} seconds \n'.format(
                self._get_pokemon_name(pokemon['pokedexTypeId']),
                pokemon['latitude'],
                pokemon['longitude'],
                expire_seconds
            )

        return message

    def _get_pokemon_name(self, pokemon_id):
        pokemon_id = int(pokemon_id)
        for pokemon in Pokemon:
            if pokemon.value == pokemon_id:
                return pokemon.name.lower().replace('_', '').capitalize()

        return 'NA'
