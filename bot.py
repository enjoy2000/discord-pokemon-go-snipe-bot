#
# Python chat bot for discord - Pokemon Go Snipe Channel
# Author: enjoy2000 | enjoy3013@gmail.com
#

import asyncio
import cfscrape
import discord
import json
import logging
import os.path
import re
import requests
import sys
import time

from enums import Pokemon
from bot import logger
from urllib.request import Request, urlopen

client = discord.Client()

# config logging
logging.basicConfig(filename='messages.log', level=logging.WARNING)

config = {}
with open('config.json') as output:
    # Load json to config object
    config = json.load(output)

api_key = config.get('api_key', 'NA')
channels = config.get('channels', [])
except_roles = config.get('except_roles', [])
user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
# header with fake user_agrent & no cache
headers = {
    "User-Agent": user_agent,
    'Cache-Control': 'max-age=0, private, must-revalidate'
}

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def is_blacklisted(message_content):
    """ Check if there is blacklisted word in message or not """

    blacklist = config.get('blacklist', [])

    # If blacklist is empty dont use black list
    if len(blacklist) == 0:
        return False

    for word in blacklist:
        if word in message_content:
            return True

global session

def init_session():
    global session
    """ start sessions to keep session/cookies """
    session = requests.session()
    session.headers.update(headers)


def _get_trackemon_session():
    global session
    init_session()

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
        logger.log('Can\'t retrieve session id for api. Waiting for next scrawl..')
        # init session again
        init_session()
        return None

    obj = lambda: None
    obj.session = session
    obj.session_id = session_id

    return obj    


def scrawl_trackemon(pokemon_name, session_data):
    """ Scrawl api from trackemon.com """

    session = session_data.session
    session_id = session_data.session_id
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
        logger.log('There is no {}'.format(pokemon_name))
    else:
        logger.log('There are {} {}(s)'.format(len(data), pokemon_name), 'blue')    

    message = ''
    for pokemon in data:
        expire_seconds = int(pokemon['expirationTime']) - time.time()
        # format message
        message += '`{}` {},{} - Expires in: {:.0f} seconds \n'.format(
            _get_pokemon_name(pokemon['pokedexTypeId']),
            pokemon['latitude'],
            pokemon['longitude'],
            expire_seconds
        )  

    return message


def _get_pokemon_name(pokemon_id):
    pokemon_id = int(pokemon_id)
    for pokemon in Pokemon:
        if pokemon.value == pokemon_id:
            return pokemon.name.lower().replace('_', '').capitalize()

    return 'NA'


if api_key == 'NA':
    raise Exception('Please specify your api key!')


@client.event
async def on_ready():

    logger.log('Logged in as')
    logger.log(client.user.name)
    logger.log(client.user.id)
    logger.log('------')

#
# python3 bot.py scrawl
#
if len(sys.argv) > 1 and sys.argv[1] == 'scrawl':

    async def get_rare_pokemons():
        """ Worker to get rare pokemons from http://pokesnipers.com/api/v1/pokemon.json """

        await client.wait_until_ready()

        # get arrays channels id need to post
        shout_out_channels = []
        for server in client.servers:
            for channel in server.channels:
                if channel.name in config.get('scrawl_channels', []):
                    shout_out_channels.append(discord.Object(channel.id))

        if len(shout_out_channels) == 0:
            raise Exception("No channel to shout out!")

        while not client.is_closed:

            logger.log('Scrawling PokeSnipers..', 'green')

            # Use scraper to bypass cloudflare ddos protection
            scraper = cfscrape.create_scraper()
            json_string = scraper.get('http://pokesnipers.com/api/v1/pokemon.json', headers=headers).content

            data = json.loads(json_string.decode('utf-8'))

            message = ''
            for pokemon in data.get('results'):
                message += "`{}` {}\n".format(pokemon.get('name'),
                                              pokemon.get('coords'))

            for channel in shout_out_channels:
                await client.send_message(channel, message)

            await asyncio.sleep(config.get('delay_scrawl', 300))

    # Loop task
    client.loop.create_task(get_rare_pokemons())

elif len(sys.argv) > 1 and sys.argv[1] == 'trackemon':
    #
    # crawl trackemon
    #
    if config.get('scrawl_trackemon') and config.get('scrawl_trackemon')['enabled']:
        async def scrawl_trackemon_worker():

            await client.wait_until_ready()

            # get arrays channels id need to post
            shout_out_channels = []
            for server in client.servers:
                for channel in server.channels:
                    if channel.name in config.get('scrawl_channels', []):
                        shout_out_channels.append(discord.Object(channel.id))

            if len(shout_out_channels) == 0:
                raise Exception("No channel to shout out!")

            while not client.is_closed:
                logger.log('Scrawling Trackemon..', 'green')

                # get trackemon session
                session_data = _get_trackemon_session()

                if not session_data:
                    logger.log('no session data')
                    client.loop.call_soon()

                if 'pokemons' in config.get('scrawl_trackemon'):
                    pokemon_names = config.get('scrawl_trackemon')['pokemons']
                    for pokemon_name in pokemon_names:
                        message = scrawl_trackemon(pokemon_name, session_data)
                        
                        if len(message):
                            for channel in shout_out_channels:
                                await client.send_message(channel, message)

                await asyncio.sleep(config.get('delay_scrawl', 300))  # increase delay to finish task

        # Loop task
        client.loop.create_task(scrawl_trackemon_worker())

