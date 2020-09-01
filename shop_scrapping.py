import requests
import re
import tldextract
from bs4 import BeautifulSoup as soup, BeautifulSoup
from urllib.request import Request, urlopen
import urllib.request

# url을 받기 위한 변수 (현재는 특정 페이지를 한정하여 스크랩핑을 한다.)
url = 'https://ssense.com/en-kr/men/product/adidas-originals/navy-trefoil-baseball-cap/5178381'
# url = 'https://news.naver.com/main/read.nhn?mode=LPOD&mid=sec&oid=001&aid=0011837563&isYeonhapFlash=Y&rc=N'
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) '
#                          'Chrome/73.0.3683.86 Safari/537.36'}
#headers = {'User-Agent': 'Mozilla/5.0'}
#data = requests.get(url, headers=headers)


# 두번째 방법
#class AppURLopener(urllib.request.FancyURLopener):
#    version = "App/1.7"

#urllib._urlopener = AppURLopener()
#output = urllib._urlopener.open(url)
#print(output)

# 비슷한 세번째 방법
req = urllib.request.Request(url, headers={'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
                                                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.39.132 '
                                                          'Safari/53.36'})
response = urllib.request.urlopen(req).read()
text = response.decode('utf-8')
print(text)

# 타 방법으로 해보기
#req = Request(url, headers=headers)
#webpage = urlopen(req).read()
#page_soup = soup(webpage, 'html.parser')

# HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
# soup이라는 변수에 "파싱 용이해진 html"이 담긴 상태가 됨
# 이제 코딩을 통해 필요한 부분을 추출하면 된다.

soup = BeautifulSoup(text, 'html.parser')

#############################
# select를 이용해서, 기능에 따라 불러오기
# 사이트에 따라 크롤링 요소가 다르다. (우선 ssense기준으로 한다.)

# ssense.com
price_selector = '#wrap > div > div > div.pdp__mobile--new.pdp__redesign > div > div.pdp-mobile > div > div > div.s-row.pdp-header__right > div > div:nth-child(1) > div > div > div:nth-child(2) > div:nth-child(1) > div > div > h1'
price = soup.select_one(price_selector).text;

#soup.select('상위태그명.클래스명 > 하위태그명.클래스명')
#print(page_soup.prettify())

print('kkkkkkk1')
print(price)
print('kkkkkkk2')


#carousel-slide-181 > picture > img
#carousel-slide-198 > picture > img

#text = "에러 1122 : 레퍼런스 오류\n 에러 1033: 아규먼트 오류"
regex = re.compile("https://img.ssensemedia.com/images/")
#pic_url = regex.search(text)
pic_url = re.findall(r'(https://img.ssensemedia.com/images/+)', text)

if pic_url != None:
    print(pic_url)


#pic = soup.find('image',text=re.compile('https://img.ssensemedia.com/images/'))
site = tldextract.extract('https://www.ssense.com/en-kr/men/product/adidas-originals/navy-trefoil-baseball-cap/5178381')



#print(pic)
print(site.domain)
