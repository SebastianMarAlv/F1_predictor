from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


class F1Scrapper:
    url = 'https://f1.tfeed.net/'

    def __init__(self):
        self.f_driver = webdriver.Firefox()
        self.f_driver.get(F1Scrapper.url)
        self.original_window = self.f_driver.current_window_handle
        self.__title_block = self.__get_title_block()

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
        user_input = self.__wait(
            self.f_driver,
            lambda d: d.find_element(By.ID, 'Ecom_User_ID')
        )
        ActionChains(self.f_driver) \
            .send_keys_to_element(user_input, "a01632483") \
            .perform()
        sleep(2)
        pass_input = self.__wait(
            self.f_driver,
            lambda d: d.find_element(By.ID, 'Ecom_Password')
        )
        ActionChains(self.f_driver) \
            .send_keys_to_element(pass_input, "") \
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
