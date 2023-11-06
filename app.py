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
        return render_template("login.html")
    else:
        return render_template("login.html", msg=msg)


def check_password(mail, password):
    # 仮パスワードでログインしたかどうかのチェック
    stored_password = db.temp_password(mail)
    salt = db.set_salt(mail)
    hash_pw = db.get_hash(password,salt)
    
    return hash_pw == stored_password

def password_changed(mail):
    # パスワードが変更されたかどうかのチェック
    return db.password_flag(mail)

@app.route("/", methods=["POST"])
def login():
    mail = request.form.get("mail")
    password = request.form.get("password")
    if db.login(mail,password):
                
        if check_password(mail, password):
            user = password_changed(mail)
            bool = db.password_flag(mail)
            print(bool)
     # ログイン判定
            if bool:
                   session["user"] = mail
                   return redirect(url_for("admin_update"))
            else:
                session["user"] = mail  # session にキー：'user', バリュー:True を追加
                session.permanent = True  # session の有効期限を有効化
                app.permanent_session_lifetime = timedelta(minutes=5)  # session の有効期限を 5 分に設定
                return redirect(url_for("mypage"))
        else:
           
            return redirect(url_for("mypage"))
    else:
        error = "メールアドレスまたはパスワードが違います。"

        # dictで返すことでフォームの入力量が増えても可読性が下がらない。
        input_data = {"mail": mail, "password": password}
        return render_template("login.html", error=error, data=input_data)


@app.route("/mypage", methods=["GET"])
def mypage():
    # session にキー：'user' があるか判定
    if "user" in session:
        return render_template("index.html")  # session があれば index.html を表示
    else:
        return redirect(url_for("index"))  # session がなければログイン画面にリダイレクト

@app.route("/logout")
def logout():
    session.pop("user", None)  # session の破棄
    return redirect(url_for("index"))  # ログイン画面にリダイレクト


@app.route("/register")
def register_form():
    return render_template("register.html")


@app.route("/register_exe", methods=["POST"])
def register_exe():
    mail = request.form.get("mail")
    password = request.form.get("password")
  
    if mail == "":
        error = "メールアドレスが未入力です。"
        return render_template("register.html", error=error)
    
    ##if password == "":
    ##    error = "パスワードが未入力です。"
    ##    return render_template("register.html", error=error)

    count = db.insert_user(mail)

    if count == 1:
        msg = "登録が完了しました。"
        return redirect(url_for("index", msg=msg))
    else:
        error = "登録に失敗しました。"
        return render_template("register.html", error=error)


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
