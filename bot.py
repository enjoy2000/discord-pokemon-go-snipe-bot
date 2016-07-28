#
# Python chat bot for discord - Pokemon Go Snipe Channel
# Author: enjoy2000 | enjoy3013@gmail.com
#

import asyncio
import discord
import re

# Config your token
token = 'API_TOKEN'

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    # Check if message contains lat/long

    # patern for check string contains lat/long
    partern = "(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)"

    print(message.content)
    
    if re.match(partern, message.content):
        # Message contains lat/long
        print('ok')
    else:
        # Delete message if not contain lat/long
        print('Need to delete')
        await client.delete_message(message)

# Start client
client.run(token)
