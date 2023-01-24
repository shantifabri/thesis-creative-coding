import time
import os
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

SKETCKES_PER_ROW = 12
NUM_ROWS = 10
VISIBLE_SKETCKES = SKETCKES_PER_ROW * NUM_ROWS

AMOUNT = 5000

ITERS = int(AMOUNT / VISIBLE_SKETCKES) + 1


def write_csv(set_links, file_name):
    df = pd.DataFrame(set_links)

    if not os.path.exists('links'):
        os.makedirs('links')

    df.to_csv(file_name)


def collect_links():
    array_links = set()

    wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "sketchThumbContainer")))

    # show more
    for i in range(ITERS):
        element = wait.until(EC.element_to_be_clickable((By.ID, 'showMoreButton')))
        element.click()

    links = driver.find_elements(By.CLASS_NAME, "sketchThumbContainer")

    for link in links:
        try:
            l_actual = link.get_attribute('href')
            if l_actual not in array_links:
                array_links.add(l_actual)
        except:
            print(f'Error en collect_links {link}')

    print(f"Numero de links: {len(array_links)}")
    write_csv(array_links, "./links/all_links.csv")


if __name__ == '__main__':
    start_time = time.time()

    options = Options()
    # options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    driver.get("https://openprocessing.org/browse/?time=anytime&type=all&q=#")

    print(f'Title: {driver.title}')
    assert "Browse Sketches - OpenProcessing" in driver.title

    wait = WebDriverWait(driver, 10)

    # accept cookies
    element = wait.until(EC.visibility_of_element_located((By.ID, 'ccc-notify-accept')))
    element.click()

    # collect_links()

    print("--- %s seconds ---" % (time.time() - start_time))


    # Abre el sketch
    # driver.get('https://openprocessing.org/sketch/1797657')

    # element = driver.find_elements(By.CLASS_NAME, "metricGroup")
    # element.click()
    # print(element)
    # a = driver.find_elements(By.CLASS_NAME, "icon_share white").click()
    # b = driver.find_elements_by_class_name("icon icon_share white").click()
