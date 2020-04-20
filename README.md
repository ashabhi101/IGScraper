# IGScraper
A simple Selenium based IG Scraper

Requires
1. Python 3.x
2. Selenium
3. Chrome
4. Chromedriver ([compatible chromedriver](https://chromedriver.chromium.org/))
5. Standard Python libraries: urllib, bs4, json, re, time

Information on setting up selenium with Chrome: https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver

Functionality:
1. ``log_in()`` - logs you in using credentials from class instantiation. Note if 2-factor authentication, you will need to input the 2nd authentication code.
2. ``get_user(username)`` - Navigate to user page
3. ``scroll_page(sleep=2, maxiters=1000, reset_links=True)`` - Scroll through user page and collect user image links
4. ``get_all_photos(sleep=2, fpath='../Data/)`` - downloads all photos from links in self.piclinks_profile.

Auxiliary methods:
1. ``reset_links()`` - clears photo queue
2. ``get_page(url)`` - same as selenium "get"
3. ``quit()`` - shuts down selenium drivers and resets links
4. ``get_photos(fpath='../Data/)`` - downloads current photo to fpath
