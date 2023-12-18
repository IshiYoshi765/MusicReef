from flask import Flask, render_template, request, redirect, url_for, session,flash, jsonify, request
import db, random,string
import tags
from datetime import timedelta
from db import get_connection

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

# @app.route("/admin", methods=["GET"])
# def index():
#     return render_template("top_page.html")

@app.route("/admin", methods=["GET"])
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
    otp = db.get_otp_pass()
    
    print(otp)
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

@app.route("/pass_reset", methods=['GET'])
def pass_reset():
    return render_template('pass_reset.html')

@app.route('/pass_reset_exe', methods=["POST"])
def pass_reset_exe():
    mail = request.form.get("mail")
    session['user'] = mail
    db.save_otp(mail)
    return render_template('check_one_pass.html', mail=mail)


@app.route("/check_one_pass", methods=["POST"])
def check_one_pass():
    mail = session['user']
    print(mail)
    otp_code = request.form.get("otp")
    print(otp_code)
    if db.verify_otp(mail,otp_code):
        return render_template("change_password.html", mail=mail)
    else:
        flash('ワンタイムパスワードが正しくありません')
    return redirect(url_for('pass_reset'))

@app.route("/change_password", methods=["POST"])
def change_password():
    password = request.form.get("new_pass")
    confirm_pass = request.form.get("confirm_password")
    mail = session['user']
    
    print(password)
    print(confirm_pass)
    
    if password == confirm_pass:
        db.update_pass(password,mail)
        print('a')
    else:
        msg = 'パスワード不一致でした・・・'
        return render_template('change_password.html', msg=msg) 
        print('b')
    
    if request.method == 'POST':
        msg = 'パスワード変更がされました'
        print('c')
        return redirect(url_for('login'))
    return render_template('change_password.html', msg=msg)


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
        
        return redirect(url_for("mypage"))
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
    tag = tags.select_tag()
    return render_template('music_register.html',music=tag)

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
    return redirect(url_for('music_register'))


@app.route("/music_edit/<int:id>",methods=["GET"])
def music_edit(id):
    music = db.get_music_and_check(id)
    sound = tags.select_tag()
    return render_template('music_edit.html',music = music,sound=sound)

@app.route("/music_edit_exe/<int:id>" ,methods=["POST"])
def music_edit_exe(id):
    name = request.form.get("name")
    genre = request.form.get("genre")
    detail = request.form.get("detail")
    length = request.form.get("length")
    composer = request.form.get("composer")
    source = request.form.get("source")
    URL = request.form.get("url")
    tags_list = request.form.getlist("tag_name")
    #music_id = request.form.get("music_id")
    db.edit_music(name,genre,detail,length,composer,source,URL,tags_list,id)
    return redirect(url_for("mypage"))
    

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

@app.route('/admin_edit')
def admin_edit():
    if "user" in session:
        return render_template('admin_edit.html')
    else:
        return render_template('index.html')

@app.route('/admin_edit_exe', methods=['POST'])
def admin_edit_exe():
    name = request.form.get("name")
    mail = session["user"]
    password = request.form.get("password")
    new_pass = request.form.get("newPassword")
    check_pass = request.form.get("Checkpassword")
    
    if name:
        id = db.get_id(mail)
        db.admin_edit(name,id)
        return render_template("admin_edit.html")
    
    if db.login(mail,password):
        if new_pass == check_pass:
            db.update_pass(new_pass,mail)
            return redirect(url_for("admin_edit"))
    else:
        msg = "現在のパスワードと一致しません"
        return render_template("admin_edit.html", msg=msg)

@app.route("/admin_delete_exe", methods=['POST'])
def admin_delete_exe():
    id = request.form.get("id")
    db.delete_user(id)
    admin_list = db.admin_select_all()
    return render_template('route_admin_list.html',admin=admin_list)

