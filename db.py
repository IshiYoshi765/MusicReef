import os, psycopg2, string, random, hashlib
import smtplib 
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os



def get_connection():
    url = os.environ["DATABASE_URL"]
    connection = psycopg2.connect(url)
    return connection


def get_salt():
    charset = string.ascii_letters + string.digits

    salt = "".join(random.choices(charset, k=30))
    return salt

def get_random_pass(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
    
def get_hash(password, salt):
    b_pw = bytes(password, "utf-8")
    b_salt = bytes(salt, "utf-8")
    hashed_password = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 1246).hex()
    return hashed_password

def send_email(to_email, password):
    # ここでメール送信の設定を行います
    from_email = os.environ['MAIL_ADDRESS']  # 送信元のメールアドレス
    email_password = os.environ['MAIL_PASS']
    
    subject = "新規登録完了"
    body = f"ご登録ありがとうございます。パスワードは {password} です。"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, email_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("メールが送信されました。")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
    
def insert_user(mail):
    
    sql = "INSERT INTO admin VALUES(default, %s, %s, %s, %s, %s)"

    
    random_pass = get_random_pass()
    send_email(mail, random_pass)

    salt = get_salt()
    hashed_password = get_hash(random_pass, salt)

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, ('',mail, hashed_password, salt,True))
        count = cursor.rowcount  # 更新件数を取得
        connection.commit()

    except psycopg2.DatabaseError:
        count = 0

    finally:
        cursor.close()
        connection.close()

    return count


def login(mail, password):
    sql = "SELECT hashed_password, salt FROM admin WHERE mail = %s"
    flg = False

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(sql, (mail,))
        user = cursor.fetchone()

        if user != None:
            # SQLの結果からソルトを取得
            salt = user[1]

            # DBから取得したソルト + 入力したパスワード からハッシュ値を取得
            hashed_password = get_hash(password, salt)

            # 生成したハッシュ値とDBから取得したハッシュ値を比較する
            if hashed_password == user[0]:
                flg = True

    except psycopg2.DatabaseError:
        flg = False

    finally:
        cursor.close()
        connection.close()

    return flg

def cal_length_num(length):
    # lengthを時間と分に分解
    hours, minutes = map(int, length.split(':'))

    # 時間に基づいてlength_numberを計算
    if hours == 0 and minutes >= 0 and minutes <= 59:
        return 0
    elif hours == 1 and minutes >= 0 and minutes <= 59:
        return 1
    elif hours == 2 and minutes >= 0 and minutes <= 59:
        return 2
    elif hours == 3 and minutes >= 0 and minutes <= 59:
        return 3
    elif hours == 4 and minutes >= 0 and minutes <= 59:
        return 4
    elif hours == 5 and minutes >= 0 and minutes <= 59:
        return 5
    elif hours >= 6:
        return 6
    else:
        # エラー処理が必要な場合はここに記述
        return -1
    

def insert_music(name,genre,detail,length,composer,source,URL,tags_list):
    # lengthが指定されるまで待つ
    while length is None or length == "":
        length = input("Please enter the length (format: HH:MM): ")
    length_number = cal_length_num(length)
    sql = "INSERT INTO music VALUES(default, %s, %s, %s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,default) RETURNING music_id"

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql,(name,genre,detail,length,length_number,composer,source,URL))
    music_id = cursor.fetchone()[0]
    print(music_id)
    for tag_name in tags_list:
        print(tags_list)
        # タグが存在するか確認
        sql = "SELECT tag_id FROM tags WHERE tag_name = %s"
        cursor.execute(sql,(tag_name,))
        tag_id = cursor.fetchone()
        if tag_id:
            tag_id = tag_id[0]
            print(tag_id)
            sql = "INSERT INTO music_tags VALUES (%s,%s)"
            cursor.execute(sql, (music_id, tag_id))
            print(music_id)
    connection.commit()

    cursor.close()
    connection.close()
    
