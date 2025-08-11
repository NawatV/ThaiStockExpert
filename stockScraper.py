from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains
# Use pathlib to work with paths (optional)
from pathlib import Path

# ===== Scrape %_ann_R_f data | Big try-except (compre.) | Small try-except | Web struc.warning ===========


def scrape_percent_ann_R_f(type):
    try:
        print("//// The structure of the site being scraped is subject to changes by its development team, which may result in scraping failures or other issues ////")
        try:
            # Set up the path to chromedriver   ##### PATH !!!
            driver_path = Path("C:/Users/LENOVO/Desktop/thai_stock_expert/chromedriver/chromedriver.exe")
            # Create a webDriver service
            service = Service(driver_path)
            # Launch Chrome
            driver = webdriver.Chrome(service=service)
        except:
            print("Something wrong with your Chrome WebDriver, please check/update it.")

        if type == "3M":
            # Open a website
            driver.get("https://www.thaibma.or.th/")
            # Wait
            time.sleep(1.5)
            # Find an element
            table = driver.find_element(By.ID, "grid_GovYC")
            tbody = table.find_element(By.TAG_NAME, "tbody")
            li_tr = tbody.find_elements(By.TAG_NAME, "tr") 
            li_td = li_tr[1].find_elements(By.TAG_NAME, "td") #= idx
            val = li_td[1].text
            print("Just scraped an init.data!, Risk-Free Rate (3M Thai Gov.Bond Yield Curve)= ", val, " %")
            # Close the browser
            driver.quit()

        return val

    except:
        print("Something wrong, please check 'stockScraper.py'")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")    
