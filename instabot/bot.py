import pandas as pd
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from time import sleep, time
from random import randint, shuffle
import os
from functools import wraps


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
print(PROJECT_ROOT)
# chromedriver executable should be stored in PROJECT_ROOT
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")


def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time()))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time())) - start
            print(f"Total execution time of {func}: {end_ / 60 if end_ > 0 else 0} minutes")
    return _time_it


class Bot:

    LOGIN_PAGE = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
    TAGS_PAGE = 'https://www.instagram.com/explore/tags/'

    MAIN_XPATH = '/html/body/div[2]/'

    def __init__(self, username, password, chromedriver_path=None, hashtags_list_path=None):

        self.username = username
        self.password = password
        self.MY_PAGE = f'https://www.instagram.com/{self.username}/'

        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        # self.browserProfile.headless = True

        chromedriver_path = chromedriver_path or DRIVER_BIN
        self.browser = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=self.browserProfile)

        hashtags_list_path = hashtags_list_path or 'hashtag.csv'
        self.hashtag_list = list(pd.read_csv(hashtags_list_path, delimiter=',')['hashtags'].values)
        self.followers_list = []

        self.followed = []
        self.liked = 0
        self.visited_tags = 0

    def open(self, site, loaded_tag):
        self.browser.get(site)
        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, loaded_tag))
            )
        except TimeoutException:
            print(f'Timeout while waiting for {loaded_tag} in {site}')

    def log_in(self):
        login_button_locator = "//button[@type='submit' and contains(., 'Log in')]"
        self.open(self.LOGIN_PAGE, login_button_locator)

        inputs = self.browser.find_elements_by_css_selector('input')
        login_button = self.browser.find_element_by_xpath(login_button_locator)

        username_input = inputs[0]
        password_input = inputs[1]

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        login_button.click()
        self.short_sleep()

        try:
            not_now_button = self.browser.find_element_by_xpath("//button[contains(., 'Not Now')]")
            not_now_button.click()
        except NoSuchElementException:
            pass

    @measure
    def iterate_over_hashtags(self, hashtags, pics, follow):
        shuffle(self.hashtag_list)
        for hashtag in tqdm(self.hashtag_list[:hashtags]):
            self.open(self.TAGS_PAGE + hashtag + '/', "//h1[contains(., {})]".format(hashtag))
            self.visited_tags += 1
            self.click_first_image()
            for i in tqdm(range(pics)):
                try:
                    self.iterate_over_images(follow)
                except Exception as e:
                    print(type(e), e)
                    break

    def iterate_over_images(self, follow):
        image_popup_xpath = self.MAIN_XPATH + 'div[2]/div/article/header/div[2]/div[1]/'
        username_xpath = image_popup_xpath + "div[1]/h2/a"
        follow_button_xpath = image_popup_xpath + "div[2]/button"

        self.wait_until_visible(username_xpath)
        username = self.browser.find_element_by_xpath(username_xpath).get_attribute('title')

        if follow:
            follow_button = self.browser.find_element_by_xpath(follow_button_xpath)
            to_follow = True if follow_button.text == 'Follow' else False

            if to_follow and username not in self.followed and username not in self.followers_list:
                self.follow(follow_button, username)

        self.like()

        # Next picture
        self.browser.find_element_by_link_text('Next').click()
        self.short_sleep()

    def create_followers_list(self):
        followers_button_xpath = f"//a[@href='/{self.username}/followers/']"
        followers_popup_xpath = self.MAIN_XPATH + 'div/div[2]'
        followers_xpath = followers_popup_xpath + '/ul/div/li'
        follower_name_xpath = './div/div[1]/div[2]/div[1]/a'

        self.open(self.MY_PAGE, followers_button_xpath)

        followers_button = self.browser.find_element_by_xpath(followers_button_xpath)
        followers_number = int(followers_button.find_element_by_css_selector('span').get_attribute('title'))

        followers_button.click()
        self.short_sleep()
        self.exhaust_infinite_scroll_in_popup(followers_popup_xpath, followers_xpath)

        followers = self.browser.find_elements_by_xpath(followers_xpath)
        followers_names = [
            follower.find_element_by_xpath(follower_name_xpath).get_attribute('title') for follower in followers
        ]
        self.followers_list = followers_names

        # assert that followers list was properly parsed
        assert followers_number > 0


    def click_first_image(self):
        first_image_xpath = '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]'
        first_image = self.browser.find_element_by_xpath(first_image_xpath)
        first_image.click()
        self.short_sleep()

    def like(self):
        like_xpath = "//span[contains(@aria-label, 'Like')][contains(@class, 'glyphsSpriteHeart__outline__24__grey_9')]"

        to_like = self.is_visible(like_xpath)
        if to_like:
            like_button = self.browser.find_element_by_xpath(like_xpath)
            like_button.click()
            self.liked += 1
            self.long_sleep()

    def follow(self, follow_button, username):
        follow_button.click()
        self.followed.append(username)
        self.long_sleep()

    @measure
    def clear_followers(self, to_leave):

        following_button_xpath = f"//a[@href='/{self.username}/following/']"
        following_popup_xpath = self.MAIN_XPATH + 'div/div[2]'
        followers_xpath = self.MAIN_XPATH + 'div/div[2]/ul/div/li'

        self.open(self.MY_PAGE, following_button_xpath)

        following_button = self.browser.find_element_by_xpath(following_button_xpath)
        following_button.click()
        self.short_sleep()
        self.exhaust_infinite_scroll_in_popup(following_popup_xpath, followers_xpath)

        followers = self.browser.find_elements_by_xpath(followers_xpath)
        print('len followers: ', len(followers))

        nr_to_unfollow = len(followers) - to_leave
        assert nr_to_unfollow > 0

        print('nr_to_unfollow: ', nr_to_unfollow)
        ids_to_unfollow = list(range(1,len(followers) + 1))
        shuffle(ids_to_unfollow)
        ids_to_unfollow = ids_to_unfollow[:nr_to_unfollow]

        unfollowed = 0
        for follower_id in tqdm(ids_to_unfollow):

            unfollow_button_xpath = f'{followers_xpath}[{follower_id}]/div/div[2]/button'
            unfollow_button = self.browser.find_element_by_xpath(unfollow_button_xpath)

            if unfollow_button.text == 'Following':

                unfollow_button.click()
                self.short_sleep()

                unfollow_confirm_button = self.browser.find_element_by_xpath("//button[contains(text(), 'Unfollow')]")
                unfollow_confirm_button.click()
                self.short_sleep()
                unfollowed += 1

        print(f'Unfollowed {unfollowed} users')

    @measure
    def exhaust_infinite_scroll_in_popup(self, popup_xpath, followers_xpath):
        following_popup = self.browser.find_element_by_xpath(popup_xpath)

        # do slow scrolling to get rid of 'suggested' link, which is blocking infinite scrolling
        for x in reversed(range(1, 10)):
            self.browser.execute_script(f"arguments[0].scrollTop = arguments[0].scrollHeight/{x}", following_popup)
            self.short_sleep()

        # exhaust infinite scrolling to load all followers
        while True:
            last_elem = self.browser.find_elements_by_xpath(followers_xpath)[-1]
            self.scroll_to_bottom(following_popup)
            self.short_sleep()
            new_last_elem = self.browser.find_elements_by_xpath(followers_xpath)[-1]
            if last_elem == new_last_elem:
                self.scroll_to_bottom(following_popup)
                self.super_long_sleep()
                self.scroll_to_bottom(following_popup)
                self.long_sleep()
                new_last_elem = self.browser.find_elements_by_xpath(followers_xpath)[-1]
                if last_elem == new_last_elem:
                    break

    def summary(self):
        print(f'Visited {self.visited_tags} tags')
        print(f'Followed {len(self.followed)} users: ')
        print(f'Liked {self.liked} pictures')

    def wait_until_visible(self, xpath):
        try:
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except TimeoutException:
            print(f'Timeout while waiting for {xpath}')

    def is_visible(self, xpath):
        try:
            element = self.browser.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return element.is_displayed()

    def super_short_sleep(self):
        sleep(1)

    def short_sleep(self):
        sleep(randint(3, 6))

    def long_sleep(self):
        sleep(randint(15, 20))

    def super_long_sleep(self):
        sleep(randint(45, 60))

    def scroll_to_bottom(self, element):
        self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
        self.short_sleep()

    def quit(self):
        self.browser.quit()
