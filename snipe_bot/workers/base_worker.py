class BaseWorker(object):

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.client = self.bot.client

        self.initialize()

    def initialize():
        pass
