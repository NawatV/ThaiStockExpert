# ThaiStockExpert

*** How to Use: 1. Place all the .py files in the same directory (e.g., Desktop).
	          2. Follow the descriptions below. 
	          3. Run the project.

--- PREREQUISITE: - Please read all the descriptions and warnings in the Python shell during usage.
// Any bug found, contact nawatv@gmail.com
// Ready to be further developed in the future, espectially the LSTM model.

# Python
--- PREREQUISITE: - Set up your Python IDE, Environment Variables, & Python libraries (such as CMD > pip install <package/lib.-name> (e.g., fsspec))
		   to be ready for usage.  

# All the Files ***
--- PREREQUISITE: - Check all the paths (### PATH !!!) in the source code & make them valid & compatible with your environment before running the project.  

# stockRetrieve.py
--- PREREQUISITE: - Register on https://developer.settrade.com/open-api/
---                            - Added your own 'app_id' & 'app_secret' below. 
---                            - Please do not open the .csv file to which the project is writing data.

# stockLSTM.py
//// The market is influenced by several factors
        So you will get probabilities, not certainties as the results ////

# stockGRU.py
//// The market is influenced by several factors
        So you will get probabilities, not certainties as the results ////

# stockScraper.py
--- PREREQUISITE: - Download a Chrome WebDriver compatible with its version on
---                   	      https://developer.chrome.com/docs/chromedriver/downloads (if 'warning' > 'Chrome for Testing avai.dashboard').
---                            - Extract all > put chromedriver.exe at your path > assign the path to 'driver_path' below.  
---                   	//Check your Chrome's version on chrome://settings/help

# web_scraper.py
--- PREREQUISITE: Same as # stockScraper.py
// Changed to develop in stockRetrieve.py  using Settrade Open API. 
- This file could be used for developing this project and/or others in the future.