# discord-pokemon-go-snipe-bot
### You have to grant `Manage Messages` to your bot

Simple chat bot to delete messages that not contain lat/long and pokemon name
So message for `spottings` need to be in this format
```
lat,long pokemon_name [IV] [extra info]
```

If not, the messages will be deleted automatically.


## Requirements

- Python 3.4.2+
- `aiohttp` library
- `websockets` library
- `PyNaCl` library (optional, for voice only)
    - On Linux systems this requires the `libffi` library. You can install in
      debian based systems by doing `sudo apt-get install libffi-dev`.

Usually `pip` will handle these for you.

## Getting Started

```bash
git clone git@github.com:enjoy2000/discord-pokemon-go-snipe-bot.git
cd discord-pokemon-go-snipe-bot
pip3 install -r requirements.txt
cp config.json.sample config.json
```
Grab your `api_key` (bot token) and put it in `config.json`, also modify your channel name

Finaly start your bot
```bash
python3 bot.py
```
## Adding Bot To Your Channel
- Go to [Discord Developers Page](https://discordapp.com/developers/applications/me) to create your bot.
- Open this url with your client_id to authorize your app
```
https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=0
```
- Add bot to your server
![Add bot to your server](https://raw.githubusercontent.com/enjoy2000/discord-pokemon-go-snipe-bot/master/docs/add-bot-to-your-server.png)
- Now you can run bot to manage your channels
