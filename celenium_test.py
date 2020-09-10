from selenium import webdriver
from selenium.webdriver.common.keys import Keys

usr = '본인아이디'
pwd = '본인비밀번호'

path = "C:/Users/bumky/Desktop/develop/chromedriver"
driver = webdriver.Chrome(path)
driver.get("http://www.facebook.org")

assert "Facebook" in driver.title

elem = driver.find_element_by_id("email")
elem.send_keys(usr)
elem = driver.find_element_by_id("pass")
elem.send_keys(pwd)
elem.send_keys(Keys.RETURN)