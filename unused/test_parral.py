import threading
import time
import inspect
import requests


class UpdateKeywordsThread(threading.Thread):
    idx = 0
    json_url = 'https://jsonplaceholder.typicode.com/todos/'
    keywords = {}

    def __init__(self):
        self.lock = threading.Lock()
        threading.Thread.__init__(
            self, target=self.update_token_keywords_wrapper)
        self.start()

    def update_token_keywords_wrapper(self):
        while True:
            # print('wrapper')
            self.update_token_keywords()

    def update_token_keywords(self):
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        # print(f"Inside {caller}")
        # print("Acquiring lock")
        self.idx += 1
        with self.lock:
            # print("Lock Acquired")
            r = requests.get(self.json_url + str(self.idx))
            self.keywords = r.json()
            print(self.keywords)
            time.sleep(7)


if __name__ == '__main__':
    hello = UpdateKeywordsThread()
    print(1)
    while True:
        time.sleep(1)
        print(hello.keywords)
