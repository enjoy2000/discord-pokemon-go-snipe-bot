#
# Python chat bot for discord - Pokemon Go Snipe Channel
# Author: enjoy2000 | enjoy3013@gmail.com
#

import asyncio
import discord
import json
import re

client = discord.Client()

config = {}
with open('config.json') as output:
    # Load json to config object
    config = json.load(output)

api_key = config.get('api_key', 'NA')
channels = config.get('channels', [])
except_roles = config.get('except_roles', [])

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
    """
    Ignore if message from except roles
    """
    for role in message.author.roles:
        if role.name in except_roles:
            return None

    """
    Check if message contains lat/long
    """
    # patern for check string contains lat/long
    partern = "(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)"
    
    # Manage channel rare_spottings only
    if message.channel.name in channels:
        if not re.match(partern, message.content):
            # Delete message if not contain lat/long
            await client.delete_message(message)

# Start client
client.run(api_key)
