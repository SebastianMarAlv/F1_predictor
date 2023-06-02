from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


class F1Scrapper:
    url = 'https://f1.tfeed.net/'

    def __init__(self):
        self.f_driver = webdriver.Firefox()
        self.f_driver.get(F1Scrapper.url)
        self.f_driver.maximize_window()
        self.original_window = self.f_driver.current_window_handle
        self.__title_block = None
        self.__link_list = None

    def login(self):
        google_login_btt = self.__wait(
            self.f_driver,
            lambda d: d.find_element(By.CLASS_NAME, 'ulogin-button-google')
        )
        google_login_btt.click()
        self.__wait(
            self.f_driver,
            EC.number_of_windows_to_be(2)
        )
        for window_handle in self.f_driver.window_handles:
            if window_handle != self.original_window:
                self.f_driver.switch_to.window(window_handle)
                break
        sleep(3)
        text_input = self.__wait(
            self.f_driver,
            lambda d: d.find_element(By.TAG_NAME, 'input')
        )

        ActionChains(self.f_driver)\
            .send_keys_to_element(text_input, "a01632483@tec.mx")\
            .perform()

        possible_buttons = self.__wait(
            self.f_driver,
            lambda d: d.find_elements(By.TAG_NAME, 'button')
        )

        for button in possible_buttons:
            if button.text == 'Siguiente':
                real_button = button
                real_button.click()
                break
        sleep(3)
        #tec login
        user_input = self.__wait(
            self.f_driver,
            lambda d: d.find_element(By.ID, 'Ecom_User_ID'),
            60
        )
        ActionChains(self.f_driver) \
            .send_keys_to_element(user_input, "a01632483") \
            .perform()
        pass_input = self.__wait(
            self.f_driver,
            lambda d: d.find_element(By.ID, 'Ecom_Password')
        )
        ActionChains(self.f_driver) \
            .send_keys_to_element(pass_input, "K7MggqtPbFpA'nX|") \
            .perform()
        self.__wait(
            self.f_driver,
            lambda d: d.find_element(By.ID, 'submitButton')
        ).click()

        sleep(3)
        self.f_driver.switch_to.window(self.original_window)
        sleep(1)

    def __wait(self, _element, function, time=10):
        try:
            result = WebDriverWait(_element, timeout=time).until(function)
            return result
        except Exception as e:
            self.f_driver.close()
            raise e

    def __get_title_block(self):
        self.__title_block = self.__wait(
            self.f_driver,
            lambda d:
            d.find_element(By.ID, 'title_holder')
            .find_element(By.ID, 'title_block')
        )

    def __get_race_list(self):
        return self.__wait(
            self.__title_block,
            lambda d: d.find_element(By.ID, 'sel_session_tb')
        )

    def __get_season_list(self):
        links = self.__wait(
            self.__title_block,
            lambda d:
            d.find_element(By.ID, 'sel_season_tb')
            .find_elements(By.TAG_NAME, 'span')
        )
        return links

    def __get_link_list(self):
        link_list = {}
        useful_cities_2011 = ['Singapore', 'Korea', 'India', 'Abu-Dhabi', 'Brazil']
        self.__get_title_block()
        season_list = self.__get_season_list()
        race_list_block = self.__get_race_list()
        num_seasons = len(season_list)
        for i in range(num_seasons):
            self.__get_title_block()
            season_list = self.__get_season_list()
            race_list_block = self.__get_race_list()
            span = season_list[i]
            sleep(0.5)
            link = self.__wait(span, lambda s: s.find_element(By.TAG_NAME, 'a'))
            link_year = int(link.text)
            if link_year < 2011:
                continue
            link_list[link_year] = {}
            link.click()
            self.__wait(self.__title_block, EC.visibility_of(race_list_block))
            ActionChains(self.f_driver) \
                .move_to_element(race_list_block) \
                .perform()
            races_links = race_list_block.find_elements(By.TAG_NAME, 'a')
            for race in races_links:
                race_name = race.text
                if link_year == 2011 and race_name not in useful_cities_2011:
                    continue
                link_list[link_year][race_name] = False
        self.__link_list = link_list


    def run(self):
        if self.__link_list is None:
            self.__get_link_list()
        # while () {
        #
        # }
        # self.__get_title_block()
        # useful_cities_2011 = ['Singapore', 'Korea', 'India', 'Abu-Dhabi', 'Brazil']
        # season_list = self.__get_season_list()
        # race_list_block = self.__get_race_list()
        #
        #
        #
        #     race.click()
        #     self.__position_to_lap()

    def __position_to_lap(self):
        # at singapore 2011 laps are enabled
        select_ele = self.__wait(
            self.f_driver,
            lambda d: d.find_element(By.ID, 'replay_laps_select')
        )
        select = Select(select_ele)
        for opt in select.options:
            if int(opt.text) < 3:
                continue
            opt.click()
            sleep(0.5)
            self.__get_current_lap_info()

    def __get_current_lap_info(self):
        elements = [
            'pos',
            'nick',
            'gap'
        ]
        for i in range(1, 21):
            print(f'getting: stats_d_{0 if i < 10 else ""}{i}')
            print(f'Driver i: {i}')
            for element in elements:
                val = self.__wait(
                    self.f_driver,
                    lambda d: d.find_element(By.ID, f'i_{0 if i < 10 else ""}{i}_{element}')
                ).text
                print(f"\t{element}: {val}")


scrapper = F1Scrapper()
scrapper.login()
sleep(1)
scrapper.run()
