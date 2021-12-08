[![works badge](https://cdn.jsdelivr.net/gh/nikku/works-on-my-machine@v0.2.0/badge.svg)](https://github.com/nikku/works-on-my-machine)

# pd_scraper
product data scraper - scrape product data from vendor websites and create ontologies\
the scraping part is an admittedly fragile implementation; works on my machine as of 12/21

# content
* bots for scraping product data for microcontrollers from [conrad](https://www.conrad.de/) and [infinity-electronic](https://www.infinity-semiconductor.com/)
* module for creating two separate ontologies from the data scraped

# instructions
* set up chrome driver
  * check Chrome version via [chrome://version/](chrome://version/)
  * download respective driver version from [Google download site](https://chromedriver.chromium.org/downloads)
  * specify the path to the Chrome driver in the config file *constants.py*
* using a virtual environment is recommended; in bash:
  * create: ```python -m venv .venv```
  * activate: ```source .venv/bin/activate```
* install dependencies, e.g., with pip ```pip install -r requirements.txt```
* run via ```python pd_scraper.py```

# contact
Felix Ocker - [felix.ocker@tum.de](mailto:felix.ocker@tum.de)
