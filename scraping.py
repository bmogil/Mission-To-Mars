# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemispheres": hemispheres(browser)
    }
    
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):    
    
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)
    
    # Convert the browser html to a soup object and then quit the browser (Don't know why it says the quit browser part ... but TB says this ... maybe a typo?)
    html = browser.html
    news_soup = soup(html, 'html.parser') 

     # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
     
    except AttributeError:
        return None, None
   
    return news_title, news_p


### Featured Images

def featured_image(browser):
    
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None
    
    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

def mars_facts():
    try:
      # use 'read_html" to scrape the facts table into a dataframe
      df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
      return None
    
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    return df.to_html()

def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    # 2. Create a list to hold the image titles.
    hemisphere_image_urls = []
    for i in range(4):
        # Browse through each article
        browser.find_by_css('a.product-item img')[i].click()
   
        # Title Parsing (Must be done here because after the next click, the title will not be there)
        html_1 = browser.html
        title_soup = soup(html_1, 'html.parser')
   
        # Title Scraping
        img_title = title_soup.find('h2', class_='title').text
    
        # Click on sample image link to get the fully enhanced image link
        browser.links.find_by_partial_text('Sample').click()
    
        # Image URL Parsing
        html = browser.html
        img_soup = soup(html, 'html.parser')
    
        # Image URL Scraping
        img_url = img_soup.find('li').a.get('href')

        # Store findings into a dictionary and append to list
        hemispheres = {}
        hemispheres['img_url'] = f'https://marshemispheres.com/{img_url}'
        hemispheres['img_title'] = img_title
        hemisphere_image_urls.append(hemispheres)
    
        browser.back()
        
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())



