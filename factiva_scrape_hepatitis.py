from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import os
import subprocess

# Set up the driver
wd = webdriver.Chrome()

# Go to the Factiva page
wd.get('http://www.library.tufts.edu/ezproxy/ezproxy.asp?LOCATION=RsrcRcrdFactiva')

time.sleep(10)

# Send keys
query = """
Hepatitis C not ("Hepatitis C Times Newspapers Ltd" or "Hepatitis C The Financial Times Limited") and (rst=st or rst=sundti or rst=t or rst=timeuk or rst=dt or rst=stel or rst=TELUK or rst=ob or rst=IND or rst=INDOP or rst=INDOS or rst=IIND or rst=grdn or rst=GRULTD or rst=ftft or rst=ftcom or rst=thesun or rst=thesuk or rst=daim or rst=mosm or rst=damonl or rst=theexp or rst=thexsu or rst=exco or rst=dmirr or rst=smirr or rst=miruk or rst=POPL or rst=daista or rst=dsun or rst=daico or rst=ns or rst=nsonl or rst=metro)
""".strip()
wd.find_element(By.TAG_NAME, 'textarea').send_keys(query)

# Click the search button
wd.find_element(By.ID, 'btnSBSearch').click()

home = os.path.expanduser('~')
print(home)

pattern = re.compile(r'Factiva\-[0-9]+\-[0-9]+.rtf')
timeout = 20
next_item = (By.CLASS_NAME, 'nextItem')

for i in range(5):
    if i != 0:
        time.sleep(5)
        wd.find_element(By.CLASS_NAME, 'headlineHeader').find_element(By.TAG_NAME, 'a').click()
    try:
        wd.find_element(By.ID, 'selectAll').click()

        element_present = WebDriverWait(wd, timeout).until(
            EC.presence_of_element_located(next_item)
        )
        
        wd.find_elements(By.CLASS_NAME, 'ppsBtn')[6].click()
        wd.find_elements(By.CLASS_NAME, 'ppsBtn')[6].click()
        time.sleep(15)
        wd.find_element(By.ID, 'listMenu-id-3').find_elements(By.TAG_NAME, 'a')[1].click()

        word_limit = (By.CLASS_NAME, 'dj_btn-blue-new')
        try:
            wl_element_present = WebDriverWait(wd, timeout).until(
                EC.presence_of_element_located(word_limit)
            )
            wl_element_present.click()  
        except TimeoutException:
            print("Timed out waiting for the element to be present.")

        time.sleep(15)
        # dl_file = [f for f in os.listdir(os.path.join(home, 'downloads')) if pattern.search(f)][0]
        # subprocess.run(['cp', os.path.join(home, 'downloads', dl_file), './factiva_data/'])
        # subprocess.run(['rm', os.path.join(home, 'downloads', dl_file)])

        time.sleep(10)
        element_present.click()
        time.sleep(10)

    except TimeoutException:
        print("Timed out waiting for the element to be present.")