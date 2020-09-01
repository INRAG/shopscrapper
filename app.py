import urllib
import tldextract
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbshopscrapper


# ** 메인 기능 **
@app.route('/postcard', methods=['POST'])
def post_shopinfo():
    # 1. 클라이언트로부터 데이터를 받기
    url_receive = request.form['url_give']  # 클라이언트로부터 url을 받는 부분
    comment_receive = request.form['comment_give']  # 클라이언트로부터 comment를 받는 부분
    userid_receive = request.form['userid_give']  # 클라이언트로부터 userid를 받는 부분 (* 원래 제대로 하려면 로그인 한 사용자에 저장된 게시물만 보이도록 해야 함)
    wprice_receive = request.form['wprice_give']  # 클라이언트로부터 wprice를 받는 부분

    print("xxx1")
    # 2. meta tag를 스크래핑하기, 필요한 데이터 준비하
    url = url_receive;
    comment = comment_receive;
    wprice = wprice_receive;
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
                                                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                             'Chrome/80.0.39.132 '
                                                             'Safari/53.36'})
    response = urllib.request.urlopen(req).read()
    text = response.decode('utf-8')
    soup = BeautifulSoup(text, 'html.parser')

    price_selector = '#wrap > div > div > div.pdp__mobile--new.pdp__redesign > div > div.pdp-mobile > div > div > ' \
                     'div.s-row.pdp-header__right > div > div:nth-child(1) > div > div > div:nth-child(2) > ' \
                     'div:nth-child(1) > div > div > h1 '
    price = soup.select_one(price_selector).text;
    # * img 파싱 부분은 튜터님 확인중 (임시 이미지로 대체)
    img = 'https://a.wattpad.com/cover/66412110-352-k394450.jpg'
    img2 = 'https://scontent-ssn1-1.xx.fbcdn.net/v/t1.0-9/p960x960/29244092_1881987471874252_4979572236735217664_o.png?_nc_cat=110&_nc_sid=85a577&_nc_ohc=RhpeUwlP1EwAX_f6psz&_nc_ht=scontent-ssn1-1.xx&oh=702026b942d126bb43748ac639414335&oe=5F72CAF3'
    site = tldextract.extract(
        'https://www.ssense.com/en-kr/men/product/adidas-originals/navy-trefoil-baseball-cap/5178381')

    # * 어떤 user가 넣는지 조회하여 자신에 해당하는 정보만 가져오기 위함. (user 정보에 인덱스 걸면 금방나올듯)
    userid = userid_receive;

    # * title 과 desc 도 받아서 구현해놓을 것 헐..
    title1_selector = '#wrap > div > div > div.pdp__mobile--new.pdp__redesign > div > div.pdp-mobile > div > div > ' \
                      'div.s-row.pdp-header__right > div > div:nth-child(1) > div > div > ' \
                      'div.s-column.pdp-product-title__left > div:nth-child(1) > h1 > a '
    title2_selector = '#wrap > div > div > div.pdp__mobile--new.pdp__redesign > div > div.pdp-mobile > div > div > ' \
                      'div.s-row.pdp-header__right > div > div:nth-child(1) > div > div > ' \
                      'div.s-column.pdp-product-title__left > div:nth-child(2) > h2 '
    title = '브랜드:' + soup.select_one(title1_selector).text + ',상품명:' + soup.select_one(title2_selector).text;

    desc_selector = '#wrap > div > div > div.pdp__mobile--new.pdp__redesign > div > div.pdp-mobile > div > div > ' \
                    'div.s-row.pdp-header__right > div > div:nth-child(2) > div > div > div:nth-child(2) > div > div > ' \
                    'div > div > div:nth-child(2) > div > p:nth-child(2) '
    desc = soup.select_one(desc_selector).text

    # * inv 를 넣는경우는 celenium을 활용해야 해야 할 수도 있음. 실제 장바구니 카트를 넣어보면서 나머지 수량을 체크함.
    article = {'userid': userid, 'url': url, 'title': title, 'desc': desc, 'img': img, 'site': site, 'price': price,
               'wprice': wprice, 'comment': comment}

    # 3. mongoDB에 데이터 넣기
    db.article.insert_one(article)

    return jsonify({'result': 'success', 'msg': '해당 내용이 저장되었습니다!'})


@app.route('/viewcard', methods=['GET'])
def read_articles():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기(Read)
    print("herehere2")
    userid=request.args.get("userid_give")
    print("xx:"+userid)
    result = list(db.articles.find({'userid':userid}, {'_id': 0,'userid':0}))
    # 2. articles라는 키 값으로 articles 정보 보내주기
    return jsonify({'result': 'success', 'msg': 'GET 연결되었습니다!', 'article': result})


# ** 로그인 및 회원가입 분 **
# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'apple'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib


#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    print("wow wow ");

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    print("wow wow 1.5");

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    print("wow wow2 ");

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        print("wow wow3 ");

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    # 토큰을 주고 받을 때는, 주로 header에 저장해서 넘겨주는 경우가 많습니다.
    # header로 넘겨주는 경우, 아래와 같이 받을 수 있습니다.
    token_receive = request.headers['token_give']

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick'], 'userid': userinfo['id']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
