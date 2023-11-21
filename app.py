from flask import Flask, render_template, request, redirect, url_for, session
import db, random,string
import tags
from datetime import timedelta

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

# @app.route("/", methods=["GET"])
# def index():
#     return render_template("top_page.html")

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
        sound_list = db.music_list()
        return render_template("index.html",music=sound_list)  # session があれば index.html を表示
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

@app.route("/admin_update")
def admin_update():
    if "user" in session:
        return render_template("admin_update.html")
    else:
        return render_template('login.html')

@app.route("/admin_update_exe", methods=["POST"])
def admin_update_exe():
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    
    # PWが不一致の場合はエラーで戻す
    
    if "user" in session:
        mail = session["user"]
    else:
        mail = ""

    
    
    if password == confirm_password:
        db.update_pass(password, mail)
        id = db.get_id(mail)
        db.set_update_flag(id)
        
        return render_template("index.html")
    else:
        error = "パスワードが一致しません。"
        return render_template("admin_update.html", error=error)

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

@app.route("/music_register")
def music_register():
    return render_template('music_register.html')

@app.route("/music_regi_exe", methods=["POST"])
def music_regi_exe():
    name = request.form.get("name")
    genre = request.form.get("genre")
    detail = request.form.get("detail")
    length = request.form.get("length")
    composer = request.form.get("composer")
    source = request.form.get("source")
    URL = request.form.get("url")
    tags_list = request.form.getlist("tag_name")
    db.insert_music(name,genre,detail,length,composer,source,URL,tags_list)
    return render_template("music_register.html")

@app.route("/music_edit/<int:id>",methods=["GET"])
def music_edit(id):
    music = db.get_music_and_check(id)
    
    return render_template('music_edit.html',music = music)

@app.route("/music_edit_exe/<int:id>" ,methods=["POST"])
def music_edit_exe(id):
    name = request.form.get("name")
    genre = request.form.get("genre")
    detail = request.form.get("detail")
    length = request.form.get("length")
    composer = request.form.get("composer")
    source = request.form.get("source")
    URL = request.form.get("url")
    # tags_list = request.form.getlist("tag_name")
    #music_id = request.form.get("music_id")
    db.edit_music(name,genre,detail,length,composer,source,URL,id)
    return render_template("index.html")
    

@app.route("/music_delete", methods=['GET'])
def music_delete(music_id):
    sond = db.get_music_and_check(music_id)
    print(sond)
    return render_template('index.html',music=sond)

@app.route("/delete_exe", methods=['POST'])
def delete_exe():
    music_id = request.form.get("music_id")
    print(music_id)
    db.delete_music(music_id)
    sound_list = db.music_list()
    return render_template('index.html',music=sound_list)

@app.route("/admin_list", methods=['GET'])
def admin_list():
    admin_all = db.admin_select_all()
    return render_template('route_admin_list.html',admins = admin_all)

    
@app.route('/search_result', methods=["POST"])
def search_result():
    name=request.form.get("name")
    #genre = request.args.get('genre')
    #sort = request.args.get('sort')
    #time = request.args.get('time')
    #site = request.args.get('site')
    
    music_list=db.search_music(name)
    
    # search_result.htmlに条件と結果を渡して表示
    
    #return render_template('search_result.html', genre=genre, sort=sort, time=time, site=site)
    return render_template('search_result.html', music=music_list)
    
if __name__ == "__main__":
    app.run(debug=True)
    
