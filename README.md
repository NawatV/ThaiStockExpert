# ThaiStockExpert

*** How to Use: 1. Place all the .py files in the same directory (e.g., Desktop). <br>
<pre>
	          2. Read/follow the descriptions below. <br> 
	          3. Start the project (follow 0_START.txt). <br>
</pre>
--- PREREQUISITE: - Please read/follow all the descriptions and warnings in the Python shell during usage.

# Python
--- PREREQUISITE: - Set up your Python IDE, Environment Variables, & Python libraries (such as CMD <br>
> pip install <package/lib.-name> (e.g., fsspec)) to be ready for usage.  

# All the Files ***
--- PREREQUISITE: - Check all the paths (### PATH !!!) in the source code & make them valid & compatible <br>
with your environment before running the project.  

### stockRetrieve.py
--- PREREQUISITE: 	- Register on https://developer.settrade.com/open-api/ <br>
			- Added your own 'app_id' & 'app_secret' below. <br> 
			- Please do not open the .csv file to which the project is writing data. <br>
//// SET's API doesn't always return up-to-date data & it's occasionally inaccessible including around 4:15-5:15am (GMT+7) ////

### stockLSTM.py
//// The market is influenced by several factors <br>
So you will get probabilities, not certainties as the results ////

### stockGRU.py
//// The market is influenced by several factors <br>
So you will get probabilities, not certainties as the results ////

### stockScraper.py
--- PREREQUISITE: - Download a Chrome WebDriver compatible with its version on https://developer.chrome.com/docs/chromedriver/downloads <br>
			(if 'warning' > 'Chrome for Testing avai.dashboard'). <br>
			- Extract all > put chromedriver.exe at your path > assign the path to 'driver_path' below. <br>  
			// Check your Chrome's version on chrome://settings/help <br>

//// The structure of the site being scraped is subject to changes by its development team, which may result in scraping failures or other issues ////

### web_scraper.py
--- PREREQUISITE: Same as # stockScraper.py <br>
// Changed to develop in stockRetrieve.py  using Settrade Open API. <br> 
- This file could be used for developing this project and/or others in the future.

*** If you find a bug or have a question, please contact nawatv@gmail.com <br> 
*** Ready to be further developed in the future, espectially the GRU and LSTM models.