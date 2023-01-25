import time
import os
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


def write_csv(data_set, file_name, headers=["link"]):
    df = pd.DataFrame(data_set)

    if not os.path.exists('links'):
        os.makedirs('links')

    df.to_csv(file_name, header=headers)


def load_csv(file_name, headers=None):
    data = pd.read_csv(file_name, names=headers)
    set_links = set(data["link"])
    return set_links


def collect_links(iters, file_name):
    driver.get("https://openprocessing.org/browse/?time=anytime&type=all&q=#")
    assert "Browse Sketches - OpenProcessing" in driver.title

    array_links = set()

    wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "sketchThumbContainer")))

    # show more
    for i in range(iters):
        element = wait.until(
            EC.element_to_be_clickable((By.ID, 'showMoreButton')))
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
    write_csv(array_links, file_name)


def get_sketch(link):
    try:
        driver.get(link)

        likes = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//div[@data-target='#heartSidePanel'][@class='metric']")))
        likes_amount = likes.text

        comments = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//div[@data-target='#commentSidePanel'][@class='metric']")))
        comments_amount = comments.text

        wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'icon_share'))).click()
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@rel='nofollow']"))).click()

        return (link, likes_amount, comments_amount)

    except:
        print(f'Error en abrir {link}')


def download_sketches(filename):
    links = load_csv('links/some.csv', headers=["link"])

    sketches = set()

    for link in links:
        t = get_sketch(link)
        if t is not None:
            sketches.add(t)

    # t = get_sketch('https://openprocessing.org/sketch/453716')
    # t = get_sketch('https://openprocessing.org/sketch/423716')

    write_csv(sketches, "./links/links-data.csv", ["link", "likes", "comments"])


if __name__ == '__main__':
    start_time = time.time()

    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    driver.get("https://openprocessing.org/signin")

    # accept cookies
    element = wait.until(EC.visibility_of_element_located(
        (By.ID, 'ccc-notify-accept')))
    element.click()

    # sign in
    driver.find_element(By.NAME, "username").send_keys(
        "***")
    driver.find_element(By.NAME, "password").send_keys("***")

    wait.until(EC.element_to_be_clickable(
        (By.ID, 'joinModal_submitButton'))).click()

    # comments = driver.find_element(
    #   By.XPATH, "//div[@data-target='#commentSidePanel'][@class='metric']")

    time.sleep(2)

    ###
    # collect_links(0, "./links/some.csv")

    ###
    download_sketches('/links/some.csv')

    driver.close()

    print("--- %s seconds ---" % (time.time() - start_time))
