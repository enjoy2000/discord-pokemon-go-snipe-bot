#
# Python chat bot for discord - Pokemon Go Snipe Channel
# Author: enjoy2000 | enjoy3013@gmail.com
#
import discord
import json
import sys

from snipe_bot import SnipeBot, logger

# test
client = discord.Client()

if __name__ == '__main__':

    @client.event
    async def on_ready():
        """ Connected to bot """

        logger.log('Logged in as')
        logger.log(client.user.name)
        logger.log(client.user.id)
        logger.log('------')

    config = {}
    with open('config.json') as output:
        # Load json to config object
        config = json.load(output)

    bot = SnipeBot(client, config)
    api_key = config.get('api_key', 'NA')

    if api_key == 'NA':
        raise Exception('Please specify your api key!')

    if len(sys.argv) == 2:
        worker_name = {
            'scrawl': 'PokeSnipers',
            'trackemon': 'Trackemon'
        }.get(sys.argv[1], 'PokeSnipers')

        bot.run_worker(worker_name)
    else:

        @client.event
        async def on_message(message):
            if bot.on_message(message):
                await client.delete_message(message)

        bot.run_worker('ChannelManagement')


    client.run(api_key)
