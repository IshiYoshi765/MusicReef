from flask import Flask, render_template, request, redirect, url_for, session
import db, random,string
import tags
from datetime import timedelta

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

@app.route("/", methods=["GET"])
def index():
    msg = request.args.get("msg")
    if msg == None:
        return render_template("index.html")
    else:
        return render_template("index.html", msg=msg)


def check_password(mail, password):
    # 仮パスワードでログインしたかどうかのチェック
    stored_password = db.temp_password(mail)
    salt = db.set_salt(mail)
    hash_pw = db.get_hash(password,salt)
    
    return hash_pw == stored_password

def password_changed(mail):
    # パスワードが変更されたかどうかのチェック
    return db.password_flag(mail)


@app.route('/tag')
def tag():
    return render_template('tag.html')

@app.route('/insert_tag',methods=['POST'])
def insert_tag():
    genre1 = request.form.get('genre1')
    tag_name = request.form.get('tag_name')
    genre = int(genre1)
    
    tags.insert_tags(genre,tag_name)
    return render_template('tag.html')

if __name__ == "__main__":
    app.run(debug=True)
