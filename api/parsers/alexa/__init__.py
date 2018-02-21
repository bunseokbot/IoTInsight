"""Alexa echo cloud service parser."""
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from parsers.log import log

import json
import time
import os
import re


class Alexa(object):
    """Alexa cloud server API."""

    def __init__(self):
        """Construct Alexa API."""
        self._log = log()
        self.isLogined = False

        self._log.info("Starting Alexa cloud service parser...")

        self.login()

    def login(self):
        """Login to alexa amazon server."""
        path = os.path.join('bin', 'chromedriver.exe')
        self.driver = webdriver.Chrome(path)

        self.driver.implicitly_wait(2)

        self._log.info("Starting chromedriver browser")

        self.driver.get('https://alexa.amazon.com')

        while True:
            # check to login successfully and redirect info main page.
            if "Sign out" in self.driver.page_source:
                self._log.info("Success to login Alexa cloud")
                self.isLogined = True
                break
            else:
                self._log.debug("Login check failed.. waiting 3 seconds")
                time.sleep(3)

        self.driver.set_window_position(-3000, 0)

    def to_json(self, data):
        """Convert html to json."""
        return json.loads(re.findall(r'<pre style=.*?>({.*?})</pre>', data)[0])

    def get_data(self, url):
        """Get data from request url."""
        self._log.debug("Alexa API request: {}".format(url))
        self.driver.get(url)
        try:
            return self.to_json(self.driver.page_source)
        except:
            return self.driver.page_source

    def __del__(self):
        """Class Destructor."""
        self._log.info("Finishing Alexa cloud service parser...")
        self.driver.quit()
        del self
