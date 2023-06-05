from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from time import sleep
from os.path import exists

class F1Scrapper:
    url = 'https://f1.tfeed.net/'

    def __init__(self):
        self.f_driver = webdriver.Firefox()
        self.f_driver.get(F1Scrapper.url)
        self.original_window = self.f_driver.current_window_handle
        self.__link_list = None

        self.f_driver.maximize_window()

    def __wait(self, function, time=10):
        try:
            result = WebDriverWait(self.f_driver, timeout=time).until(function)
            return result
        except Exception as e:
            self.f_driver.close()
            raise e

    def __find_and_click_google_button(self):
        google_login_btt = self.__wait(lambda d: d.find_element(By.CLASS_NAME, 'ulogin-button-google'))
        google_login_btt.click()
        self.__wait(EC.number_of_windows_to_be(2))

    def __change_to_new_window(self):
        i = 0
        while self.f_driver.window_handles[i] == self.original_window:
            i += 1
        self.f_driver.switch_to.window(self.f_driver.window_handles[i])

    def __login_to_google(self):
        # Wait a little longer so the page can end loading
        text_input = self.__wait(lambda d: d.find_element(By.TAG_NAME, 'input'), 20)
        ActionChains(self.f_driver) \
            .send_keys_to_element(text_input, "a01632483@tec.mx") \
            .perform()
        possible_buttons = self.__wait(lambda d: d.find_elements(By.TAG_NAME, 'button'))
        i = 0
        while possible_buttons[i].text != 'Siguiente':
            i += 1
        possible_buttons[i].click()

    def __login_to_itesm(self):
        # The Google login may ask for solving a captcha in the previous step
        # If captcha loads in, it has to be solved by hand, extra time for that
        user_input = self.__wait(lambda d: d.find_element(By.ID, 'Ecom_User_ID'), 60)
        pass_input = self.__wait(lambda d: d.find_element(By.ID, 'Ecom_Password'))
        submit_button = self.__wait(lambda d: d.find_element(By.ID, 'submitButton'))
        sleep(0.5)
        ActionChains(self.f_driver) \
            .send_keys_to_element(user_input, "a01632483") \
            .send_keys_to_element(pass_input, "K7MggqtPbFpA'nX|") \
            .perform()
        submit_button.click()

    def login(self):
        self.__find_and_click_google_button()
        self.__change_to_new_window()
        self.__login_to_google()
        self.__login_to_itesm()

        sleep(3)
        self.f_driver.switch_to.window(self.original_window)
        sleep(1)

    def __get_race_list(self):
        return self.__wait(lambda d: d.find_element(By.ID, 'sel_session_tb'))

    def __get_season_list(self):
        season_driver = self.__wait(lambda d: d.find_element(By.ID, 'sel_season_tb'))
        return WebDriverWait(season_driver, timeout=20).until(lambda d: d.find_elements(By.TAG_NAME, 'a'))

    def __wait_for_visibility(self, _race_list_block):
        self.__wait(EC.visibility_of(_race_list_block))
        ActionChains(self.f_driver) \
            .move_to_element(_race_list_block) \
            .perform()

    def __get_link_list(self):
        useful_cities_2011 = ['Singapore', 'Korea', 'India', 'Abu-Dhabi', 'Brazil']
        link_list = {}

        for i in range(len(self.__get_season_list())):
            link = self.__get_season_list()[i]
            link_year = int(link.text)
            if link_year < 2011:
                continue
            link_list[link_year] = []

            race_list_block = self.__get_race_list()
            link.click()

            self.__wait_for_visibility(race_list_block)

            races_links = WebDriverWait(race_list_block, timeout=10).until(lambda d: d.find_elements(By.TAG_NAME, 'a'))
            for race in races_links:
                race_name = race.text
                if link_year == 2011 and race_name not in useful_cities_2011:
                    continue
                link_list[link_year].append(race_name)
        self.__link_list = link_list

    @staticmethod
    def __find_current_link(_year, _season_list):
        for link in _season_list:
            link_year = int(link.text)
            if _year == link_year:
                return link

    @staticmethod
    def __find_current_race(_race, _races_links):
        for race_link in _races_links:
            race_name = race_link.text
            if race_name == _race:
                return race_link

    def run(self):
        if self.__link_list is None:
            self.__get_link_list()
        self.__link_list: dict[list[str]]
        for year in self.__link_list.keys():
            for race in self.__link_list[year]:
                sleep(2)
                # Get blocks from current DOM
                race_list_block = self.__get_race_list()
                season_list = self.__get_season_list()
                F1Scrapper.__find_current_link(year, season_list).click()

                self.__wait_for_visibility(race_list_block)
                sleep(0.5)
                races_links = WebDriverWait(race_list_block, timeout=10)\
                    .until(lambda d: d.find_elements(By.TAG_NAME, 'a'))
                self.__find_current_race(race, races_links).click()
                # Make sure the page has loaded
                sleep(5)  # For some reason will not work without this
                self.f_driver.refresh()  # Sometimes refresh is needed for correct login
                self.__wait(lambda d: d.find_element(By.ID, 'detailedinfo_block'))

                if not exists(f'data/{year}-{race}.csv'):
                    print(f'Scrapping data/{year}-{race}.csv alredy exists')
                    self.__scrape_race(year, race)
                else:
                    print(f'data/{year}-{race}.csv alredy exists, skipped')

                home_btn = self.__wait(lambda d: d.find_element(By.ID, 'stats_si_home').find_element(By.TAG_NAME, 'a'))
                home_btn.click()
                self.__wait(lambda d: d.find_element(By.ID, 'mname_tb'))
                sleep(1)

    def __get_num_racers(self):
        for i in range(30, 0, -1):
            driver = self.__wait(lambda d: d.find_element(By.ID, f'stats_d_{0 if i < 10 else ""}{i}'))
            if driver.is_displayed():
                return i

    def __scrape_race(self, year, race):
        def check_if_diff_lap(_last_lap):
            return lambda d: d.find_element(By.ID, 'i_01_lap').text != _last_lap

        select_ele = self.__wait(lambda d: d.find_element(By.ID, 'replay_laps_select'))
        select = Select(select_ele)

        race_dt = pd.DataFrame()

        first_lap = True
        last_lap = None
        num_drivers = None
        last_item = select.options[-1]
        for opt in select.options:
            if int(opt.text) < 3 or opt == last_item:
                continue
            print(f'Current lap: {opt.text}')
            opt.click()
            if not first_lap:
                self.__wait(check_if_diff_lap(last_lap), 600)
            else:
                first_lap = False
                stats_ele = self.__wait(lambda d: d.find_element(By.ID, 'stats_d_01'))
                self.__wait(EC.visibility_of(stats_ele), 20)
                num_drivers = self.__get_num_racers()
            lap_dt = self.__get_current_lap_info(num_drivers, int(opt.text))
            race_dt = pd.concat([race_dt, lap_dt])
            last_lap = self.__wait(lambda d: d.find_element(By.ID, 'i_01_lap')).text
        race_dt.to_csv(f'data/{year}-{race}.csv')

    def __get_current_lap_info(self, num_drivers, snap_num):
        elements = ['snap_num', 'pos', 'nick', 'lap', 'gap']
        lap_dt = {}
        for ele in elements:
            lap_dt[ele] = []

        for i in range(1, num_drivers + 1):
            for element in elements:
                if element == 'snap_num':
                    lap_dt[element].append(snap_num)
                else:
                    ele_id = f'i_{0 if i < 10 else ""}{i}_{element}'
                    val = self.__wait(lambda d: d.find_element(By.ID, ele_id)).text
                    lap_dt[element].append(val)
                    # print(f"\t{element}: {val}")
        lap_dt = pd.DataFrame(lap_dt)
        return lap_dt


scrapper = F1Scrapper()
scrapper.login()
scrapper.run()
