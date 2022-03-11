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

## Set Bot Enable to archive group message

You need to chat with botfather and disable the privacy mode

![image info](https://user-images.githubusercontent.com/45333055/157828711-296aa904-fc19-497b-acbf-b251228bad98.png)
add Group Privacy
![image info](https://user-images.githubusercontent.com/45333055/157828723-a6c05855-b55e-4f44-9de5-63c0cc1ee4cf.png)

## Create Configuration

```
mkdir -p ~/.config/telegram-archive-bot/
cp config.json.example config.json
```

Put your Telegram bot's access token into `config.json`.

```
cp config.json ~/.config/telegram-archive-bot/config.json
```

## Execute Telegram Archive Bot

### Run in Local

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

### Run with docker compose

```
$ docker-compose up -d
```

There will be a log file `telegram.log` in the directory where `telegram_archive_bot.py` is.

Now, you can send messages and files to TAB, and TAB will create Archives in `archive/` every 60 seconds.

## (Optional) Echo Bot with Restful API

For demonstrating how to integrate Telegram Bot and Restful API together.

### Local development

```
  $ cd telegram_bot_backend
  $ cp .env.example .env
  # Edit .env to fill in desired environment variables
  $ cd app
  $ cp ../.env .env
  $ poetry install
  $ poetry run uvicorn main:app --reload --host 0.0.0.0 --port ${port}
  # The server would be listening on localhost:{port} now
```

### Run with docker compose

```
$ cd backend
$ cp .env.example .env
# Edit .env to fill in desired environment variables
$ docker-compose up -d
```
### chatbot webhook setting

send this get request
```
https://api.telegram.org/bot${your api token}/setWebhook?url=${your deploy url}/hook
```
and then you need to get this result
```
{"ok":true,"result":true,"description":"Webhook was set"}
```
