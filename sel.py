import msvcrt
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib.parse import urlparse


options = Options()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

#options.add_argument("--headless=new") # Modern argument for Chrome 109+
options.add_argument("--Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service,options=options)

driver.execute_cdp_cmd("Network.enable", {})

driver.get("https://www.youtube.com/watch?v=eFeDpUVEy48")
time.sleep(6)

play_button = driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button")
play_button.click()

while True:

    if msvcrt.kbhit():
        key = msvcrt.getch().decode("utf-8").lower()
        if key == 'c':
            driver.quit()
    for entry in driver.get_log('performance'):
        msg = json.loads(entry["message"])["message"]

        if msg["method"] == "Network.responseReceived":
            response = msg["params"]["response"]
            url = response["url"]

            if "googlevideo.com/videoplayback" in url:
                print("STATUS:", response["status"])
                print("REMOTE:", response.get("remoteIPAddress"))
                print("URL:", url)