@app.route("/list_of_review", methods=['GET'])
def list_of_review():
    review_all = db.list_of_review()
    return render_template('list_of_review.html', reviews=review_all)
    
@app.route('/search_result', methods=["POST"])
def search_result():
    name=request.form.get("name")
    genre = request.form.get("genre")
    #sort = request.args.get('sort')
    #time = request.args.get('time')
    #site = request.args.get('site')
    
    music_list=db.search_music(name,genre)
    
    
    # search_result.htmlに条件と結果を渡して表示
    
    #return render_template('search_result.html', genre=genre, sort=sort, time=time, site=site)
    return render_template('search_result.html', music=music_list,genre=genre,name=name)
    
@app.route("/delete_review/<int:review_id>", methods=['GET'])
def delete_review(review_id):
    db.delete_review(review_id)
    return redirect(url_for('list_of_review'))

@app.route('/', methods=["GET"])
def user_top():
    recent_music = db.get_recent_music()
    week_top_songs = db.get_top_songs_weekly()
    month_top_songs = db.get_top_songs_monthly()
    
    recent_music_id = recent_music[0][0] if recent_music else None

    average_rating = db.get_average_rating_for_music(recent_music_id) if recent_music_id else None
    return render_template('user_top.html', recent_music=recent_music, week_top_songs=week_top_songs, month_top_songs=month_top_songs, average_rating=average_rating)
  
@app.route('/download/<int:music_id>', methods=['GET'])
def download_music(music_id):
    
    db.increment_access_count(music_id)

    
    music_url = db.get_music_url(music_id)

    return redirect(music_url)


#----------------------------------------------------音源口コミモーダル-------------------------------------------------------------
@app.route('/api/musicinfo', methods=['GET'])
def get_music_info_and_reviews():
    music_id = request.args.get('music_id')
    music_info = get_music_and_check(music_id)
    reviews = get_reviews_for_music(music_id)
    return jsonify({"music": music_info, "reviews": reviews})

def get_music_and_check(music_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM music WHERE music_id = %s;", (music_id,))
        music_info = cursor.fetchone()
        return music_info
    finally:
        cursor.close()
        connection.close()

def get_reviews_for_music(music_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM music_review WHERE music_id = %s;", (music_id,))
        reviews = cursor.fetchall()
        return reviews
    finally:
        cursor.close()
        connection.close()
        

@app.route("/delete_review1/<int:review_id>", methods=['GET'])
def delete_review_endpoint(review_id):
    result = delete_review(review_id)

    return jsonify(result)

def delete_review(review_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM music_review WHERE id = %s;", (review_id,))
        connection.commit()
        return {"message": "口コミが削除されました"}
    finally:
        cursor.close()
        connection.close()
#------------------------------------------------------------------------------------------------------------------------------------


@app.route('/review/<int:music_id>')
def review(music_id):
    
    music_info = db.get_music_by_id(music_id)
    get_info = db.get_review_by_music_id(music_id)
    return render_template('comment.html', music_info=music_info, music_id=music_id, get_info=get_info)
        
@app.route('/post_comment', methods=['GET', 'POST'])
def post_comment():
    if request.method == 'POST':
        # フォームからのデータを取得
        star_str = request.form.get('rating')
        review = request.form.get('review')
        music_id = request.form.get('music_id')

        if star_str is not None and star_str.replace('.', '', 1).isdigit():
            star = float(star_str)

            # db モジュールの insert_comment メソッドを呼び出し
            count = db.insert_comment(star, review, music_id)

            if count == 1:
                msg = '音源が登録されました'
                get_info = db.get_review_by_music_id(music_id)
                return redirect(url_for('review', music_id=music_id, get_info=get_info))
            else:
                error = '音源の登録に失敗しました。'
                return render_template('comment.html', error=error)
        else:
            error = '評価が不正です。'
            return render_template('comment.html', error=error)

    return render_template('comment.html')



if __name__ == "__main__":
    app.run(debug=True)
    