else:
    @client.event
    async def on_message(message):
        """
        Event loop on every message receive
        """
        # Do nothing if bot is sending message
        if message.author == client.user:
            return None

        """
        Ignore if message from except roles
        """
        for role in message.author.roles:
            if role.name in except_roles:
                return None

        """
        Check if message contains lat/long & pokemon name
        """
        pattern = "^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)(?=.*(Bulbasaur|bulbasaur|Ivysaur|ivysaur|Venusaur|venusaur|Charmander|charmander|Charmeleon|charmeleon|Charizard|charizard|Squirtle|squirtle|Wartortle|wartortle|Blastoise|blastoise|Caterpie|caterpie|Metapod|metapod|Butterfree|butterfree|Weedle|weedle|Kakuna|kakuna|Beedrill|beedrill|Pidgey|pidgey|Pidgeotto|pidgeotto|Pidgeot|pidgeot|Rattata|rattata|Raticate|raticate|Spearow|spearow|Fearow|fearow|Ekans|ekans|Arbok|arbok|Pikachu|pikachu|Raichu|raichu|Sandshrew|sandshrew|Sandslash|sandslash|Nidoran F|nidoran f|Nidorina|nidorina|Nidoqueen|nidoqueen|Nidoran M|nidoran m|Nidorino|nidorino|Nidoking|nidoking|Clefairy|clefairy|Clefable|clefable|Vulpix|vulpix|Ninetales|ninetales|Jigglypuff|jigglypuff|Wigglytuff|wigglytuff|Zubat|zubat|Golbat|golbat|Oddish|oddish|Gloom|gloom|Vileplume|vileplume|Paras|paras|Parasect|parasect|Venonat|venonat|Venomoth|venomoth|Diglett|diglett|Dugtrio|dugtrio|Meowth|meowth|Persian|persian|Psyduck|psyduck|Golduck|golduck|Mankey|mankey|Primeape|primeape|Growlithe|growlithe|Arcanine|arcanine|Poliwag|poliwag|Poliwhirl|poliwhirl|Poliwrath|poliwrath|Abra|abra|Kadabra|kadabra|Alakazam|alakazam|Machop|machop|Machoke|machoke|Machamp|machamp|Bellsprout|bellsprout|Weepinbell|weepinbell|Victreebel|victreebel|Tentacool|tentacool|Tentacruel|tentacruel|Geodude|geodude|Graveler|graveler|Golem|golem|Ponyta|ponyta|Rapidash|rapidash|Slowpoke|slowpoke|Slowbro|slowbro|Magnemite|magnemite|Magneton|magneton|Farfetchd|farfetchd|Doduo|doduo|Dodrio|dodrio|Seel|seel|Dewgong|dewgong|Grimer|grimer|Muk|muk|Shellder|shellder|Cloyster|cloyster|Gastly|gastly|Haunter|haunter|Gengar|gengar|Onix|onix|Drowzee|drowzee|Hypno|hypno|Krabby|krabby|Kingler|kingler|Voltorb|voltorb|Electrode|electrode|Exeggcute|exeggcute|Exeggutor|exeggutor|Cubone|cubone|Marowak|marowak|Hitmonlee|hitmonlee|Hitmonchan|hitmonchan|Lickitung|lickitung|Koffing|koffing|Weezing|weezing|Rhyhorn|rhyhorn|Rhydon|rhydon|Chansey|chansey|Tangela|tangela|Kangaskhan|kangaskhan|Horsea|horsea|Seadra|seadra|Goldeen|goldeen|Seaking|seaking|Staryu|staryu|Starmie|starmie|MrMime|mrmime|Scyther|scyther|Jynx|jynx|Electabuzz|electabuzz|Magmar|magmar|Pinsir|pinsir|Tauros|tauros|Magikarp|magikarp|Gyarados|gyarados|Lapras|lapras|Ditto|ditto|Eevee|eevee|Vaporeon|vaporeon|Jolteon|jolteon|Flareon|flareon|Porygon|porygon|Omanyte|omanyte|Omastar|omastar|Kabuto|kabuto|Kabutops|kabutops|Aerodactyl|aerodactyl|Snorlax|snorlax|Articuno|articuno|Zapdos|zapdos|Moltres|moltres|Dratini|dratini|Dragonair|dragonair|Dragonite|dragonite|Mewtwo|mewtwo|Mew|mew)).*$"
        reverse_pattern = "^(Bulbasaur|bulbasaur|Ivysaur|ivysaur|Venusaur|venusaur|Charmander|charmander|Charmeleon|charmeleon|Charizard|charizard|Squirtle|squirtle|Wartortle|wartortle|Blastoise|blastoise|Caterpie|caterpie|Metapod|metapod|Butterfree|butterfree|Weedle|weedle|Kakuna|kakuna|Beedrill|beedrill|Pidgey|pidgey|Pidgeotto|pidgeotto|Pidgeot|pidgeot|Rattata|rattata|Raticate|raticate|Spearow|spearow|Fearow|fearow|Ekans|ekans|Arbok|arbok|Pikachu|pikachu|Raichu|raichu|Sandshrew|sandshrew|Sandslash|sandslash|Nidoran F|nidoran f|Nidorina|nidorina|Nidoqueen|nidoqueen|Nidoran M|nidoran m|Nidorino|nidorino|Nidoking|nidoking|Clefairy|clefairy|Clefable|clefable|Vulpix|vulpix|Ninetales|ninetales|Jigglypuff|jigglypuff|Wigglytuff|wigglytuff|Zubat|zubat|Golbat|golbat|Oddish|oddish|Gloom|gloom|Vileplume|vileplume|Paras|paras|Parasect|parasect|Venonat|venonat|Venomoth|venomoth|Diglett|diglett|Dugtrio|dugtrio|Meowth|meowth|Persian|persian|Psyduck|psyduck|Golduck|golduck|Mankey|mankey|Primeape|primeape|Growlithe|growlithe|Arcanine|arcanine|Poliwag|poliwag|Poliwhirl|poliwhirl|Poliwrath|poliwrath|Abra|abra|Kadabra|kadabra|Alakazam|alakazam|Machop|machop|Machoke|machoke|Machamp|machamp|Bellsprout|bellsprout|Weepinbell|weepinbell|Victreebel|victreebel|Tentacool|tentacool|Tentacruel|tentacruel|Geodude|geodude|Graveler|graveler|Golem|golem|Ponyta|ponyta|Rapidash|rapidash|Slowpoke|slowpoke|Slowbro|slowbro|Magnemite|magnemite|Magneton|magneton|Farfetchd|farfetchd|Doduo|doduo|Dodrio|dodrio|Seel|seel|Dewgong|dewgong|Grimer|grimer|Muk|muk|Shellder|shellder|Cloyster|cloyster|Gastly|gastly|Haunter|haunter|Gengar|gengar|Onix|onix|Drowzee|drowzee|Hypno|hypno|Krabby|krabby|Kingler|kingler|Voltorb|voltorb|Electrode|electrode|Exeggcute|exeggcute|Exeggutor|exeggutor|Cubone|cubone|Marowak|marowak|Hitmonlee|hitmonlee|Hitmonchan|hitmonchan|Lickitung|lickitung|Koffing|koffing|Weezing|weezing|Rhyhorn|rhyhorn|Rhydon|rhydon|Chansey|chansey|Tangela|tangela|Kangaskhan|kangaskhan|Horsea|horsea|Seadra|seadra|Goldeen|goldeen|Seaking|seaking|Staryu|staryu|Starmie|starmie|MrMime|mrmime|Scyther|scyther|Jynx|jynx|Electabuzz|electabuzz|Magmar|magmar|Pinsir|pinsir|Tauros|tauros|Magikarp|magikarp|Gyarados|gyarados|Lapras|lapras|Ditto|ditto|Eevee|eevee|Vaporeon|vaporeon|Jolteon|jolteon|Flareon|flareon|Porygon|porygon|Omanyte|omanyte|Omastar|omastar|Kabuto|kabuto|Kabutops|kabutops|Aerodactyl|aerodactyl|Snorlax|snorlax|Articuno|articuno|Zapdos|zapdos|Moltres|moltres|Dratini|dratini|Dragonair|dragonair|Dragonite|dragonite|Mewtwo|mewtwo|Mew|mew)(?=.*(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)).*$"

        # Manage channel rare_spottings only
        if message.channel.name in channels:
            if not (re.match(pattern, message.content) or re.match(reverse_pattern, message.content)) or is_blacklisted(message.content):
                # Log & print out
                log_message = 'Message has been deleted: {} - Author: {}'.format(
                    message.content, message.author.name)
                logger.log(log_message)
                logging.warning(log_message)

                # Delete message if not contain lat/long
                await client.delete_message(message)

    #
    # Announcement
    #
    logger.log(config.get('announcement'))
    if config.get('announcement', None):
        async def announcement():
            logger.log('Posting announcements..')

            announcement = config.get('announcement')
            message = announcement.get('message', None)
            delay = announcement.get('delay', 300)

            if not message:
                logger.log('Please config your announcement message', 'red')
                return

            await client.wait_until_ready()

            # get arrays channels id need to post
            announcement_channels = []
            for server in client.servers:
                for channel in server.channels:
                    if channel.name in channels:
                        announcement_channels.append(
                            discord.Object(channel.id))

            while not client.is_closed:
                for channel in announcement_channels:
                    await client.send_message(channel, message)

                await asyncio.sleep(delay)

        # Loop task
        client.loop.create_task(announcement())


# Start client
client.run(api_key)
