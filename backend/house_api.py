from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from house_update import House, db
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:peter0107@database-1.cc0lokhfxaeb.us-east-2.rds.amazonaws.com:3306/software_database'
db.init_app(app)

# /house/filter 필터링하는 부분 
@app.route('/house/filter', methods=['GET'])
def filter_houses():
    try:
        if 'reset' in request.args:
            # 전체 데이터를 반환
            all_houses = House.query.all()
            result = [
                {
                    'house_id': house.house_id,
                    'house_type': house.house_type,
                    'pay_type': house.pay_type,
                    'lat': house.lat,
                    'lon': house.lon,
                    'feature': house.feature,
                    'direction': house.direction,
                    'floor': house.floor,
                    'prc': house.prc,
                    'rentprc': house.rentprc,
                    'space1': house.space1,
                    'space2': house.space2,
                    'taglist': house.taglist,
                    'imgurl': house.imgurl
                }
                for house in all_houses
            ]
        
        else:
           # 필터 기준을 받아오기
            house_type_filters = request.args.getlist('house_type[]')
            print(f"Filters: {house_type_filters}")
            print(f"Args: {request.args}")
            pay_type_filters = request.args.getlist('pay_type[]')
            prc_filter = request.args.get('prc_lt[]')
            rentprc_filter = request.args.get('rentprc_lt[]')
            space2_filter = request.args.get('space2_lt[]')
            taglist_filter = request.args.get('taglist[]')
            direction_filter = request.args.get('direction[]')

            # 필터 조건에 따라 쿼리 작성
            query = House.query

            # 중복 선택 가능 영역
            if house_type_filters:
                query = query.filter(House.house_type.in_(house_type_filters))
                print(query)
            if pay_type_filters:
                query = query.filter(House.pay_type.in_(pay_type_filters))

            # 단일 선택(문자열)
            if direction_filter:
                query = query.filter(House.direction == direction_filter)
            if taglist_filter:
                query = query.filter(House.taglist.contains([taglist_filter]))

            # 단일 선택(숫자값 이하)
            if prc_filter:
                query = query.filter(House.prc <= int(prc_filter))
            if rentprc_filter:
                query = query.filter(House.rentprc <= int(rentprc_filter))
            if space2_filter:
                query = query.filter(House.space2 <= int(space2_filter))

            # 정렬 기준에 따라 쿼리 작성
            if 'sort' in request.args:
                sort_by = request.args.get('sort[]')
                if sort_by == 'prc': # /filter?sort=prc&order=(ascend)or(descend)
                    # prc가 0보다 큰 경우에만 정렬 수행, prc가 0인 경우 전세임.
                    query = query.filter(House.prc > 0)
                    query = query.order_by(House.prc.asc() if request.args.get('order[]') != 'descend' else House.prc.desc())
                elif sort_by == 'rentprc':
                    query = query.order_by(House.rentprc.asc() if request.args.get('order[]') != 'descend' else House.rentprc.desc())
                elif sort_by == 'space2':
                    query = query.order_by(House.space2.asc() if request.args.get('order[]') != 'descend' else House.space2.desc())

            # 필터된 매물 정보를 JSON 형태로 변환하여 반환
            result = []
            filtered_houses = query.all()
            for house in filtered_houses:
                result.append({
                    'house_id': house.house_id,
                    'house_type': house.house_type,
                    'pay_type': house.pay_type,
                    'lat': house.lat,
                    'lon': house.lon,
                    'feature': house.feature,
                    'direction': house.direction,
                    'floor': house.floor,
                    'prc': house.prc,
                    'rentprc': house.rentprc,
                    'space1': house.space1,
                    'space2': house.space2,
                    'taglist': house.taglist,
                    'imgurl': house.imgurl
                })
            app.logger.info(f"받은 매개변수: {request.args}")
            print(query)
            print("filtered")

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})

#매물 세부정보 페이지 
@app.route('/house/<house_id>', methods=['GET'])
def get_house_details(house_id):
    house = House.query.filter_by(house_id=house_id).first()

    if house:
        return render_template('house_details.html', house=house)
    else:
        return jsonify({'error': 'House not found'}), 404 

@app.route('/house/init', methods=['GET'])
def initial():
    try:
        # 전체 주소를 가져오기
        all_houses = House.query.all()

        # 모든 주소를 JSON 형태로 변환하여 반환
        result = []
        for house in all_houses:
            result.append({
                'house_id': house.house_id,
                'house_type': house.house_type,
                'pay_type': house.pay_type,
                'lat': house.lat,
                'lon': house.lon,
                'feature': house.feature,
                'direction': house.direction,
                'floor': house.floor,
                'prc': house.prc,
                'rentprc': house.rentprc,
            })
        app.logger.info("전체 매물 정보를 가져왔습니다.")

        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/house')
def house():
    return render_template('real.html') 

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)