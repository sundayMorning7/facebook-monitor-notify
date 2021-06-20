import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options

from update_keywords_thread import UpdateKeywordsThread
from mail_service import MailService

# from boto.s3.connection import S3Connection
# s3 = S3Connection(os.environ['S3_KEY'], os.environ['S3_SECRET'])


class MonitorFacebook():
    facebook_login_url = 'https://www.facebook.com/login/device-based/regular/login/?login_attempt=1'

    facebook_login = "mmarikgod@gmail.com"
    facebook_pass = "pcMsygex84GTo9kpH"

    def __init__(self, group_monitoring_url, search_tokens_url):
        self.mail_service = MailService()
        self.monitor_group_url = group_monitoring_url
        seconds = 60
        self.keywords_update_job = UpdateKeywordsThread(
            5 * seconds, search_tokens_url)

    def format_html_and_highlight_tokens(self, text, highlight_options):
        highlight_options.sort(key=lambda x: x[1])

        result = ""
        p1 = 0
        for token, token_start, token_length in highlight_options:
            token_end = token_start + token_length
            start_str = text[p1: token_start]
            formatted = f'<span style="background-color: yellow;">{text[token_start: token_end]}</span>'
            result += start_str + formatted
            p1 = token_end
        result += text[p1:]
        print('--FORMATTED')
        print(result)
        return f"""\
        <html>
        <body>
            <p>Hey!,<br>
            <a href="{self.monitor_group_url}">Group link.</a>
            </p>
            <p>{result}<p>
        </body>
        </html>
        """

    def search_tokens(self, text):
        result = []
        for t in self.keywords_update_job.tokens:
            idx = text.find(t)
            if idx != -1:
                result.append((t, idx, len(t)))  # enty starts, and it's length
        result.sort(key=lambda x: x[1])
        return result

    def process_article(self, article: WebElement, idx):
        """Checks whether there's a match in article's text with tokens. If yes, then send an email.

        Args:
            text (str): [article's text]
        """
        text = self.extract_message(article)
        if text == None:
            print("TEXT IS NONE!!!!!!!!!!!" + '-'*20, "ARTICLE: ", idx)
            return
        found_tokens = self.search_tokens(text)
        if len(found_tokens):
            print(found_tokens)

            message = self.format_html_and_highlight_tokens(
                text, found_tokens)
            tokens_str = ", ".join([t[0] for t in found_tokens])
            print('emailing')
            self.mail_service.send_emails(text, message, tokens_str)

    def extract_message(self, article: WebElement):
        try:
            message = article.find_element_by_xpath(
                './/div[@data-ad-comet-preview="message"]')
            try:
                message_more = message.find_element_by_xpath(
                    './/div[@role="button"]')
                message_more.click()
            except NoSuchElementException:
                pass

            return message.text
        except NoSuchElementException:
            pass

    def init_driver(self):
        op = Options()

        # chrome_prefs = {}
        # op.experimental_options["prefs"] = chrome_prefs
        # op.add_experimental_option("prefs", {
        #     "profile.default_content_setting_values.notifications": 1,
        #     "profile.managed_default_content_settings.images": 2,
        #     "profile.default_content_settings.images": 2
        # })
        op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        op.add_argument("--headless")
        # op.add_argument('--disable-dev-shm-usage')
        # op.add_argument('--disable-gpu')
        # op.add_argument("--no-sandbox")
        # op.add_argument("--disable-dev-sh-usage")
        # op.add_argument("--remote-debugging-port=9222")

        # executable_path="chromedriver.exe"
        # import pprint
        # pprint.pprint(dict(os.environ), width=1)
        # exit(1)
        self.driver = webdriver.Chrome(
            executable_path=os.environ.get("CHROME_DRIVER_PATH"), options=op)
        self.driver.set_window_size(1920, 1080)

    def login_and_go_to_monitoring_page(self):
        self.driver.get(self.facebook_login_url)

        emailField = self.driver.find_element(
            By.ID, 'email')
        emailField.send_keys(self.facebook_login)

        passwordField = self.driver.find_element(
            By.ID, 'pass')
        passwordField.send_keys(self.facebook_pass)

        loginBtn = self.driver.find_element(
            By.ID, 'loginbutton')
        loginBtn.click()

        time.sleep(3)
        self.driver.get(self.monitor_group_url)

    def start(self):
        self.keywords_update_job.start()
        self.init_driver()
        self.login_and_go_to_monitoring_page()
        # banner = self.driver.find_element_by_id('pagelet_growth_expanding_cta')
        # .set_attribute('display': 'none')
        # self.driver.execute_script(
        #     "arguments[0].style.display = 'none';", banner)
        while True:
            time.sleep(5)

            # for i in range(2):  # 15 for 64 articles
            #     self.driver.execute_script(
            #         f"window.scrollTo(0, document.body.scrollHeight);")
            #     time.sleep(2)

            # find all articles on a page, except comments. if articles has an ancestor of article, then it's a comment
            articles = self.driver.find_elements_by_xpath(
                '//div[@role="feed"]//div[@role="article" and not(ancestor::div[@role="article"])]')
            print("Found articles: " + str(len(articles)))
            for idx, article in enumerate(articles[:3]):
                # print(self.keywords_update_job.tokens)
                print(article.location['y'])
                self.driver.execute_script(
                    f"window.scrollTo(0, {article.location['y']} - 30);")
                time.sleep(3)

                self.process_article(article, idx)

            self.driver.refresh()
            time.sleep(5)

        self.keywords_update_job.stop()
        self.driver.close()


def main():
    monitor = MonitorFacebook("https://www.facebook.com/salutcat/",
                              'https://raw.githubusercontent.com/ljharb/json-file-plus/main/package.json')
    monitor.start()


if __name__ == "__main__":
    main()
