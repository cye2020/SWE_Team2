from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
import math
import json
import logging
from models import House
# Configure logging
logging.basicConfig(level=logging.ERROR)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:peter0107@database-1.cc0lokhfxaeb.us-east-2.rds.amazonaws.com:3306/software_database'
db = SQLAlchemy(app)



def crawl_each_region(url): #각 동별 매물목록 url을 받아서 크롤링

    # 크롬 옵션 설정 및 드라이버 설정
    chrome_options = Options()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36" #우회용
    chrome_options.add_argument('user-agent=' + user_agent)
    # chrome_options.add_argument('--headless') #창 안띄우고 크롤링, 우회시에는 사용 안하는 것이 좋음
    driver = webdriver.Chrome(options=chrome_options)

    #학생 수요에 맞는 설정
    house_type="OPST:VL:DDDGG:SGJT:OR:GSW" #오피스텔,빌라,단독/다가구,상가주택,원룸,고시원
    pay_type="B1:B2:B3" #전세/월세/단기임대 매물 확인
    
    #각 동 url 설정
    if url == "율전동":
        url_cluster = "https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=4111113200&rletTpCd=OPST%3AVL%3AOBYG%3ASGJT%3AOR%3AGSW&tradTpCd=B1%3AB2%3AB3&z=14&lat=37.297618&lon=126.971492&btm=37.2692772&lft=126.9335978&top=37.3259481&rgt=127.0093862&pCortarNo=14_4111113200&addon=COMPLEX&bAddon=COMPLEX&isOnlyIsale=false"
    #     "https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=4111113200&rletTpCd=OPST%3AVL%3ADDDGG%3ASGJT%3AOR%3AGSW&tradTpCd=B1%3AB2%3AB3&z=14&lat=37.297618&lon=126.971492&btm=37.2695846&lft=126.9305937&top=37.325641&rgt=127.0123903&pCortarNo=14_4111113200&addon=COMPLEX&bAddon=COMPLEX&isOnlyIsale=false"
    elif url == "천천동":
        url_cluster = "https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=4111113300&rletTpCd=OPST%3AVL%3AOBYG%3ASGJT%3AOR%3AGSW&tradTpCd=B1%3AB2%3AB3&z=14&lat=37.295833&lon=126.978263&btm=37.2674915&lft=126.9403688&top=37.3241638&rgt=127.0161572&pCortarNo=14_4111113200&addon=COMPLEX&bAddon=COMPLEX&isOnlyIsale=false"
        # "https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=4111113300&rletTpCd=OPST%3AVL%3ADDDGG%3ASGJT%3AOR%3AGSW&tradTpCd=B1%3AB2%3AB3&z=14&lat=37.295833&lon=126.978263&btm=37.2661596&lft=126.9394675&top=37.3254947&rgt=127.0170585&pCortarNo=&addon=COMPLEX&isOnlyIsale=false"
    else:
        print("Invalid input")
        return

    #각 동 매물 목록 크롤링
    driver.get(url_cluster)
    json_data = driver.execute_script("return JSON.parse(document.body.innerText)")
    values = json_data['data']['ARTICLE']
    z = json_data['z']
    cortarNo = json_data['cortar']['detail']['cortarNo']

    #해당 동의 매물 세부정보 크롤링
    json_data_article = []
        
    for v in values:
        lgeo = v['lgeo']
        count = v['count']
        lat = v['lat']
        lon = v['lon']

        len_pages = count / 20 + 1
        for idx in range(math.ceil(len_pages)):
            url_article = "https://m.land.naver.com/cluster/ajax/articleList?""itemId={}&mapKey=&lgeo={}&showR0=&" \
                    "rletTpCd={}&tradTpCd={}&z={}&lat={}&""lon={}&totCnt={}&cortarNo={}&page={}" \
                        .format(lgeo, lgeo, house_type, pay_type, z, lat, lon, count, cortarNo, idx)
            driver.get(url_article)

            json_data_article.append(driver.execute_script("return JSON.parse(document.body.innerText)"))

    driver.quit()

    return json_data_article

def crawl_main():

    content = []
    content.append(crawl_each_region("율전동"))
    content.append(crawl_each_region("천천동"))

    return content

def process_crawled_data(content):

    item_list = []
    img_default_url = "https://landthumb-phinf.pstatic.net"

    # 데이터 변환
    for dong in content:
        for idx in range(len(dong)):
            body = dong[idx]['body']

            if not body:
                continue

            for item in body:
                new_item = House(
                    house_id=item.get('atclNo', 0),
                    house_type=item.get('rletTpNm', ''),
                    pay_type=item.get('tradTpNm', ''),
                    lat=item.get('lat', 0.0),
                    lon=item.get('lng', 0.0),
                    feature=item.get('atclFetrDesc', None),
                    direction=item.get('direction', ''),
                    floor=item.get('flrInfo', None),
                    prc=item.get('prc', 0),
                    rentprc=item.get('rentPrc', 0),
                    space1=item.get('spc1', None),
                    space2=item.get('spc2', None),
                    taglist=item.get('tagList', {}),
                    imgurl=img_default_url + item.get('repImgUrl', '') if item.get('repImgUrl') else None
                )
                item_list.append(new_item)

    return item_list

def update_database(item_list):
    
    try:
        with app.app_context():
            for item in item_list:
                existing_item = House.query.filter_by(house_id=item.house_id).first()

                if existing_item:
                    # 기존 아이템 업데이트
                    existing_item.house_type = item.house_type
                    existing_item.pay_type = item.pay_type
                    existing_item.lat = item.lat
                    existing_item.lon = item.lon
                    existing_item.feature = item.feature
                    existing_item.direction = item.direction
                    existing_item.floor = item.floor
                    existing_item.prc = item.prc
                    existing_item.rentprc = item.rentprc
                    existing_item.space1 = item.space1
                    existing_item.space2 = item.space2
                    existing_item.taglist = item.taglist
                    existing_item.imgurl = item.imgurl

                else:
                    #새로운 아이템 추가
                    db.session.add(item)

            db.session.commit()
    except Exception as e:
        logging.error(f"Error updating database: {e}")
        db.session.rollback()
    finally:
        db.session.close()

@app.route('/')
def index():
    return jsonify({"message": "Update server is running"})

@app.route('/house/update', methods=['POST'])
def update():
    # 크롤링
    content = crawl_main()

    # 데이터 변환
    item_list = process_crawled_data(content)

    # 데이터베이스 업데이트
    update_database(item_list)

    return jsonify({"message": "Data updated successfully"})

if __name__ == '__main__':
    app.run(debug=True)