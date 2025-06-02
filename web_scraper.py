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

#As of 2/June/2025 
# ============= Scrape data | Click ele | Search for stock [SET(eng)] =============================
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
time.sleep(3)

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
li2_data = []   # Storing 'Price Info'
li3_data = []   # Storing 'Highlights'


# Pre-find an element
## Clear the pop-up if it exists [Click]
clrPopup()

## Accept all the cookies [Click | Full XPATH + By.CLASS & TAG_NAME]
try:
    #--- Full XPATH ---
    e_x = None
    e_x = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[7]/div/div/div[2]/button")
    if e_x is not None:
        e_x.click()

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
    e_srh_path = "/html/body/div[1]/div/div/header/div[1]/div[1]/div/div[3]/div"
    e_srh = None
    e_srh = driver.find_element(By.XPATH, e_srh_path) #X if e_srh is not None:
    time.sleep(1)
    print("Type the stock name:", end=" ")
    n = input()

    #--- Clear the pop-up if it exists [Click] ---
    clrPopup()
    
    #--- pyperclip ctrl+c +v & click the search box ---
    pyperclip.copy(n) 
    e_srh.click()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()

    #--- js to click search ---
    div_path = "/html/body/div[1]/div/div/header/div[1]/div[1]/div[1]/div[3]/div/div[4]" #X /svg
    e_srhBtn = driver.find_element(By.XPATH, div_path)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", e_srhBtn)
    time.sleep(3)
    # Doesn't work
    # e_srh.clear() | e_srh.send_keys("Amata") | e_srh.send_keys(Keys.RETURN / Keys.ENTER) | e_srhBtn.click() | ActionChains(driver)       
except:
    print("Something wrong in the searching time")

# At the searched page
## Clear the pop-up if it exists [Click]
clrPopup()

# Close the browser
driver.quit()
