from pickle import TRUE
import re
import time
from re import S
import pandas as pd
from typing import List
from itertools import count
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime

import os

array_links = set()

DRIVER_PATH = "/Users/mauricio/Downloads/chromedriver"

DEFAULT_DELAY = 5

SKETCKES_PER_ROW = 12
NUM_ROWS = 10

VISIBLE_SKETCKES = SKETCKES_PER_ROW * NUM_ROWS


def collect_links():
    num_iter_show_more = int(num_results / (VISIBLE_SKETCKES))
    print(f"Numero de clicks en el boton Show More: {num_iter_show_more}")

    # Descomentar para usarlo con todos los sketch
    for x in range(1, num_iter_show_more):
    # for x in range(1, 4):
        wait.until(EC.visibility_of_element_located((By.ID, "showMoreButton")))
        show_more_button = driver.find_element(By.ID, "showMoreButton")
        try:
            show_more_button.click()
        except:
            print(f"Error in expand_all_sketches {show_more_button}")
        print(f"Number of visible sketches: {x * VISIBLE_SKETCKES}")

        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "sketchThumbContainer")))
        time.sleep(DEFAULT_DELAY)

    wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "sketchThumbContainer")))
    time.sleep(DEFAULT_DELAY)

    links = driver.find_elements(By.CLASS_NAME, "sketchThumbContainer")

    for link in links:
        try:
            l = link.get_attribute('href')
            array_links.add(l)
        except:
            print(f"Error en collect_links {link}")

    print(f"Numero de links: {len(array_links)}")

    df = pd.DataFrame(array_links)

    now = datetime.now()
    timestamp = datetime.timestamp(now)

    if not os.path.exists('links'):
        os.makedirs('links')

    df.to_csv("./links/" + str(int(timestamp)) + ".csv")


def download_sketches(links) -> None:
    # Accept cookies
    driver.find_element_by_id("ccc-notify-accept").click()

    for sketch in links:

        # Abre el sketch
        driver.get(sketch)

        a = driver.find_elements_by_class_name("icon_share white").click()
        b = driver.find_elements_by_class_name("icon icon_share white").click()


def create_driver(auto:bool = True):
    if auto:
        return webdriver.Chrome(service=Service(
                ChromeDriverManager().install()), options=options)
    else:
        return webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    


if __name__ == '__main__':
    options = Options()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')

    options.headless = True

    driver = create_driver(auto=False)
    driver.get('https://openprocessing.org/browse/')
    
    wait = WebDriverWait(driver, DEFAULT_DELAY)
    wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "sketchThumbContainer")))

    # Accept cookies
    driver.find_element(By.ID, "ccc-notify-accept").click()

    # NOTE: Moving the following block of code into a separate
    # function does not work. It does not refresh the number
    # of results

    # This timer is needed to be able to update the number of results
    time.sleep(4)
    elements = driver.find_elements(By.NAME, "time")
    
    count: int = 0
    for e in elements:
        # This means that we are in the 'anytime' option
        if count == 2:
            e.click()
            time.sleep(5)
        count += 1
    
    wait.until(EC.visibility_of_element_located(
        (By.ID, "searchResults")))

    amount = driver.find_element(By.ID, "showMoreAmount")
    num_results = int(re.findall('[0-9]+', amount.text)[0])

    print(f"Numero total de sketches: {num_results}")

    collect_links()
    # download_sketches()
