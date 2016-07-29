# discord-pokemon-go-snipe-bot
### You have to grant `Manage Messages` for your bot

Simple chat bot to delete messages that not contain lat/long
So message for `spottings` need to be in this format
```
lat/long IV pokemon_name
```
no matter what the order.

If not the messages will be deleted automatically.


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
Grab your `api_key` and put it in `config.json`, also modify your channel name

Finaly start your bot
```bash
python3 bot.py
```
