[![works badge](https://cdn.jsdelivr.net/gh/nikku/works-on-my-machine@v0.2.0/badge.svg)](https://github.com/nikku/works-on-my-machine)

# pd_scraper
product data scraper - scrape product data from vendor websites and create ontologies\
the scraping part is an admittedly fragile implementation; works on my machine as of 12/21

# content
* bots for scraping product data for microcontrollers from [conrad](https://www.conrad.de/), [infinity-electronic](https://www.infinity-semiconductor.com/), and [RS Components](https://de.rs-online.com/web/)
* module for creating separate ontologies from the data scraped from conrad and infinity

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

# requirements
* Chrome
* Python 3.9+ recommended

# license
GPL v3.0

# contact
Felix Ocker - [felix.ocker@tum.de](mailto:felix.ocker@tum.de)
