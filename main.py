import time
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.firefox.options import Options

# options = Options()
# options.add_argument('--start-maximized')

driver = webdriver.Firefox()
driver.maximize_window()
driver.get("https://openprocessing.org/browse/?time=anytime&type=all&q=#")
assert "Browse Sketches - OpenProcessing" in driver.title

wait = WebDriverWait(driver, 10)

element = wait.until(EC.element_to_be_clickable((By.ID, 'ccc-notify-accept')))
element.click()

for i in range(5):
    element = wait.until(EC.element_to_be_clickable((By.ID, 'showMoreButton')))
    element.click()
# elem.clear()
# elem.send_keys("pyconlamadamadingdong")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
time.sleep(10)
# driver.close()
