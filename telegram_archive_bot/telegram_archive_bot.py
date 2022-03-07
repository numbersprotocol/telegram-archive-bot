#!/usr/bin/env python3
#
# Copyright 2022 Numbers Protocol
# Copyright 2022 Starling Lab
#
# This file is part of Telegram Archive Bot (TAB).
#
# TAB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TAB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TAB.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import json
import logging
import os
import subprocess
import tempfile
import tarfile
import threading
import time
import zipfile

import telegram.ext

from datetime import datetime
from logzero import setup_logger


logger = setup_logger(
    name = 'starling',
    logfile='./telegram.log',
)


class TelegramBotService(object):
    def __init__(self, token, debug=False):
        if os.path.isfile(token):
            self.token = self.get_token_from_config(token)
        else:
            self.token = token

        self.debug = debug

        # Telegram Updater employs Telegram Dispatcher which dispatches
        # updates to its registered handlers.
        self.updater = telegram.ext.Updater(self.token,
                                            use_context=True)

        self.update_data_dir()
        self.archiver()

    def get_token_from_config(self, config):
        with open(config) as f:
            cfg = json.load(f)
        return cfg['token']

    def run(self, args):
        """Infinite loop serving inference requests"""
        self.connect_telegram(args)

    def connect_telegram(self, args):
        try:
            self.updater.dispatcher.add_handler(
                telegram.ext.CommandHandler('help', self.handler_help))
            self.updater.dispatcher.add_handler(
                telegram.ext.CommandHandler('hi', self.handler_hi))
            self.updater.dispatcher.add_handler(
                telegram.ext.MessageHandler(
                    filters=None,
                    callback=self.handler_message
                )
            )

            if (args["has_getlog"]):
                self.updater.dispatcher.add_handler(
                    telegram.ext.CommandHandler('getlog', self.handler_getlog))
            self.updater.start_polling()
        except Exception as e:
            logger.critical(e)

    def handler_help(self, update, context):
        logger.info("Received command `help`")
        update.message.reply_text((
            'I support these commands:\n\n'
            'help - Display help message.\n'
            'hi - Test Telegram client.\n'
        ))

    def handler_hi(self, update, context):
        logger.info("Received command `hi`")
        update.message.reply_text(
            'Hi, {}'.format(update.message.from_user.first_name))

    def handler_message(self, update, context):
        logger.debug(f'update: {update}, context: {context}')
        self.save_message(update)
        # if len(update.message.text) > 0:
        #     update.message.reply_text(update.message.text)

        # User uploaded image(s) and chose "Compress images"
        if len(update.message.photo) > 0:
            # Telegram will create (4) different size JPEG images,
            # and they are not the original image.
            file_id = update.message.photo[-1].file_id
            logger.debug(f'Find photo {file_id}')
            file = context.bot.get_file(file_id)
            save_to = os.path.join(
                self.data_dir,
                f'{file_id}.jpeg'
            )
            with open(save_to, 'wb') as f:
                f.write(file.download_as_bytearray())
        else:
            pass

        if 'document' in update.message.to_dict():
            file_id = update.message.document.file_id
            logger.debug(f'Find document {file_id}')
            file = context.bot.get_file(file_id)
            save_to = os.path.join(
                self.data_dir,
                update.message.document.file_name
            )
            with open(save_to, 'wb') as f:
                f.write(file.download_as_bytearray())
        else:
            pass

    def update_data_dir(self):
        '''Update data dir by using current timestamp as name
        '''
        data_dir = 'data'
        try:
            subprocess.call(f'mkdir -p {data_dir}', shell=True)
            self.data_dir = data_dir
        except Exception as e:
            logger.warn(f'Fail to create data dir: {data_dir}')

    def save_message(self, update):
        message_timestamp = int(update.message.date.timestamp())
        message_filepath = os.path.join(self.data_dir,
                                        f'{message_timestamp}.json')
        with open(message_filepath , 'w') as f:
            json.dump(update.to_dict(), f)
            logger.debug(f'Save message {message_filepath}')

    def archiver(self):
        '''Create an archive for every interval seconds

        An archive is a Zip file consisting of the messages and attachments
        sent to the bot during an interval.
        '''
        # Default interval is 60 seconds
        interval = 60
        # Setting to False for development or debugging purpose
        create_zip = True

        threading.Timer(interval, self.archiver).start()

        if not os.listdir(self.data_dir):
            logger.debug('data dir is empty, will not create an archive')
            return
        else:
            pass

        current_timestamp = int(datetime.now().timestamp())
        archive_dir = f'archive/{current_timestamp}'
        logger.debug(f'Create an archive at {archive_dir}')

        # Create a temporary archive dir to store messages and attachments
        # for creating an archive later
        try:
            subprocess.call(f'mkdir -p {archive_dir}', shell=True)
        except Exception as e:
            logger.warn(f'Fail to create archive dir {archive_dir}')

        try:
            subprocess.call(f'mv {self.data_dir}/* {archive_dir}', shell=True)
        except Exception as e:
            logger.warn(f'Fail to move data to archive dir {archive_dir}')

        if create_zip:
            try:
                logger.debug(f'Create archive {archive_dir}.zip')
                with zipfile.ZipFile(f'{archive_dir}.zip', 'w') as zipf:
                    for dir_name, subdir_names, file_names in os.walk(archive_dir):
                        for file_name in file_names:
                            file_path = os.path.join(archive_dir, file_name)
                            zipf.write(file_path, os.path.basename(file_path))
            except Exception as e:
                logger.warn(f'Fail to create archive {archive_dir}.zip')

            # Delete the temporary archive dir
            try:
                logger.debug(f'Delete archive dir {archive_dir}')
                subprocess.call(f'rm -rf {archive_dir}', shell=True)
            except Exception as e:
                logger.warn(f'Fail to delete archive dir {archive_dir}')

            logger.info(f'Archive is at {archive_dir}.zip')
        else:
            logger.info(f'Archive is at {archive_dir}')

    def handler_getlog(self, update, context):
        '''(Dev-only) Get system log for debugging
        '''
        logger.info("Received command `getlog`, chat id: %s" % update.message.chat_id)

        # Create temporary tar.xz file
        tmpTGZ1 = tempfile.NamedTemporaryFile(suffix=".tar.xz")
        tmpTGZ = tarfile.open(fileobj=tmpTGZ1, mode="w:xz")
        tmpTGZPath = tmpTGZ1.name

        # Traverse /var/log
        varlogDir = os.path.abspath(os.path.join(os.sep, "var", "log"))
        for root, dirs, files in os.walk(varlogDir):
            for file in files:
                fullPath = os.path.join(root, file)
                # Check if the file is a regular file
                if not os.path.isfile(fullPath):
                    continue
                # Check if the file is accessable
                if not os.access(fullPath, os.R_OK):
                    continue
                # Pack the file
                tmpTGZ.add(name = fullPath, recursive=False)
        tmpTGZ.close()
        self.updater.bot.send_document(chat_id = update.message.chat_id, document = open(tmpTGZPath, 'rb'), filename=time.strftime('berrynet-varlog_%Y%m%d_%H%M%S.tar.xz'))


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--token',
        help=('Telegram token got from BotFather, '
              'or filepath of a JSON config file with token.')
    )
    ap.add_argument('--debug',
        action='store_true',
        help='Debug mode toggle'
    )
    ap.add_argument('--has-getlog',
        action='store_true',
        help='Enable getlog command'
    )
    return vars(ap.parse_args())


def main():
    args = parse_args()
    if args['debug']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    telbot_service = TelegramBotService(args['token'], args['debug'])
    telbot_service.run(args)


if __name__ == '__main__':
    main()
