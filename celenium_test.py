from selenium import webdriver
from selenium.webdriver.common.keys import Keys

path = "/Users/rocky/Desktop/sparta-app/chromedriver"
driver = webdriver.Chrome(path)
driver.get("http://www.facebook.org")