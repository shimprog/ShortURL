from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError
import string
import sqlite3
from urllib.parse import urlparse 
str_encode = str.encode
from string import ascii_lowercase
from string import ascii_uppercase
import base64

app = Flask(__name__)
host = 'http://localhost:5000/'


def table_check():
    create_table = """
        CREATE TABLE IF NOT EXISTS WEB_URL(
        ID INTEGER PRIMARY KEY,
        URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('mini.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
            conn.commit()
        except OperationalError:
            pass


def toBase62(num, b=62):
    if b <= 0 or b > 62:
        return 0
    base = string.digits + ascii_lowercase + ascii_uppercase
    r = num % b
    res = base[r]
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res


def toBase10(num, b=62):
    base = string.digits + ascii_lowercase + ascii_uppercase
    limit = len(num)
    res = 0
    for i in range(limit):
        res = b * res + base.find(num[i])
    return res

table_check()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = str_encode(request.form.get('url'))
        if urlparse(original_url).scheme == '':
            url = 'http://' + original_url
        else:
            url = original_url
        with sqlite3.connect('mini.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO WEB_URL (URL) VALUES (?)',
                [base64.urlsafe_b64encode(url)]
            )

            conn.commit()

            encoded_string = toBase62(res.lastrowid)

        return render_template('index.html', short_url=host + encoded_string)
        
    return render_template('index.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded = toBase10(short_url)
    url = host
    try: 
        with sqlite3.connect('mini.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute('SELECT URL FROM WEB_URL WHERE ID=?', [decoded])
            try:
                short = res.fetchone()
                if short is not None:
                    url = base64.urlsafe_b64decode(short[0])
            except Exception as e:
                print(e)
        return redirect(url.decode('utf-8'))


    except OverflowError as e:
        print(str(e))


if __name__ == '__main__':
    app.run(debug=True)
