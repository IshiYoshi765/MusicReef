import os, psycopg2, string, random, hashlib
import smtplib 
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart





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

def delete_user(id):
    connection = get_connection()
    cursor = connection.cursor()
    
    check_sql = "select * from one_time_pass where admin_id = %s"
    cursor.execute(check_sql,(id,))
    result = cursor.fetchone()

    if result:     
        sql = "delete from one_time_pass where admin_id=%s"
        cursor.execute(sql, (id,))
    
    sql_one_pass = "delete from admin where id=%s"
    cursor.execute(sql_one_pass,(id,)) 
    connection.commit()
        
    cursor.close()
    connection.close()
    
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
    
def edit_music(name,genre,detail,length,composer,source,URL,tags_list,id):
    # lengthが指定されるまで待つ
    while length is None or length == "":
        length = input("Please enter the length (format: HH:MM): ")
    length_number = cal_length_num(length)
    sql = "UPDATE music SET name = %s,genre = %s,detail = %s,length = %s,length_number = %s, composer = %s,source = %s,URL = %s,update_time = CURRENT_TIMESTAMP WHERE music_id = %s"

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql,(name,genre,detail,length,length_number,composer,source,URL,id))
    connection.commit()
    
    sql_delete_tags = "DELETE FROM music_tags WHERE music_id = %s"
    cursor.execute(sql_delete_tags,(id,))
    
    sql_select = "SELECT music_id FROM music WHERE music_id = %s"
    cursor.execute(sql_select,(id,))
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
    
    sql_delete_tags = "DELETE FROM music_tags WHERE music_id = %s"
    cursor.execute(sql_delete_tags,(music_id,))

    sql = "delete from music where music_id=%s"

    cursor.execute(sql, (music_id,))
    connection.commit()
    
    
    cursor.close()
    connection.close()

#音源の検索
def search_music(name, genre):
    connection = get_connection()
    cursor = connection.cursor()

    tag_names = name.split()

    tag_name_placeholders = ','.join(['%s'] * len(tag_names))
    
    # タグ名がない場合の条件分岐
    tag_condition = ""
    if tag_names:
        tag_condition = "OR (tags.tag_name IN ({tag_name_placeholders}))"
    
    sql = f"""
    SELECT DISTINCT music.*
    FROM music
    LEFT JOIN music_tags ON music.music_id = music_tags.music_id
    LEFT JOIN tags ON music_tags.tag_id = tags.tag_id
    WHERE (music.name LIKE %s {tag_condition})
    AND music.genre LIKE %s
    GROUP BY music.music_id
    HAVING COUNT(DISTINCT tags.tag_id) >= {len(tag_names)};
    """
    
    print(tag_name_placeholders)

    name2 = "%" + name + "%"
    genre2 = "%" + genre + "%"

    if tag_names:
        cursor.execute(sql.format(tag_name_placeholders=tag_name_placeholders), ([name2] + tag_names + [genre2]))
    else:
        cursor.execute(sql, ([name2, genre2]))
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

    sql = "SELECT music_id,name,genre,detail,length,composer,source,URL,date_register,update_time FROM music ORDER BY music_id ASC"

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

def freeze_flag(mail):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT * FROM admin WHERE mail = %s"
    
    cursor.execute(sql,(mail,))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return result[6]
    
    
def set_update_flag(id):
    
    connection = get_connection()
    cursor = connection.cursor()
    sql = "UPDATE admin SET temporary_password_flag = false WHERE id=%s"

    cursor.execute(sql, (id,))
    connection.commit()

    cursor.close()
    connection.close()
    
def cold_flag(id):
    connection =get_connection()
    cursor = connection.cursor()
    
    sql = "update admin set cold_flag = false where id = %s"
    cursor.execute(sql,(id,))
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

