from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
# Use pathlib to work with paths (optional)
from pathlib import Path

#As of 1/June/2025 
# ============= Full XPATH + Click (SET(eng)) =============================

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
time.sleep(4) #<-3


# Pre-find an element
## Exit a pop-up if it exists [Click]
try:
    e_x = None
    e_x = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[1]/button")
    if e_x is not None:
        e_x.click()
except:
    print("No 'X' button found.")
    
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
li_data = []
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

    li_data.append([e_idx_col.text, e_last_col.text])

# Print li_data
print(li_data)

# Close the browser
driver.quit()
