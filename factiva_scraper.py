from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from bs4 import BeautifulSoup
import time
import pandas as pd
import glob
import re
import getpass
from typing import List, Tuple
import os

username = input("Enter your username: ")
password = getpass.getpass()

class FactivaWebDriver:
    def __init__(self, options:List=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-popup-blocking",
    ]) -> None:
        self.options = options
        chrome_options = webdriver.ChromeOptions()
        for option in self.options:
            chrome_options.add_argument(option)
        self.wd = webdriver.Chrome(options=chrome_options)
        self.wd.get('http://www.library.tufts.edu/ezproxy/ezproxy.asp?LOCATION=RsrcRcrdFactiva')
        self.wd.refresh()

class Login:
    def __init__(self, username, password, options:List=[
        "--no-sandbox", 
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-popup-blocking",
    ]) -> None:
        self.username = username
        self.password = password

        fwd = FactivaWebDriver(options=options)
        self.wd = fwd.wd

    def __call__(self, timeout=10) -> None:
        tufts_login = WebDriverWait(self.wd, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//div[@__idx='0']"))
        )
        tufts_login.click()

        tufts_username = WebDriverWait(self.wd, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='username']"))
        )
        tufts_username.send_keys(self.username)

        tufts_password = WebDriverWait(self.wd, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='password']"))
        )
        tufts_password.send_keys(self.password)

        tufts_login_button = WebDriverWait(self.wd, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//button[@type='submit']"))
        )
        tufts_login_button.click()

        skip_for_now_button = WebDriverWait(self.wd, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[@type='button']"))
        )[1]
        skip_for_now_button.click()

        trust_this_computer_button = WebDriverWait(self.wd, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//button[@id='trust-browser-button']"))
        )
        trust_this_computer_button.click()

        # switch to new factiva
        switch_factiva = WebDriverWait(self.wd, 3*timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'nf-toggle-switch'))
        )
        switch_factiva.click()

class Scraper:
    def __init__(self, query, timeout:int=10, save_every:int=10, restart:bool=False) -> None:
        login = Login(username, password)
        login()

        self.wd = login.wd
        self.query = query
        self.restart = restart
        self.save_every = save_every
        self.timeout = timeout
        os.makedirs('./factiva_data', exist_ok=True)

    def _input_query(self) -> None:
        search_bar = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-wiv1jh"))
        )
        search_bar.send_keys(self.query + '\n')

    def _change_filters(self) -> None:
        dropdowns = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='css-twgx2n']/div[@class='css-14sgzgm']"))
        )

        ## dates
        dropdowns[-1].click()
        date_options = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-170nmmu'))
        )[-2]
        date_options.click()

        ## order
        dropdowns[0].click()
        rel_options = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1muq4vo'))
        )[-1]
        rel_options.click()
    
    def _input_date(self, day, month, year) -> None:
        self.wd.refresh()
        dropdowns = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='css-twgx2n']/div[@class='css-14sgzgm']"))
        )
        dropdowns[0].click()
        rel_options = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1muq4vo'))
        )[-1]
        rel_options.click()
        dropdowns[-1].click()
        date_options = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-170nmmu'))
        )[-1]
        date_options.click()
        date_selects = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-idt3y3'))
        )
        if len(day) == 1:
            day = '0' + day
        date = f"{day}-{month[:3]}-{year}"
        date_selects[0].send_keys(date)
        done_button = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'css-z7eyns'))
        )
        done_button.click()
    
    def _recover(self) -> None: 
        poss_recovery_files = glob.glob('./factiva_data/*_to_page_*.csv')
        sorted_files = sorted(poss_recovery_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        latest_file = sorted_files[-1]
        print(f"Recovering from {latest_file}")
        df = pd.read_csv(latest_file)
        dates = df.apply(lambda x: re.search(r'\d{1,2}\s+\w+\s+\d{4}', x['Byline']).group(0), axis=1)
        dates = pd.to_datetime(dates, format='%d %B %Y').sort_values()
        last_date = dates.iloc[-1].strftime('%d-%b-%Y')
        print(f"Last date: {last_date}")
        d, m, y = last_date.split('-')
        self._input_date(d, m, y)
    
    def _parse_results(self, save_every:int=10) -> List:
        page_numbers = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-lakely"))
        )
        max_pages = page_numbers.text.split()[-1].replace(',', '')

        data = []
        current_date = None
        for i in range(int(max_pages)-1):
            print(f"Page {i+1}/{max_pages}, Date: {current_date}, Articles collected: {len(data)}, Percent complete: {len(data)/int(max_pages)*100:.2f}%")
            try:
                year_of_first_result_on_page = WebDriverWait(self.wd, 1.5*self.timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'css-1tryk67'))
                ).text
                if ',' in year_of_first_result_on_page:
                    year_of_first_result_on_page = year_of_first_result_on_page.split(',')[0]
                current_date = year_of_first_result_on_page
                d, m, y = year_of_first_result_on_page.split()
                
                page_results = WebDriverWait(self.wd, 2*self.timeout).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-p43ypb'))
                )
            except TimeoutException:
                self._input_date(d, m, y)
            
            for j in range(len(page_results)):
                try:
                    title, byline, text = self._get_text_from_result(page_results[j])
                    data.append((title, byline, text))
                except AttributeError:
                    print(f"No text available on page {i+1}, article {j+1}")
                    pass
                except IndexError:
                    print(f"No text available on page {i+1}, article {j+1}")
                    pass
                except TimeoutException:
                    print(f"No text available on page {i+1}, article {j+1}")
                    pass

                back_button = WebDriverWait(self.wd, self.timeout).until(
                    EC.presence_of_element_located((By.ID, 'articleBackButton'))
                )
                back_button.click()
                time.sleep(2)
                page_results = WebDriverWait(self.wd, self.timeout).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-p43ypb'))
                )
            self.wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            next_page = WebDriverWait(self.wd, self.timeout).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "css-1oqu26d"))
            )[-1]
            try:
                next_page.click()
            except StaleElementReferenceException:
                break

            print("Articles collected: ", len(data))

            if i//save_every == 0:
                print("Saving intermediary data...")
                df = pd.DataFrame(data, columns=['Title', 'Byline', 'Text'])
                df.to_csv(f'./factiva_data/{self.query}_to_page_{i}.csv', index=False)
                print("Data saved.")
        
        self.data = data
        return data

    def _get_text_from_result(self, result) -> Tuple[str,str,str]:
        self.wd.execute_script("arguments[0].scrollIntoView();", result)
        result.click()
        article = WebDriverWait(self.wd, self.timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        soup = BeautifulSoup(article.get_attribute("innerHTML"), 'html.parser')
        title = soup.find('h1').get_text()
        byline = soup.find('div', class_="styled-wrappers__ExternalControlWrapper-sc-15q75tq-1 enwsIg").get_text()
        text = soup.find('div', class_="body-paragraph__BodyParagraphWrapper-sc-1c0tve-0 gByVbi").get_text()
        return title, byline, text
    
    def _save(self, data, filename) -> None:
        print("Saving data...")
        df = pd.DataFrame(data, columns=['Title', 'Byline', 'Text'])
        df.to_csv(filename, index=False)
        print("Data saved.")

    def scrape(self, filename=None):
        if not filename:
            filename = f'factiva_{self.query}.csv'
        
        self._input_query()
        print("Input query")

        self._change_filters()
        print("Changed filters")

        if self.restart:
            self._recover()
            print("Recovered from last save")

        self._parse_results(save_every=self.save_every)
        print("Parsed results")

        self._save(self.data, filename)
        self.wd.close()
