import pymysql
from flask import Flask


# create the app
app = Flask(__name__)


try:
    db = pymysql.connect(
        host='database-1.cc0lokhfxaeb.us-east-2.rds.amazonaws.com',
        port=3306,
        user='root',
        passwd='peter0107',
        db='software_database',
        charset='utf8'
    )
    cursor = db.cursor()

except pymysql.err.InterfaceError as e:
    print(f"Error connecting to MySQL: {e}")



@app.route('/')
def testdb():
    return "hello world"
        

if __name__ == '__main__':
    app.run(debug=True)