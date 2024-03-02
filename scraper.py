from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
import math
import pandas as pd
import os

from dotenv import load_dotenv
load_dotenv()

def get_text(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    #https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.94/win64/chromedriver-win64.zip go here for windows version
    chrome_service = ChromeService(executable_path='/Users/m296082/Downloads/chromedriver-mac-arm64/chromedriver')
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )

    full_text = driver.find_element(By.TAG_NAME, 'body').text
    driver.quit()
    return full_text

api_key = os.getenv("API_KEY")
console_id = os.getenv("CONSOLE_ID")

queries = ["Is Climate Change Real?"]

incr = 58
max_year = 2024
min_year = 2000
upper_month = 0
month_incr = incr % 12
year_incr = incr // 12
upper_year = max_year
lower_year = upper_year - year_incr

for query in queries:
    dataset = {
        "title": [],
        "link": [],
        "determined_date": [],
        "date_range": [],
        "content": [],
        "snippet": []
    }
    while (upper_year > min_year):
        lower_month = upper_month - month_incr
        if lower_month < 0:
            lower_month += 12
            lower_year -= 1
        print(f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={console_id}&q={query}&start={1}&num=10&sort=date:r:{lower_year}{'{:02d}'.format(lower_month)}00:{upper_year}{'{:02d}'.format(upper_month)}00")
        res = requests.get(f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={console_id}&q={query}&start={1}&num=10&sort=date:r:{lower_year}{'{:02d}'.format(lower_month)}00:{upper_year}{'{:02d}'.format(upper_month)}00").json()    
        upper_year = lower_year
        lower_year -= year_incr
        upper_month = lower_month
        if "items" in res:
            for i, result in enumerate(res["items"]):
                print(result["link"])
                content = get_text(result["link"])
                date = "NA"
                try:
                    res = requests.head(result["link"])
                    date_data = res.headers.get("Last-Modified")
                    if date_data:
                        date = date_data
                    else:
                        meta = result["pagemap"]["metatags"][0]
                        res = [val for key, val in meta.items() if "date" in key]
                        if res:
                            date = res[0]
                except:
                    pass
                dataset["title"].append(result["title"])
                dataset["link"].append(result["link"])
                dataset["determined_date"].append(date)
                dataset["date_range"].append(f"{lower_year}{lower_month}-{upper_year}{upper_month}")
                dataset["content"].append(content)
                dataset["snippet"].append(result["snippet"])

            datasetFile = pd.DataFrame(dataset)
            datasetFile.to_csv(f"{query}.csv")                                  