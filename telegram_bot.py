import telegram
from telegram import *
from telegram.ext import *
from configuration import Configuration


class Telegram:

    def __init__(self,
                 login_method: None,
                 search_for_workable_heroes: None,
                 refresh_heroes_positions_method: None,
                 balance_method: None,
                 send_screenshot_method=None,
                 refresh_page_method=None,
                 send_execution_infos_method=None,
                 rest_all_method=None
                 ):

        self.active = Configuration.telegram['active']
        self.multi = Configuration.telegram['multi']

        if self.active:
            self.tokenMain = Configuration.telegram['tokenMain']
            self.chatidMain = Configuration.telegram['chatidMain']

            if self.multi:
                self.secondaryInfos = Configuration.telegram['secondaryInfos']

            self.login_method = login_method
            self.search_for_workable_heroes = search_for_workable_heroes
            self.refresh_heroes_positions_method = refresh_heroes_positions_method
            self.balance_method = balance_method
            self.send_screenshot_method = send_screenshot_method
            self.refresh_page_method = refresh_page_method
            self.send_execution_infos_method = send_execution_infos_method
            self.rest_all_method = rest_all_method

            if int(len(self.tokenMain)) > 10 and int(len(self.chatidMain) >= 5):
                self.bot = self.criar_bot_telegram(self.tokenMain)

                if self.multi:
                    self.secondaryBots = []

                    for i in self.secondaryInfos:
                        aux = self.secondaryInfos[i]

                        if int(len(aux['token'])) > 10 and int(len(aux['chatid']) >= 5):
                            self.secondaryBots.append(self.criar_bot_telegram(aux['token']))

                self.telsendtext('''
        /start Iniciar Bot
        ''', 0)
                print('>>---> Notificações no Telegram habilitadas.\n')
            else:
                print('>>---> Notificações no Telegram desabilitadas.\n')

    def start_command(self, update: Update, context: CallbackContext):
        buttons = [
            [KeyboardButton("Login")],
            [KeyboardButton("Work")],
            [KeyboardButton("Refresh Positions")],
            [KeyboardButton("Balance")],
            [KeyboardButton("Screenshot")],
            [KeyboardButton("Refresh Page")],
            [KeyboardButton("Executions Infos")],
            [KeyboardButton("Rest All")]
        ]

        context.bot.send_message(chat_id=update.effective_chat.id, text="Bem vindo!",
                                 reply_markup=ReplyKeyboardMarkup(buttons))

    def message_handler(self, update: Update, context: CallbackContext):
        if "Login" in update.message.text:
            self.login_method(True)
        elif "Work" in update.message.text:
            self.search_for_workable_heroes(True)
        elif "Refresh Positions" in update.message.text:
            self.refresh_heroes_positions_method(True)
        elif "Balance" in update.message.text:
            self.balance_method(True)
        elif "Screenshot" in update.message.text:
            self.send_screenshot_method(True)
        elif "Refresh Page" in update.message.text:
            self.refresh_page_method(True)
        elif "Executions Infos" in update.message.text:
            self.send_execution_infos_method()
        elif "Rest All" in update.message.text:
            self.rest_all_method()

    def criar_bot_telegram(self, token):
        return telegram.Bot(token=token)

    def telsendtext(self, bot_message, activeaccount, num_try=0):
        if not self.active:
            return

        try:
            self.bot.send_message(chat_id=self.chatidMain, text=bot_message)
        except:
            if num_try == 1:
                self.bot = self.criar_bot_telegram(self.tokenMain)
                return self.telsendtext(bot_message, activeaccount, 1)
            return 0

        if activeaccount != 0:
            if activeaccount in self.secondaryInfos[activeaccount]['profilesToSendMessage']:
                try:
                    return self.secondaryBots[activeaccount - 1].send_message(
                        chat_id=self.secondaryInfos[activeaccount]['chatid'], text=bot_message)
                except:
                    if num_try == 1:
                        self.secondaryBots.insert(activeaccount - 1, self.criar_bot_telegram(
                            self.secondaryInfos[activeaccount]['token']))
                        return self.telsendtext(bot_message, activeaccount, 1)
                    return 0

    def telsendphoto(self, photo_path, activeaccount, num_try=0):
        if not self.active:
            return

        try:
            self.bot.send_photo(chat_id=self.chatidMain, photo=open(photo_path, 'rb'))
        except:
            if num_try == 1:
                self.bot = self.criar_bot_telegram(self.tokenMain)
                return self.telsendphoto(photo_path, 1)
            return 0

        if activeaccount != 0:
            if activeaccount in self.secondaryInfos[activeaccount]['profilesToSendMessage']:
                try:
                    return self.secondaryBots[activeaccount - 1].send_photo(
                        chat_id=self.secondaryInfos[activeaccount]['chatid'], photo=open(photo_path, 'rb'))
                except:
                    if num_try == 1:
                        self.secondaryBots.insert(activeaccount - 1,
                                                  self.criar_bot_telegram(self.secondaryInfos[activeaccount]['token']))
                        return self.telsendphoto(photo_path, 1)
                    return 0
