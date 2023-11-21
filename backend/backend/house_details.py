from flask import Flask, request, render_template, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from house_update import House, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:peter0107@database-1.cc0lokhfxaeb.us-east-2.rds.amazonaws.com:3306/software_database'
db.init_app(app)

# /house/details/<house_id> 정의
@app.route('/house/details/<house_id>', methods=['GET'])
def get_house_details(house_id):
    house = House.query.filter_by(house_id=house_id).first()

    if house:
        return render_template('house_details.html', house=house)
    else:
        return jsonify({'error': 'House not found'}), 404

# Main page with form to input house_id
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        house_id = request.form.get('house_id')
        return redirect(f'/house/details/{house_id}')
    return render_template('house_details_form.html')

if __name__ == '__main__':
    app.run(debug=True)
