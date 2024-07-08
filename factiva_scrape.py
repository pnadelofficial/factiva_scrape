from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Page input for Factiva Scrape.')
parser.add_argument('page', default=1, type=int, help='The page number to start on.')
args = parser.parse_args()

page = args.page

# Set up the driver
wd = webdriver.Chrome()

# Go to the Factiva page
wd.get('http://www.library.tufts.edu/ezproxy/ezproxy.asp?LOCATION=RsrcRcrdFactiva')

time.sleep(5)

# Send keys
wd.find_element(By.TAG_NAME, 'textarea').send_keys('rst=grdn and AIDS')

# Click the search button
wd.find_element(By.ID, 'btnSBSearch').click()

home = os.path.expanduser('~')
print('Home Path: ', home)
print('Starting on page: ', page)

pattern = re.compile(r'Factiva\-[0-9]+\-[0-9]+.rtf')
timeout = 20

if page > 1:
    for i in range(page - 1):
        time.sleep(5)
        next_item = wd.find_element(By.CLASS_NAME, 'nextItem')
        next_item.click()

for i in range(5):
    if i != 0:
        time.sleep(5)
        wd.find_element(By.CLASS_NAME, 'headlineHeader').find_element(By.TAG_NAME, 'a').click()
    try:
        time.sleep(5)
        wd.find_element(By.ID, 'selectAll').click()

        next_item = (By.CLASS_NAME, 'nextItem')
        element_present = WebDriverWait(wd, timeout).until(
            EC.presence_of_element_located(next_item)
        )
        
        wd.find_elements(By.CLASS_NAME, 'ppsBtn')[6].click()
        wd.find_elements(By.CLASS_NAME, 'ppsBtn')[6].click()
        time.sleep(15)
        list_menu = wd.find_element(By.ID, 'listMenu-id-3')
        time.sleep(5)
        btn = list_menu.find_elements(By.TAG_NAME, 'a')[1]
        time.sleep(2)
        try:
            btn.click()
        except:
            for _ in range(5):
                time.sleep(5)
                btn.click()

        word_limit = (By.CLASS_NAME, 'dj_btn-blue-new')
        try:
            wl_element_present = WebDriverWait(wd, timeout).until(
                EC.presence_of_element_located(word_limit)
            )
            wl_element_present.click()  
            time.sleep(20)
        except TimeoutException:
            print("Word limit issue not present.")
            pass

        time.sleep(5)
        element_present.click()
        page += 1
        print('Page: ', page)
        time.sleep(5)

    except TimeoutException:
        print("Timed out waiting for the element to be present.")