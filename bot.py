import time
import sys
import os
from cv2 import cv2
from os import listdir
from random import random, randint
import pyautogui
from datetime import datetime

from src.logger import logger, loggerMapClicked
from configuration import Configuration
from telegram_bot import Telegram
from screen_controls import ScreenControls
from instructions import instruction
from strings import Strings


class Bot:

    def __init__(self):
        pyautogui.PAUSE = Configuration.c['time_intervals']['interval_between_movements']
        pyautogui.FAILSAFE = False
        pyautogui.MINIMUM_DURATION = 0.1
        pyautogui.MINIMUM_SLEEP = 0.1
        pyautogui.PAUSE = 2

        self.images = self.load_images()
        self.home_heroes = self.load_heroes_to_send_home()
        self.windows = self.load_windows()

        self.telegram = Telegram(
            self.login,
            self.search_for_workable_heroes,
            self.refresh_heroes_positions,
            self.go_balance,
            self.send_screenshot,
            self.refresh_page,
            self.send_executions_infos,
            self.rest_all
        )
        self.hero_clicks = 0
        self.login_attempts = 0
        self.last_log_is_progress = False
        self.accounts = 0
        self.activeaccount = 0
        self.accountLabels = Configuration.accountLabels
        self.defaultProfileLabel = None
        self.strings = Strings(Configuration.language)
        # self.accountslist = list(range(0, self.accounts))

    # region Configs

    def remove_suffix(self, input_string, suffix):
        if suffix and input_string.endswith(suffix):
            return input_string[:-len(suffix)]
        return input_string

    def load_images(self):
        file_names = listdir('./targets/')
        targets = {}
        for file in file_names:
            path = 'targets/' + file
            targets[self.remove_suffix(file, '.png')] = cv2.imread(path)
        return targets

    def load_heroes_to_send_home(self):
        if not Configuration.home['enable']:
            return

        file_names = listdir('./targets/heroes-to-send-home')
        heroes = []
        for file in file_names:
            path = './targets/heroes-to-send-home/' + file
            heroes.append(cv2.imread(path))

        print(f">>---> {self.strings.getRegionalizedString(0)} {len(heroes)}")
        return heroes

    def load_windows(self):
        windows = []
        t = Configuration.c['time_intervals']
        for window in ScreenControls.getWindowsWithTitle():
            if window.title.count('bombcrypto-multibot') >= 1:
                continue

            windows.append({
                'window': window,
                'disconnected': 0,
                'login': 0,
                'heroes': 0,
                'balance': 0,
                'new_map': 0,
                'refresh_heroes': 0,
                'send_screenshot': t['send_screenshot'] * 60,
                'refresh_page': t['refresh_page'] * 60,
                'maps': []
            })

        return windows

    def add_randomness(self, n, randomn_factor_size=None):
        if randomn_factor_size is None:
            randomness_percentage = 0.1
            randomn_factor_size = randomness_percentage * n

        random_factor = 2 * random() * randomn_factor_size
        if random_factor > 5:
            random_factor = 5
        without_average_random_factor = n - randomn_factor_size
        randomized_n = int(without_average_random_factor + random_factor)
        return int(randomized_n)

    # endregion

    # region Click de Botões

    def click_on_go_work(self):
        return ScreenControls.positions(self.images['go-work'], threshold=Configuration.threshold['go_to_work_btn'])

    def click_on_go_home(self):
        return ScreenControls.positions(self.images['go-home'],
                                        threshold=Configuration.threshold['home_button_threshold'])

    def click_on_hero_home(self, image):
        return ScreenControls.positions(image, threshold=Configuration.threshold['hero_threshold'])

    def click_on_green_bar(self):
        return ScreenControls.positions(self.images['green-bar'], threshold=Configuration.threshold['green_bar'])

    def click_on_full_bar(self):
        return ScreenControls.positions(self.images['full-stamina'], threshold=Configuration.threshold['default'])

    def click_on_treasure_hunt(self, timeout=3):
        return ScreenControls.clickbtn(self.images['treasure-hunt-icon'], timeout=timeout)

    def click_on_x(self):
        return ScreenControls.clickbtn(self.images['x'])

    def click_on_ok(self):
        return ScreenControls.clickbtn(self.images['ok'])

    def click_on_go_back(self):
        return ScreenControls.clickbtn(self.images['go-back-arrow'])

    def click_on_heroes(self):
        return ScreenControls.clickbtn(self.images['hero-icon'])

    def click_on_send_all(self):
        return ScreenControls.positions(self.images['send-all'], threshold=Configuration.threshold['go_to_work_btn'])

    def click_on_rest_all(self):
        return ScreenControls.positions(self.images['rest-all'], threshold=Configuration.threshold['go_to_work_btn'])

    def click_on_balance(self):
        ScreenControls.clickbtn(self.images['consultar-saldo'])

    # endregion

    # region Painel Herói

    def scroll(self):
        hero_item_list = ScreenControls.positions(self.images['hero-item'], threshold=Configuration.threshold['common'])
        if len(hero_item_list) == 0:
            return
        x, y, w, h = hero_item_list[len(hero_item_list) - 1]
        ScreenControls.movetowithrandomness(x, y, 1)

        if not Configuration.c['use_click_and_drag_instead_of_scroll']:
            pyautogui.scroll(-Configuration.c['scroll_size'])
        else:
            pyautogui.dragRel(0, -Configuration.c['click_and_drag_amount'], duration=1, button='left')

    def rest_all(self):
        logger(f'⚒️ {self.strings.getRegionalizedString(1)}', 'green')
        self.go_to_heroes()
        time.sleep(7)
        self.click_on_rest_all()
        time.sleep(7)
        self.go_to_treasure_hunt()

    def is_working(self, bar, buttons):
        y = bar[1]

        for (_, button_y, _, button_h) in buttons:
            isbelow = y < (button_y + button_h)
            isabove = y > (button_y - button_h)
            if isbelow and isabove:
                return False
        return True

    def is_home(self, hero, buttons):
        y = hero[1]

        for (_, button_y, _, button_h) in buttons:
            isbelow = y < (button_y + button_h)
            isabove = y > (button_y - button_h)
            if isbelow and isabove:
                return False
        return True

    def send_all(self):
        buttons = self.click_on_send_all()
        for (x, y, w, h) in buttons:
            ScreenControls.movetowithrandomness(x + (w / 2), y + (h / 2), 1)
            pyautogui.click()

    def send_green_bar_heroes_to_work(self):
        offset = 140

        green_bars = self.click_on_green_bar()
        logger(f'🟩 {len(green_bars)} {self.strings.getRegionalizedString(2)}')
        buttons = self.click_on_go_work()
        logger(f'🆗 {len(buttons)} {self.strings.getRegionalizedString(3)}')

        not_working_green_bars = []
        for bar in green_bars:
            if not self.is_working(bar, buttons):
                not_working_green_bars.append(bar)
        if len(not_working_green_bars) > 0:
            logger(f'🆗 {len(not_working_green_bars)} {self.strings.getRegionalizedString(4)}')
            logger(
                f'👆 {self.strings.getRegionalizedString(5)} {len(not_working_green_bars)} {self.strings.getRegionalizedString(6)}')

        hero_clicks_cnt = 0
        for (x, y, w, h) in not_working_green_bars:
            ScreenControls.movetowithrandomness(x + offset + (w / 2), y + (h / 2), 1)
            pyautogui.click()
            self.hero_clicks = self.hero_clicks + 1
            hero_clicks_cnt = hero_clicks_cnt + 1
            if hero_clicks_cnt > 20:
                logger(f'⚠️ {self.strings.getRegionalizedString(7)}')
                return
        return len(not_working_green_bars)

    def send_full_bar_heroes_to_work(self):
        offset = 100
        full_bars = self.click_on_full_bar()
        buttons = self.click_on_go_work()

        not_working_full_bars = []
        for bar in full_bars:
            if not self.is_working(bar, buttons):
                not_working_full_bars.append(bar)

        if len(not_working_full_bars) > 0:
            logger(
                f'👆 {self.strings.getRegionalizedString(5)} {len(not_working_full_bars)} {self.strings.getRegionalizedString(6)}')
            logger(
                f'👆 {self.strings.getRegionalizedString(5)} {len(not_working_full_bars)} {self.strings.getRegionalizedString(6)}')

        for (x, y, w, h) in not_working_full_bars:
            ScreenControls.movetowithrandomness(x + offset + (w / 2), y + (h / 2), 1)
            pyautogui.click()
            self.hero_clicks = self.hero_clicks + 1

        return len(not_working_full_bars)

    def send_heroes_to_work(self):
        if Configuration.c['select_heroes_mode'] == 'full':
            return self.send_full_bar_heroes_to_work()
        elif Configuration.c['select_heroes_mode'] == 'green':
            return self.send_green_bar_heroes_to_work()
        else:
            return self.send_all()

    def send_heroes_to_home(self):
        if not Configuration.home['enable']:
            return
        heroes_positions = []
        for hero in self.home_heroes:
            hero_positions = self.click_on_hero_home(hero)
            if not len(hero_positions) == 0:
                hero_position = hero_positions[0]
                heroes_positions.append(hero_position)

        n = len(heroes_positions)
        if n == 0:
            print(self.strings.getRegionalizedString(8))
            return
        print(f'{n} {self.strings.getRegionalizedString(9)}')
        go_home_buttons = self.click_on_go_home()
        go_work_buttons = self.click_on_go_work()

        for position in heroes_positions:
            if not self.is_home(position, go_home_buttons):
                print(self.is_working(position, go_work_buttons))
                if not self.is_working(position, go_work_buttons):
                    print(self.strings.getRegionalizedString(10))
                    ScreenControls.movetowithrandomness(go_home_buttons[0][0] + go_home_buttons[0][2] / 2,
                                                        position[1] + position[3] / 2,
                                                        1)
                    pyautogui.click()
                else:
                    print(self.strings.getRegionalizedString(11))
            else:
                print(self.strings.getRegionalizedString(12))

    def go_to_heroes(self):
        if self.click_on_go_back():
            self.login_attempts = 0

        time.sleep(3)
        self.click_on_heroes()
        time.sleep(3)

    def search_for_workable_heroes(self, update_last_execute=False):
        if update_last_execute:
            self.telegram.telsendtext(self.strings.getRegionalizedString(13), self.activeaccount)
            for currentWindow in self.windows:
                currentWindow['heroes'] = 0

            return

        self.go_to_heroes()

        if Configuration.c['select_heroes_mode'] == 'full':
            logger(f'⚒️ {self.strings.getRegionalizedString(14)}', 'green')
        elif Configuration.c['select_heroes_mode'] == 'green':
            logger(f'⚒️ {self.strings.getRegionalizedString(15)}', 'green')
        else:
            logger(f'⚒️ {self.strings.getRegionalizedString(16)}', 'green')

        empty_scrolls_attempts = Configuration.c['scroll_attempts']

        if Configuration.c['select_heroes_mode'] == 'all':
            time.sleep(3)
            self.send_all()
            logger(self.strings.getRegionalizedString(17))
            time.sleep(3)
        else:
            while empty_scrolls_attempts > 0:
                self.send_heroes_to_work()
                self.send_heroes_to_home()
                empty_scrolls_attempts = empty_scrolls_attempts - 1
                self.scroll()
                time.sleep(2)
            logger(f'💪 {self.hero_clicks} {self.strings.getRegionalizedString(18)}')

        self.go_to_treasure_hunt()

    # endregion

    def go_to_treasure_hunt(self):
        self.click_on_x()
        time.sleep(3)
        self.click_on_treasure_hunt()

    def refresh_heroes_positions(self, update_last_execute=False):
        if update_last_execute:
            self.telegram.telsendtext(self.strings.getRegionalizedString(19), 0)
            for currentWindow in self.windows:
                currentWindow['refresh_heroes'] = 0

            return
        C = Configuration.c['time_intervals']
        if C["refresh_heroes"] == True:
            logger(f'🔃 {self.strings.getRegionalizedString(20)}')
            self.click_on_go_back()
            time.sleep(3)
            self.click_on_treasure_hunt()

    # login

    def login(self, update_last_execute=False):
        if update_last_execute:
            self.telegram.telsendtext(self.strings.getRegionalizedString(21), 0)
            for currentWindow in self.windows:
                currentWindow['login'] = 0
            return

        logger(f'😿 {self.strings.getRegionalizedString(22)}')

        if self.login_attempts > 10:
            logger(f'🔃 {self.strings.getRegionalizedString(23)}')
            self.login_attempts = 0
            pyautogui.hotkey('ctrl', 'f5')
            return

        if ScreenControls.clickbtn(self.images['ok'], timeout=3):
            pass

        if ScreenControls.clickbtn(self.images['connect-wallet'], timeout=12):
            logger(f'🎉 {self.strings.getRegionalizedString(24)}')
            self.login_attempts = self.login_attempts + 1
            time.sleep(3)

        # Login activated
        l = Configuration.c['login_with_pass']
        if l["activated"] == True:
            if ScreenControls.clickbtn(self.images['type-username'], timeout=4):
                ScreenControls.inputtype(l["accounts"][self.activeaccount]["username"])
                logger(f'⌨ {self.strings.getRegionalizedString(25)}')

            if ScreenControls.clickbtn(self.images['type-password'], timeout=4):
                ScreenControls.inputtype(l["accounts"][self.activeaccount]["password"])
                logger(f'⌨ {self.strings.getRegionalizedString(26)}')

            if ScreenControls.clickbtn(self.images['connect-login'], timeout=5):
                logger(f'👌 {self.strings.getRegionalizedString(27)}')
                self.login_attempts = self.login_attempts + 1
                time.sleep(4)

                if self.click_on_treasure_hunt(timeout=5):
                    self.login_attempts = 0
                return
            else:
                pass

        else:
            if ScreenControls.clickbtn(self.images['connect-metamask'], timeout=5):
                logger(f'👌 {self.strings.getRegionalizedString(28)}')
                self.login_attempts = self.login_attempts + 1
                time.sleep(4)

                if ScreenControls.clickbtn(self.images['select-wallet-2'], timeout=6):
                    self.login_attempts = self.login_attempts + 1
                    time.sleep(5)

                    if self.click_on_treasure_hunt(timeout=5):
                        self.login_attempts = 0
                    return
            else:
                pass

    def disconnect(self):
        logger(f'{self.strings.getRegionalizedString(45)}')
        time.sleep(6)
        if ScreenControls.clickbtn(self.images['ok'], timeout=3) or ScreenControls.clickbtn(self.images['connect-wallet'], timeout=3):
            logger(f'{self.strings.getRegionalizedString(46)}')
            self.login()
            time.sleep(5)
            self.click_on_treasure_hunt(timeout = 3)
            self.login_attempts = 0
        else:
            logger(f'{self.strings.getRegionalizedString(47)}')
            pass

    def go_balance(self, update_last_execute=False, curwind=''):
        if update_last_execute:
            self.telegram.telsendtext(self.strings.getRegionalizedString(29), 0)
            for currentWindow in self.windows:
                currentWindow['balance'] = 0
            return

        logger(self.strings.getRegionalizedString(30))
        time.sleep(2)
        self.click_on_balance()
        i = 10
        coins_pos = ScreenControls.positions(self.images['coin-icon'], threshold=Configuration.threshold['default'])
        while len(coins_pos) == 0:
            if i <= 0:
                break
            i = i - 1
            coins_pos = ScreenControls.positions(self.images['coin-icon'], threshold=Configuration.threshold['default'])
            time.sleep(3)

        if len(coins_pos) == 0:
            logger(self.strings.getRegionalizedString(31))
            self.click_on_x()
            return

        left, top, width, height = coins_pos[0]
        left -= 10
        top -= 40
        width = 586
        height = 180

        myscreen = pyautogui.screenshot(region=(left, top, width, height))
        print(f'r = {left}, {top}, {width}, {height}')
        img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\targets\saldo1.png'
        myscreen.save(img_dir)
        time.sleep(3)

        enviar = f'{self.strings.getRegionalizedString(32)} {self.get_profile_label()} 🚀🚀🚀'
        self.telegram.telsendtext(enviar, self.activeaccount)
        self.telegram.telsendphoto(img_dir, self.activeaccount)
        self.click_on_x()
        time.sleep(3)

    def send_screenshot(self, update_last_execute=False):
        if update_last_execute:
            self.telegram.telsendtext(self.strings.getRegionalizedString(33), 0)
            for currentWindow in self.windows:
                currentWindow['send_screenshot'] = 0

            return

        if self.click_on_treasure_hunt(timeout = 3):
            pass

        myscreen = pyautogui.screenshot()
        img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\targets\allscreens.png'
        myscreen.save(img_dir)
        time.sleep(3)
        self.telegram.telsendtext(f'{self.strings.getRegionalizedString(34)} {self.get_profile_label()}', self.activeaccount)
        self.telegram.telsendphoto(img_dir, self.activeaccount)
        time.sleep(3)

    def refresh_page(self, update_last_execute=False):
        self.telegram.telsendtext(self.strings.getRegionalizedString(35), 0)
        for currentWindow in self.windows:
            currentWindow['refresh_page'] = 0
            currentWindow['login'] = 0
            currentWindow['window'].activate()
            pyautogui.hotkey('ctrl', 'f5')
            time.sleep(10)

    def send_executions_infos(self):
        for currentWindow in self.windows:
            title = currentWindow['window'].title
            print(currentWindow['login'])
            login = '' if currentWindow['login'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S',
                                                                         time.localtime(int(currentWindow['login'])))
            heroes = '' if currentWindow['heroes'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S',
                                                                           time.localtime(int(currentWindow['heroes'])))
            balance = '' if currentWindow['balance'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(
                int(currentWindow['balance'])))
            new_map = '' if currentWindow['new_map'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(
                int(currentWindow['new_map'])))
            refresh_heroes = '' if currentWindow['refresh_heroes'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S',
                                                                                           time.localtime(int(
                                                                                               currentWindow[
                                                                                                   'refresh_heroes'])))
            send_screenshot = '' if currentWindow['send_screenshot'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S',
                                                                                             time.localtime(int(
                                                                                                 currentWindow[
                                                                                                     'send_screenshot'])))
            refresh_page = '' if currentWindow['refresh_page'] == 0 else time.strftime('%d/%m/%Y %H:%M:%S',
                                                                                       time.localtime(int(currentWindow[
                                                                                                              'refresh_page'])))
            texto = f'''
        window: {title}
        login: {login}
        heroes: {heroes}
        balance: {balance}
        new_map: {new_map}
        refresh_heroes: {refresh_heroes}
        send_screenshot: {send_screenshot}
        refresh_page: {refresh_page}
      '''

            self.telegram.telsendtext(texto, self.activeaccount)

    def get_profile_label(self):
        if self.activeaccount in self.accountLabels:
            return self.accountLabels[self.activeaccount]
        else:
            return self.defaultProfileLabel

    def start(self):
        print(instruction)
        t = Configuration.c['time_intervals']

        if len(self.windows) >= 1:
            self.accounts = len(self.windows)

            print(f'\n\n>>---> {len(self.windows)} {self.strings.getRegionalizedString(36)}')
            self.telegram.telsendtext(f'🔌 {self.strings.getRegionalizedString(37)} {len(self.windows)} '
                                      f'{self.strings.getRegionalizedString(38)} \n\n 💰 '
                                      f'{self.strings.getRegionalizedString(39)}', 0)

            while True:
                for currentWindow in self.windows:
                    time.sleep(2)
                    now = time.time()
                    self.defaultProfileLabel = currentWindow['window'].title
                    currentWindow['window'].activate()
                    if not currentWindow['window'].isMaximized:
                        currentWindow['window'].maximize()

                    print(f'\n\n>>---> {self.strings.getRegionalizedString(40)} {currentWindow["window"].title}')

                    if self.activeaccount == self.accounts:
                        self.activeaccount = 1
                    else:
                        self.activeaccount = self.activeaccount + 1

                    if now - currentWindow['login'] > self.add_randomness(t['check_login_and_refresh_heroes'] * 60):
                        currentWindow['login'] = now
                        self.login()

                    if now - currentWindow['heroes'] > self.add_randomness(t['send_heroes_for_work'] * 60):
                        currentWindow['heroes'] = now
                        self.search_for_workable_heroes()

                    if now - currentWindow['new_map'] > t['check_for_new_map_button']:
                        currentWindow['new_map'] = now
                        currentWindow['maps'].append(now)

                        if ScreenControls.clickbtn(self.images['new-map']):
                            self.telegram.telsendtext(f'{self.strings.getRegionalizedString(41)} {self.get_profile_label()}',
                                                      self.activeaccount)
                            loggerMapClicked()
                            time.sleep(3)
                            num_jaulas = len(ScreenControls.positions(self.images['jail'], threshold=0.8))
                            if num_jaulas > 0:
                                self.telegram.telsendtext(
                                    f'{self.strings.getRegionalizedString(42)} {num_jaulas} {self.strings.getRegionalizedString(43)}'
                                    f' {self.get_profile_label()}', self.activeaccount)

                    if now - currentWindow['refresh_heroes'] > self.add_randomness(t['check_login_and_refresh_heroes'] * 60):
                        currentWindow['refresh_heroes'] = now
                        time.sleep(4)
                        self.refresh_heroes_positions()

                    if now - currentWindow['balance'] > self.add_randomness(t['get_balance'] * 60):
                        currentWindow['balance'] = now
                        self.go_balance(False, currentWindow['window'].title)

                    if now - currentWindow['send_screenshot'] > self.add_randomness(t['send_screenshot'] * 60):
                        currentWindow['send_screenshot'] = now
                        self.send_screenshot(False)

                    logger(None, progress_indicator=True)

                    sys.stdout.flush()

                    if not now - currentWindow['login']:
                        self.disconnect()

        else:
            print(self.strings.getRegionalizedString(44))
