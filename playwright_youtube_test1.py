import random

from playwright.sync_api import sync_playwright
import time
import argparse

from trio import sleep


def yot(HAR_name):
    with (sync_playwright() as p):
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        browser = p.chromium.launch(channel="chrome",
                                    headless=False,
                                    args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(
            user_agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
            java_script_enabled=True,
            viewport={"width": 1280, "height": 720},
            device_scale_factor= 1,
            record_har_path=HAR_name
        )
        page = context.new_page()
        page.goto("https://www.youtube.com/watch?v=cO997sPYZ9U",wait_until="load")
        st_time = time.time()

        setting = page.locator(".ytp-settings-button")
        setting.hover()
        setting.click()
        Q = page.get_by_text("Quality").nth(0)
        Q.hover()
        Q.click()
        Q7 = page.get_by_text("1080p")
        Q7.hover()
        Q7.click()
        while time.time() - st_time < 70:
            play=page.locator("button[class='ytp-play-button ytp-button']")
            if play.get_attribute("data-title-no-tooltip")=="Play":
                play.hover()
                play.click()
                time.sleep(0.1)

            box = page.locator("button[class='ytp-play-button ytp-button']").bounding_box()
            page.mouse.move(
                box["x"] + box["width"] / 2+random.randint(0, 2),
                box["y"] + box["height"] / 2+random.randint(1, 2),
                steps=10
            )
            print(page.locator("div[class='ytp-progress-bar']").get_attribute("aria-valuetext"))
            time.sleep(5)

        print(page.title())
        page.close()
        context.close()
        browser.close()

def wiki(HAR_name):
    with sync_playwright() as p:
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        browser = p.chromium.launch(channel="chrome",
                                    headless=False,
                                    args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(
            user_agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
            java_script_enabled=True,
            viewport={"width": 1280, "height": 720},
            device_scale_factor= 1,
            record_har_path=HAR_name
        )
        page = context.new_page()
        page.goto("https://www.wikipedia.org/",wait_until="networkidle")
        #time.sleep(3)
        srch=page.locator("input[name='search']")
        srch.fill("Machine learning")
        srch.press("Enter")
        time.sleep(2)
        link = page.locator("a[title='Artificial intelligence']").nth(5)
        link.scroll_into_view_if_needed()
        link.click()
        time.sleep(2)

        print(page.title())
        page.close()
        context.close()
        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_name', required=True, )
    args = parser.parse_args()
    yot(args.output_name)
    #wiki(args.output_name)