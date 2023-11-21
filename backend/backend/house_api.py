from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from house_update import House, db
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:peter0107@database-1.cc0lokhfxaeb.us-east-2.rds.amazonaws.com:3306/software_database'
db.init_app(app)

# /house/filter 정의
@app.route('/house/filter', methods=['GET'])
def filter_houses():
    try:
        # "reset"으로 모든 필터를 초기화하고 전체 항목을 반환
        if 'reset' in request.args:
            query = House.query
        
        else:
            # 필터 기준을 받아오기
            house_type_filters = request.args.getlist('house_type')
            pay_type_filters = request.args.getlist('pay_type')
            prc_filter = request.args.get('prc_lt')
            rentprc_filter = request.args.get('rentprc_lt')
            space2_filter = request.args.get('space2_lt')
            taglist_filters = request.args.getlist('taglist')
            direction_filters = request.args.getlist('direction')

            # 필터 조건에 따라 쿼리 작성
            query = House.query

            # 중복 선택 가능 영역
            if house_type_filters:
                query = query.filter(or_(*[House.house_type == house_type for house_type in house_type_filters]))
            if pay_type_filters:
                query = query.filter(or_(*[House.pay_type == pay_type for pay_type in pay_type_filters]))
            if direction_filters:
                query = query.filter(or_(*[House.direction == direction for direction in direction_filters]))
            if taglist_filters:
                query = query.filter(or_(*[House.taglist.contains([tag]) for tag in taglist_filters]))

            # 단일 선택(숫자값 이하)
            if prc_filter:
                query = query.filter(House.prc <= int(prc_filter))
            if rentprc_filter:
                query = query.filter(House.rentprc <= int(rentprc_filter))
            if space2_filter:
                query = query.filter(House.space2 <= int(space2_filter))

            # 정렬 기준에 따라 쿼리 작성
            if 'sort' in request.args:
                sort_by = request.args.get('sort')
                if sort_by == 'prc': # /filter?sort=prc&order=(ascend)or(descend)
                    # prc가 0보다 큰 경우에만 정렬 수행, prc가 0인 경우 전세임.
                    query = query.filter(House.prc > 0)
                    query = query.order_by(House.prc.asc() if request.args.get('order') != 'descend' else House.prc.desc())
                elif sort_by == 'rentprc':
                    query = query.order_by(House.rentprc.asc() if request.args.get('order') != 'descend' else House.rentprc.desc())
                elif sort_by == 'space2':
                    query = query.order_by(House.space2.asc() if request.args.get('order') != 'descend' else House.space2.desc())

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
            print(result)

        return render_template('a.html', houses=result)

    except Exception as e:
        return jsonify({'error': str(e)})

# / 주소로 접근 시 /house로 리다이렉트
@app.route('/')
def index():
    return redirect(url_for('house'))

@app.route('/house', methods=['GET'])
def house():
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
                'space1': house.space1,
                'space2': house.space2,
                'taglist': house.taglist,
                'imgurl': house.imgurl
            })
        app.logger.info("전체 매물 정보를 가져왔습니다.")

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)