import threading
import time
import inspect
import requests


class UpdateKeywordsThread(threading.Thread):
    idx = 0
    tokens = []
    cancel = False

    def __init__(self, interval_sec, json_url):
        self.json_url = json_url
        self.interval_sec = interval_sec
        self.lock = threading.Lock()
        threading.Thread.__init__(
            self, target=self.update_token_keywords_wrapper)

    def update_token_keywords_wrapper(self):
        while not(self.cancel):
            # print('wrapper')
            self.update_token_keywords()

    def update_token_keywords(self):
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        # print(f"Inside {caller}")
        # print("Acquiring lock")
        self.idx += 1
        with self.lock:
            # print("Lock Acquired")
            r = requests.get(self.json_url)
            data = r.json()
            self.tokens = data["keywords"]

            self.tokens.append('franges')
            self.tokens.append('Santi i la Marta')
            self.tokens.append('1962')
            self.tokens.append('250.000')

            print(self.tokens)
            time.sleep(self.interval_sec)

    def stop(self):
        self.cancel = True
# if __name__ == '__main__':
#     hello = UpdateKeywordsThread()
#     print(1)
#     while True:
#         time.sleep(1)
#         print(hello.keywords)