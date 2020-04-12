from selenium import webdriver

browser=webdriver.Firefox()
browser.get('http://localhost:8000')

#断言‘django’是否在浏览器网页的标题中
assert 'Django' in browser.title