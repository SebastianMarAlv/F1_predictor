from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cookie_parser import parse_all
from time import sleep


class F1Scrapper:
    url = 'https://f1.tfeed.net/'

    def __init__(self):
        self.f_driver = webdriver.Firefox()
        self.f_driver.get(F1Scrapper.url)
        self.original_window = self.f_driver.current_window_handle
        self.__title_block = self.__get_title_block()

    def __load_google_cookies(self):
        self.f_driver.delete_all_cookies()
        cookies = parse_all()

        def insert_c(site: str):
            for cookie in cookies:
                try:
                    self.f_driver.add_cookie(cookie)
                except Exception as e:
                    print(cookie)
                    self.f_driver.close()
                    raise e
        insert_c('https://accounts.google.com')
        self.f_driver.get('https://google.com')
        sleep(4)
        insert_c('https://google.com')
        sleep(1)
        self.f_driver.refresh()

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
        sleep(6)
        self.__load_google_cookies()
        print('cookies_loaded')
        # text_input = self.__wait(
        #     self.f_driver,
        #     lambda d: d.find_element(By.TAG_NAME, 'input')
        # )
        # ActionChains(self.f_driver)\
        #     .send_keys_to_element(text_input, "elsiu")\
        #     .perform()

    def __wait(self, _element, function, time=10):
        try:
            result = WebDriverWait(_element, timeout=time).until(function)
            return result
        except Exception as e:
            self.f_driver.close()
            raise e

    def __get_title_block(self):
        return self.__wait(
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
        spans = self.__wait(
            self.__title_block,
            lambda d:
            d.find_element(By.ID, 'sel_season_tb')
            .find_elements(By.TAG_NAME, 'span')
        )
        links = list(map(lambda span: self.__wait(span, lambda s: s.find_element(By.TAG_NAME, 'a')), spans))
        return links

    def run(self):
        season_list = scrapper.__get_season_list()
        race_list_block = scrapper.__get_race_list()

        link = season_list[0]
        link.click()
        self.__wait(self.__title_block, EC.visibility_of(race_list_block))
        races_links = race_list_block.find_elements(By.TAG_NAME, 'a')
        races_links[0].click()


scrapper = F1Scrapper()
scrapper.login()
