#PREREQUISITE: - Download a Chrome WebDriver compatible with its version on
#                   https://developer.chrome.com/docs/chromedriver/downloads (if 'warning' > 'Chrome for Testing avai.dashboard')
#              - Extract all > put chromedriver.exe at your path > assign the path to 'driver_path' below  
#                   //Check your Chrome's version on chrome://settings/help

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains
# Use copy & paste
import pyperclip
# Use pathlib to work with paths (optional)
from pathlib import Path

#As of 5/June/2025 
# ============= Scrape data | Click ele | Search for stock | Scrape the searched data | [SET(eng)] =============================
#               Full XPATH 

# Set up the path to chromedriver
                    ### PATH !!!
driver_path = Path("C:/Users/LENOVO/Desktop/thai_stock_expert/chromedriver/chromedriver.exe")
# Create a webDriver service
service = Service(driver_path)
# Launch Chrome
driver = webdriver.Chrome(service=service)
# Open a website: SET (eng)
driver.get("https://www.set.or.th/en/home")
# Wait
time.sleep(4)

# Function
def clrPopup():
    try:
        e_x = None
        e_x = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[1]/button")
        if e_x is not None:
            e_x.click()
    except:
        print("No 'X' button found.")

# Long-term vars
li1_data = []   # Storing [idx, last]
li2_data = []   # Storing 'Price Info (Day Range)'
li3_data = []   # Storing 'Price Info (52-Week Range)'
li4_data = []   # Storing 'Highlights'


# Pre-find an element
## Clear the pop-up if it exists [Click]
clrPopup()

## Accept all the cookies [Click | Full XPATH + By.CLASS & TAG_NAME]
try:
    #--- Full XPATH ---
    e_acc = None
    e_acc = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[7]/div/div/div[2]/button")
    if e_acc is not None:
        e_acc.click()

    #--- By.CLASS & TAG_NAME ---
    # e_acc_block = driver.find_element(By.CLASS_NAME, "pdpa")
    # e_acc = e_acc_block.find_element(By.TAG_NAME, "button")
    # if e_acc is not None:
    #    e_acc.click()
        
except:
    print("No 'Accept cookies' button found.")
    
# Find an element
for i in range(10):                      
    e_col_path = "/html/body/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div/div[1]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div/table[2]/tbody/"
    e_idx_col = None
    e_last_col = None
    
    try:
        e_idx_col = driver.find_element(By.XPATH, e_col_path + "tr[" + str(i+1) + "]/td[1]/div/a/div")
        # print(e_idx_col.text, end=" | ")
    except:
        print("No e_idx_col_" + str(i+1) + " found.")
    try:
        e_last_col = driver.find_element(By.XPATH, e_col_path + "tr[" + str(i+1) + "]/td[2]/div/span")
        # print(e_last_col.text)
    except:
        print("No e_last_col_" + str(i+1) + " found.")

    li1_data.append([e_idx_col.text, e_last_col.text])

# Print li1_data
print(li1_data)

# Find & search in a search box [pyperclip & js] [Must use]
try:
    #--- Recognize an input ---
    e_search_path = "/html/body/div[1]/div/div/header/div[1]/div[1]/div/div[3]/div"
    e_search = None
    e_search = driver.find_element(By.XPATH, e_search_path) #X if e_search is not None:
    time.sleep(1)
    print("Type the stock name:", end=" ")
    n = input() # Already case-insensitive on SET

    #--- Clear the pop-up if it exists [Click] ---
    clrPopup()
    
    #--- pyperclip ctrl+c +v & click the search box ---
    pyperclip.copy(n) 
    e_search.click()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()

    #--- js to click search ---
    div_path = "/html/body/div[1]/div/div/header/div[1]/div[1]/div[1]/div[3]/div/div[4]" #X /svg
    e_searchBtn = driver.find_element(By.XPATH, div_path)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", e_searchBtn)
    time.sleep(4)
    # Doesn't work
    # e_search.clear() | e_search.send_keys("Amata")
    #   | e_search.send_keys(Keys.RETURN / Keys.ENTER) | e_searchBtn.click() | ActionChains(driver)       
except:
    print("Something wrong in the searching time")

# At the searched page
## Clear the pop-up if it exists [Click]
clrPopup()

# Find an element
e_pinfo_all = driver.find_element(By.ID, "stock-quote-tab-pane-1") #To be used next
try:
    #e_pinfo = driver.find_element(By.XPATH, e_pinfo_path)
    #e_pinfo_all = driver.find_element(By.ID, "stock-quote-tab-pane-1") #To be used next
    e_pinfo_cont = e_pinfo_all.find_element(By.CSS_SELECTOR, "[class*='price-info-stock']") # X By.CLASS_NAME
    e_pinfo_detail = e_pinfo_cont.find_element(By.CSS_SELECTOR, "[class*='cost-detail']")
    e_pinfo_detailBxs = e_pinfo_detail.find_elements(By.CSS_SELECTOR, "[class*='price-info-stock-detail-box']")
    for bx in e_pinfo_detailBxs:
        itms = bx.find_elements(By.CSS_SELECTOR, "[class*='item-list-details']") #= 6 items
        #--- Data Range ---
        data_day = itms[0]
        label_day = data_day.find_element(By.TAG_NAME, "label")
        value_day = data_day.find_element(By.TAG_NAME, "span")
        li2_data.append([label_day.text, value_day.text])
        #--- 52-Week Range ---
        data_52 = itms[1]
        label_52 = data_52.find_element(By.TAG_NAME, "label")
        value_52 = data_52.find_element(By.TAG_NAME, "span")
        li3_data.append([label_52.text, value_52.text])
except:
    print("Price Info failed")

# Print li2_data & li3_data
print(li2_data)
print(li3_data)



# Find an element <<<<<<<< Highlights & Make find_element more flex. (cssselector, etc.)
#try:
    # Doesn't work
    #X e_hl_impL_main_path = "/html/body/div[1]/div/div/div[2]/div[2]/div[2]/div/div/div[2]/div/div/div[1]"
    #X driver.execute_script("arguments[0].scrollIntoView(true);", e_hl_impL_main)
    #X e_hl_impLs = driver.find_elements(By.CSS_SELECTOR, "[class*='price-important-stock-left']")        
#except:
    #print("Highlights failed")

# Print li4_data
print(li4_data)

#Wait the popup
time.sleep(5)
clrPopup()



# Close the browser
driver.quit()
