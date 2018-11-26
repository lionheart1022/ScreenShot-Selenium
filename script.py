from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
import traceback
import tempfile
import os
import time

DEBUG_MODE = False


def _get_js_body_height(driver):
    scroll = driver.execute_script('return document.body.scrollHeight;')
    window_outer = driver.execute_script('return window.outerHeight;')
    window_inner = driver.execute_script('return window.innerHeight;')
    height = scroll + window_outer - window_inner
    print("Detected JS page height: %s" % height)
    return height


def make_screenshot(driver, output_name):
    _body_height = _get_js_body_height(driver)
    if _body_height and _body_height > 105:
        try:
            driver.set_window_size(1024, 800)
        except Exception as e:
            print('Error while trying to maximize the browser: %s' % e)

    time.sleep(30)
    driver.save_screenshot(output_name)

    if not DEBUG_MODE:
        driver.quit()


def _init_chromium():
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()  # this is for Chromium
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--window-size=%s" % '{},{}'.format(1024, 800))
    executable_path = '/usr/sbin/chromedriver'
    if not os.path.exists(executable_path):
        executable_path = '/usr/local/bin/chromedriver'
    # initialize webdriver, open the page and make a screenshot
    driver = webdriver.Chrome(chrome_options=chrome_options,
                              executable_path=executable_path
                              )
    print('Webdriver version: {}'.format(driver.capabilities))
    return driver


if __name__ == "__main__":
    driver = _init_chromium()

    if driver:
        try:
            driver.get('https://google.com')
            time.sleep(5)

            input_keyword_text = driver.find_elements_by_xpath('//div[@class="SDkEP"]//input')[0]
            input_keyword_text.send_keys('abc')
            input_keyword_text.send_keys(Keys.ENTER)

            search_results = driver.find_elements_by_xpath('//div[@id="search"]//cite')
            ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

            for search_result in search_results:
                try:
                    driver = _init_chromium()
                    driver.get(search_result.text)
                    WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
                        EC.presence_of_element_located((By.TAG_NAME, "html"))
                    )

                    t_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    t_file.close()

                    make_screenshot(driver, t_file.name)
                    print("Made screenshot for %s" % t_file.name)
                    driver.quit()

                except:
                    print('Found no product links: {}'.format(traceback.format_exc()))
        except:
            print('Found no product links: {}'.format(traceback.format_exc()))

        if 'driver' in locals():
            driver.quit()
