from flask import Flask, jsonify, render_template
import psycopg2

app = Flask(__name__)

def get_db_content():
    conn = psycopg2.connect(
        host="target_db",
        database="target_db",
        user="target_user",
        password="target_password"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs_table_joined")  # replace "your_table" with your actual table name
    rows = cur.fetchall()
    return rows

@app.route('/')
def home():
    content = get_db_content()
    return render_template('index.html', content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)