# Telegram Archive Bot (TAB)

Telegram Archive Bot creates Archives consisting of the received messages and attachments every 60 seconds.

Archives are Zip files stored in `archive/`.

Before creating an archive, TAB puts the messages and attachments in the temporary directory `data/`.

## Register a Telegram Bot

You need to register a Telegram Bot and get its access token before running TAB.

Steps to register a Telegram Bot and get its access token:

1. Install a Telegram app on your mobile or desktop.
2. Search `@botfather` and start a conversation.
3. Send `/newbot`.
4. Enter bot username and bot name
5. BotFather will send a message including:
    * Bot link: You can start a conversation with the bot by clicking the link.
    * HTTP API Token (Access Token): Write down the token. It is necessary to run TAB.

## Create Configuration

```
mkdir -p ~/.config/telegram-archive-bot/
cp config.json.example ~/.config/telegram-archive-bot/config.json
```

Put your Telegram bot's access token into `config.json`.

## Execute Telegram Archive Bot

Create the execution environment

```
virtualenv -p python3 venv
source venv/bin/activate
python3 -m pip install python-telegram-bot logzero
```

Run TAB

```
python3 telegram_archive_bot.py --token ~/.config/telegram-archive-bot/config.json [--debug]
```

or

```
python3 telegram_archive_bot.py --token <bot-access-token> [--debug]
```

There will be a log file `telegram.log` in the directory where `telegram_archive_bot.py` is.

Now, you can send messages and files to TAB, and TAB will create Archives in `archive/` every 60 seconds.

## (Optional) Echo Bot with Restful API

For demonstrating how to integrate Telegram Bot and Restful API together.

### deploy

#### package install

```
pip install fastapi uvicorn python-telegram-bot
```

#### app build

```
cp config.ini.example config.int
```

config.int:

```
[TELEGRAM]
ACCESS_TOKEN =${your api token}
```

```
uvicorn main:app --host 0.0.0.0 --port ${port}
```

#### chatbot webhook setting

send this get request
```
https://api.telegram.org/bot${your api token}/setWebhook?url=${your deploy url}/hook
```
and then you need to get this result
```
{"ok":true,"result":true,"description":"Webhook was set"}
```