def admin_edit(name,id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "UPDATE admin SET name = %s WHERE id= %s"

    cursor.execute(sql, (name,id))
    connection.commit()

    cursor.close()
    connection.close()
    

def list_of_review():
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT * FROM music_review"

    cursor.execute(sql)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()
    return rows
    



def save_otp(mail):
    
    connection = get_connection()
    cursor = connection.cursor()
    
    sql = "SELECT id FROM admin WHERE mail = %s"
    cursor.execute(sql,(mail,))
    admin_result = cursor.fetchone()

    if admin_result:
        admin_id = admin_result[0]
        print(admin_id)
        otp_code = get_otp_pass()
        send_email(mail, otp_code)
        sql = "INSERT INTO one_time_pass VALUES(default,%s,%s,CURRENT_TIMESTAMP,default)"
        cursor.execute(sql,(admin_id,otp_code))
        connection.commit()
        print('成功')
        
    cursor.close()
    connection.close()
        
def update_pass(password,mail):
    salt = get_salt()
    hashed_password = get_hash(password,salt)
    
    connection = get_connection()
    cursor = connection.cursor()
    
    sql = "UPDATE admin SET hashed_password=%s, salt=%s  WHERE mail=%s"
        
    cursor.execute(sql,(hashed_password,salt,mail))
    connection.commit()
        
    cursor.close()
    connection.close()
        

# ランダムなソルトを生成
def get_otp_pass():
    # 文字列の候補(英大小文字 + 数字)
    charset = string.ascii_letters + string.digits
    
    # charsetからランダムに30文字取り出して結合
    one_time = ''.join(random.choices(charset, k=6))
    now = datetime.now()
    # print(one_time)
    # print(now)
    # print(time)
    return one_time

def verify_otp(admin_id, entered_otp):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        sql_select = "SELECT otp_code, expiration_time, is_used FROM one_time_pass WHERE admin_id = (SELECT id FROM admin WHERE mail = %s) ORDER BY expiration_time DESC LIMIT 1"
        cursor.execute(sql_select, (admin_id,))
        db_otp_result = cursor.fetchone()
        print(db_otp_result)

        if db_otp_result:
            db_otp, expiration_time, is_used = db_otp_result
            
            current_time = datetime.now()
            time = expiration_time + timedelta(seconds=30)
            print(current_time)
            print(time)
            
            # ワンタイムパスワードが使用されていないかつ有効期限内であることを確認
            if not is_used and time >= current_time:
                # 入力されたワンタイムパスワードとデータベースのワンタイムパスワードを比較
                if entered_otp == db_otp:
                    sql = "UPDATE one_time_pass SET is_used = true WHERE admin_id = (SELECT id FROM admin WHERE mail = %s) AND otp_code = %s"
                    cursor.execute(sql,(admin_id,db_otp))
                    connection.commit()
                    return True  # パスワードが一致する場合
                else:
                    print(f"Entered OTP: {entered_otp}, DB OTP: {db_otp}")
            else:
                print("Invalid expiration time or used OTP.")
        else:
            print("No valid OTP found.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if connection:
            connection.close()

    return False  # パスワードが一致しない場合またはエラーが発生した場合

def delete_review(review_id):
    connection = get_connection()
    cursor = connection.cursor()

    sql = "DELETE FROM music_review WHERE id = %s"
    cursor.execute(sql, (review_id,))

    connection.commit()
    cursor.close()
    connection.close()
    
def get_recent_music():
    connection = get_connection()
    cursor = connection.cursor()

    sql = """
        SELECT m.*, AVG(r.star) AS avg_rating
        FROM music m
        LEFT JOIN music_review r ON m.music_id = r.music_id
        GROUP BY m.music_id
        ORDER BY m.date_register DESC
        LIMIT 5
    """

    cursor.execute(sql)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def increment_access_count(music_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # アクセス数を1加算
        sql = "UPDATE music SET access = access + 1 WHERE music_id = %s"
        cursor.execute(sql, (music_id,))
        connection.commit()
    except psycopg2.DatabaseError as e:
        print(f"アクセス数の更新エラー: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def get_music_url(music_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        sql = "SELECT URL FROM music WHERE music_id = %s"
        cursor.execute(sql, (music_id,))

        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            print(f"Error: No URL found for music_id {music_id}")
            return None

    except Exception as e:
        print(f"Error in get_music_url: {e}")
        return None

    finally:
        cursor.close()
        connection.close()

def get_top_songs_weekly():
    today = datetime.utcnow()
    monday = today - timedelta(days=today.weekday())

    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        sql = """
            WITH WeeklyRank AS (
                SELECT
                    music_id,
                    ROW_NUMBER() OVER (ORDER BY access DESC) AS ranking
                FROM
                    music
                WHERE
                    EXTRACT(DOW FROM date_register) BETWEEN 1 AND 6
            )
            UPDATE music m
            SET access = 0
            FROM WeeklyRank wr
            WHERE m.music_id = wr.music_id;

            SELECT
                m.*
            FROM
                music m
            WHERE
                EXTRACT(DOW FROM m.date_register) BETWEEN 1 AND 6
            ORDER BY
                m.access DESC
            LIMIT 3;
        """

        cursor.execute(sql)

        week_top_songs = cursor.fetchall()

    except psycopg2.DatabaseError as e:
        print(f"Error in get_top_songs_weekly: {e}")
        week_top_songs = []

    finally:
        cursor.close()
        connection.close()

    return week_top_songs

def get_top_songs_monthly():
    today = datetime.utcnow()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (
        today.replace(day=28) + timedelta(days=4)
    ).replace(day=1) - timedelta(days=1)

    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        sql = """
            WITH MonthlyRank AS (
                SELECT
                    music_id,
                    ROW_NUMBER() OVER (ORDER BY access DESC) AS ranking
                FROM
                    music
                WHERE
                    date_register BETWEEN %s AND %s
            )
            UPDATE music m
            SET access = 0
            FROM MonthlyRank mr
            WHERE m.music_id = mr.music_id;

            SELECT
                m.*
            FROM
                music m
            WHERE
                date_register BETWEEN %s AND %s
            ORDER BY
                m.access DESC
            LIMIT 3;
        """

        cursor.execute(sql, (first_day_of_month, last_day_of_month, first_day_of_month, last_day_of_month))

        month_top_songs = cursor.fetchall()

    except psycopg2.DatabaseError as e:
        print(f"get_top_songs_monthly でエラーが発生しました: {e}")
        month_top_songs = []

    finally:
        cursor.close()
        connection.close()

    return month_top_songs

def get_music_by_id(music_id):
    sql = 'SELECT * FROM music WHERE music_id = %s'

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (music_id,))
        music_info = cursor.fetchone()

        # データが見つからない場合
        if music_info is None:
            # または、デフォルトの音楽情報をセットするなどの対処を行う
            music_info = {
                'id': 0,
                'title': 'Unknown Title',
                'composer': 'Unknown Composer',
                'genre': 'Unknown Genre',
                # 他の音楽情報も必要に応じてデフォルトの値をセット
            }
    except psycopg2.DatabaseError as e:
        # エラーメッセージをログに出力するなどの対処を行う
        print(f"Error fetching music info: {e}")
        music_info = None
    finally:
        cursor.close()
        connection.close()

    return music_info



def get_average_ratings():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # 各 music_id ごとの平均評価を計算するクエリ
        sql = """
            SELECT music_id, AVG(star) AS average_rating
            FROM music_review
            GROUP BY music_id
        """
        cursor.execute(sql)
        ratings = {row[0]: row[1] for row in cursor.fetchall()}

        return ratings

    except Exception as e:
        print(f"get_average_ratings でエラーが発生しました: {e}")
        return {}

    finally:
        cursor.close()
        connection.close()


        
def insert_comment(star, review, music_id):
    sql = 'INSERT INTO music_review (star, review, music_id, date_time) VALUES (%s, %s, %s, NOW())'

    count = 0

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (star, review, music_id))
        connection.commit()
        count = cursor.rowcount

    except psycopg2.DatabaseError as e:
        print(f"DatabaseError: {e}")
    finally:
        cursor.close()
        connection.close()

    return count

def get_review_by_music_id(music_id, limit=5, offset=0):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT star, review, date_time FROM music_review WHERE music_id = %s ORDER BY date_time DESC LIMIT %s OFFSET %s", (music_id, limit, offset))
        reviews = cursor.fetchall()
        review_list = []
        for review in reviews:
            review_dict = {
                'star': review[0],
                'review': review[1],
                'date_time': review[2].strftime('%Y/%m/%d %H:%M')
            }
            review_list.append(review_dict)
        return review_list
    finally:
        cursor.close()
        connection.close()