def edit_music(name,genre,detail,length,composer,source,URL,id):
    # lengthが指定されるまで待つ
    # while length is None or length == "":
    #     length = input("Please enter the length (format: HH:MM): ")
    # length_number = cal_length_num(length)
    sql = "UPDATE music SET name = %s,genre = %s,detail = %s,length = %s,composer = %s,source = %s,URL = %s WHERE music_id = %s"

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql,(name,genre,detail,length,composer,source,URL,id))
    # music_id = cursor.fetchone()[0]
    # print(music_id)
    # for tag_name in tags_list:
    #     print(tags_list)
    #     # タグが存在するか確認
    #     sql = "SELECT tag_id FROM tags WHERE tag_name = %s"
    #     cursor.execute(sql,(tag_name,))
    #     tag_id = cursor.fetchone()
    #     if tag_id:
    #         tag_id = tag_id[0]
    #         print(tag_id)
    #         sql = "INSERT INTO music_tags VALUES (%s,%s)"
    #         cursor.execute(sql, (music_id, tag_id))
    #         print(music_id)
    connection.commit()

    cursor.close()
    connection.close()

# def get_tags(genre):
#     connection = get_connection()
#     cursor = connection.cursor()
#     sql = "SELECT tag_name FROM tags WHERE genre = %s"
#     cursor.execute(sql,(genre,))
#     tags_list = [row[0] for row in cursor.fetchall()]
#     cursor.close()
#     connection.close()
#     return tags_list

def delete_music(music_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "delete from music where music_id=%s"

    cursor.execute(sql, (music_id,))
    connection.commit()

    cursor.close()
    connection.close()

#音源の検索
def search_music(name):
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT * FROM music WHERE name LIKE %s"

    name2 = "%" + name + "%"

    cursor.execute(sql, (name2,))

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows

def get_music_and_check(id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT * FROM music WHERE music_id = %s"
    cursor.execute(sql, (id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    if row:
        music = {
            "music_id": row[0],
            "name": row[1],
            "genre": row[2],
            "detail": row[3],
            "length": row[4],
            "length_number": row[5],
            "composer": row[6],
            "source": row[7],
            "URL": row[8],
            "date_register": row[9],
            "update_time": row[10],
            "access": row[11]
        }
        return music
    else:
        return None

def music_list():
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT music_id,name,genre,detail,length,composer,source,URL FROM music"

    cursor.execute(sql)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def update_pass(password, id):
    
    salt = get_salt()
    pass_code = get_hash(password,salt)
    
    connection = get_connection()
    cursor = connection.cursor()
    sql = "UPDATE admin SET hashed_password=%s, salt=%s  WHERE mail=%s"

    cursor.execute(sql, (pass_code,salt,id))
    connection.commit()

    cursor.close()
    connection.close()

def temp_password(mail):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT * FROM admin WHERE mail = %s"
    
    cursor.execute(sql,(mail,))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return result[3]
    # if result:
    #     return result[2]
    # else:
    #     return None

def set_salt(mail):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT * FROM admin WHERE mail = %s"
    
    cursor.execute(sql,(mail,))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return result[4]


def password_flag(mail):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT * FROM admin WHERE mail = %s"
    
    cursor.execute(sql,(mail,))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return result[5]

    
def set_update_flag(id):
    
    connection = get_connection()
    cursor = connection.cursor()
    sql = "UPDATE admin SET temporary_password_flag = false WHERE id=%s"

    cursor.execute(sql, (id,))
    connection.commit()

    cursor.close()
    connection.close()
    
def get_id(mail):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT * FROM admin WHERE mail = %s"
    
    cursor.execute(sql,(mail,))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return result[0]


def admin_select_all():
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT id,name,mail FROM admin"

    cursor.execute(sql)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


    

def list_of_review():
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT * FROM music_review"

    cursor.execute(sql)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows