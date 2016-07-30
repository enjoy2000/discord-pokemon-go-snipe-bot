#
# Python chat bot for discord - Pokemon Go Snipe Channel
# Author: enjoy2000 | enjoy3013@gmail.com
#

import asyncio
import discord
import json
import logging
import re

from urllib.request import Request, urlopen

client = discord.Client()

# config logging
logging.basicConfig(filename = 'messages.log', level = logging.WARNING)

config = {}
with open('config.json') as output:
    # Load json to config object
    config = json.load(output)

api_key = config.get('api_key', 'NA')
channels = config.get('channels', [])
except_roles = config.get('except_roles', [])
"""
Worker to get rare pokemon from http://pokesnipers.com/api/v1/pokemon.json
"""
async def get_rare_pokemons():
    await client.wait_until_ready()

    # get arrays channels id need to shou
    shout_out_channels = []
    for server in client.servers:
        for channel in server.channels:
            if channel.name in config.get('scrawl_channels', []):
                shout_out_channels.append(discord.Object(channel.id))

    if len(shout_out_channels) == 0:
        raise Exception("No channel to shout out!")
        

    while not client.is_closed:

        print('Scrawling..')

        req = Request(
            'http://pokesnipers.com/api/v1/pokemon.json',
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Cache-Control': 'max-age=0, private, must-revalidate'
            }
        )
        json_string = urlopen(req).read()
        data = json.loads(json_string.decode('utf-8'))

        message =  ''
        for pokemon in data.get('results'):
            message += pokemon.get('coords') + ' ' + pokemon.get('name') + "\r\n"

        for channel in shout_out_channels:
            await client.send_message(channel, message)
        await asyncio.sleep(config.get('delay_scrawl', 300)) # task runs every 60 seconds

@client.event
async def on_ready():
    if api_key == 'NA':
        raise Exception('Please specify your api key!')

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
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
    # Message has to be formatted: `Lat/Long Pokemon IV
    partern = "^(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)(?=.*(Bulbasaur|bulbasaur|Ivysaur|ivysaur|Venusaur|venusaur|Charmander|charmander|Charmeleon|charmeleon|Charizard|charizard|Squirtle|squirtle|Wartortle|wartortle|Blastoise|blastoise|Caterpie|caterpie|Metapod|metapod|Butterfree|butterfree|Weedle|weedle|Kakuna|kakuna|Beedrill|beedrill|Pidgey|pidgey|Pidgeotto|pidgeotto|Pidgeot|pidgeot|Rattata|rattata|Raticate|raticate|Spearow|spearow|Fearow|fearow|Ekans|ekans|Arbok|arbok|Pikachu|pikachu|Raichu|raichu|Sandshrew|sandshrew|Sandslash|sandslash|Nidoran F|nidoran f|Nidorina|nidorina|Nidoqueen|nidoqueen|Nidoran M|nidoran m|Nidorino|nidorino|Nidoking|nidoking|Clefairy|clefairy|Clefable|clefable|Vulpix|vulpix|Ninetales|ninetales|Jigglypuff|jigglypuff|Wigglytuff|wigglytuff|Zubat|zubat|Golbat|golbat|Oddish|oddish|Gloom|gloom|Vileplume|vileplume|Paras|paras|Parasect|parasect|Venonat|venonat|Venomoth|venomoth|Diglett|diglett|Dugtrio|dugtrio|Meowth|meowth|Persian|persian|Psyduck|psyduck|Golduck|golduck|Mankey|mankey|Primeape|primeape|Growlithe|growlithe|Arcanine|arcanine|Poliwag|poliwag|Poliwhirl|poliwhirl|Poliwrath|poliwrath|Abra|abra|Kadabra|kadabra|Alakazam|alakazam|Machop|machop|Machoke|machoke|Machamp|machamp|Bellsprout|bellsprout|Weepinbell|weepinbell|Victreebel|victreebel|Tentacool|tentacool|Tentacruel|tentacruel|Geodude|geodude|Graveler|graveler|Golem|golem|Ponyta|ponyta|Rapidash|rapidash|Slowpoke|slowpoke|Slowbro|slowbro|Magnemite|magnemite|Magneton|magneton|Farfetchd|farfetchd|Doduo|doduo|Dodrio|dodrio|Seel|seel|Dewgong|dewgong|Grimer|grimer|Muk|muk|Shellder|shellder|Cloyster|cloyster|Gastly|gastly|Haunter|haunter|Gengar|gengar|Onix|onix|Drowzee|drowzee|Hypno|hypno|Krabby|krabby|Kingler|kingler|Voltorb|voltorb|Electrode|electrode|Exeggcute|exeggcute|Exeggutor|exeggutor|Cubone|cubone|Marowak|marowak|Hitmonlee|hitmonlee|Hitmonchan|hitmonchan|Lickitung|lickitung|Koffing|koffing|Weezing|weezing|Rhyhorn|rhyhorn|Rhydon|rhydon|Chansey|chansey|Tangela|tangela|Kangaskhan|kangaskhan|Horsea|horsea|Seadra|seadra|Goldeen|goldeen|Seaking|seaking|Staryu|staryu|Starmie|starmie|MrMime|mrmime|Scyther|scyther|Jynx|jynx|Electabuzz|electabuzz|Magmar|magmar|Pinsir|pinsir|Tauros|tauros|Magikarp|magikarp|Gyarados|gyarados|Lapras|lapras|Ditto|ditto|Eevee|eevee|Vaporeon|vaporeon|Jolteon|jolteon|Flareon|flareon|Porygon|porygon|Omanyte|omanyte|Omastar|omastar|Kabuto|kabuto|Kabutops|kabutops|Aerodactyl|aerodactyl|Snorlax|snorlax|Articuno|articuno|Zapdos|zapdos|Moltres|moltres|Dratini|dratini|Dragonair|dragonair|Dragonite|dragonite|Mewtwo|mewtwo|Mew|mew)).*$"
    
    # Manage channel rare_spottings only
    if message.channel.name in channels:
        if not re.match(partern, message.content):      
            # Log & print out
            log_message = 'Message has been deleted: {} - Author: {}'.format(message.content, message.author.name)
            print(log_message)
            logging.warning(log_message)

            # Delete message if not contain lat/long
            await client.delete_message(message)


# Loop task
client.loop.create_task(get_rare_pokemons())

# Start client
client.run(api_key)
