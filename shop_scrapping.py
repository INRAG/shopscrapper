import requests
import re
import tldextract
from bs4 import BeautifulSoup as soup, BeautifulSoup
from urllib.request import Request, urlopen
from pymongo import MongoClient
from flask import Flask

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbshopscrapper
import urllib.request
import schedule

# url을 받기 위한 변수 (현재는 특정 페이지를 한정하여 스크랩핑을 한다.)
# db에 article에 저장되어있는 url 을 불러와서 시간 조건(해당 소스에 기재)과 가격조건을 가져와서 참 여부에 따라 알람을 보내는 스케쥴을 설정한다. (기본적으로는 10분)
# 앱 푸시는 현재 구현되기 전이므로, print로 해당 조건이 맞는지까지 우선 검증한다.
# 시간 조건에 따라 1번이상 계속 메시지를 보내는 경우가 생기므로, 조건이 충족했을 때마다 확인 체크용 데이터를 남겨서 처리한다. 우선적으로는 두번정도 보낸다.
# 혼자가 아닌 여러명이 사용하는 경우, 사용자 (즉,앱)을 분별하여 전송을 하는 것이 필요함.

# 1. DB에 있는 데이터를 조회하여, 알람을 보내기 위한 준비
# 1-1. 보내는 대상에 대한 세분화가 필요함(알람유효기간 지난것, 이미 보낸것) but 지금은 전체로 함.
# 1-2. 메시지를 보낼 때, 자세한 텍스트를 보내주기 위해서 대부분의 정보를 가져온다.(userid별 단말기 정보가 필요함)

def job():
    result = list(db.article.find({}, {'_id': 0}))
    print(result);

    for i in result:
        url = i['url']
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
                                                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.39.132 '
                                                                 'Safari/53.36'})
        response = urllib.request.urlopen(req).read()
        text = response.decode('utf-8')
        soup = BeautifulSoup(text, 'html.parser')
        price_selector = '#wrap > div > div > div.pdp__mobile--new.pdp__redesign > div > div.pdp-mobile > div > div > div.s-row.pdp-header__right > div > div:nth-child(1) > div > div > div:nth-child(2) > div:nth-child(1) > div > div > h1'
        price = soup.select_one(price_selector).text;
        price_mix = re.findall(r'[\d\.\d]+', price)

        # price 정보는 주기에 따라 db에도 저장한다. (후 처리)
        # price와 wprice 와의 관계 비교.
        if price_mix[0] < i['wprice']:
            print("** 충족 후 알람 보내기. **")
            #중복메시지 반복됨에 따른 처리
            print(i['title']+'에 대한 가격정보가 현재가격('+price_mix[0]+')이 되어 설정한 ('+i['wprice']+')보다 적게 충족되었습니다.')

            # * 앱푸쉬를 보내는 조건이므로 앱푸쉬를 보내며, 앱푸쉬를 보낸 시간을 계산하여, 앱푸쉬 기능에서 가장 최근에 보낸게 있으면 제외하도록 한다.

        else:
            print("** 충족하지 못하였습니다. **")
            print(i['title'] + '에 대한 가격정보가 현재가격(' + price_mix[0] + ')이 되어 설정한 (' + i['wprice'] + ')보다 크게 충족되었습니다.')


if __name__ == '__main__':
    schedule.every().day.at('01:02').do(job)  # 매일 09:00 마다 job 함수를 실행
    while True:
        schedule.run_pending()
