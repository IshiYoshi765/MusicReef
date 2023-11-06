import os, psycopg2, string, random, hashlib
import smtplib 
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


def insert_book(isbn, title, author, publisher):
    sql = "INSERT INTO books VALUES(default, %s, %s, %s,%s)"

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        sql,
        (
            isbn,
            title,
            author,
            publisher,
        ),
    )
    connection.commit()

    cursor.close()
    connection.close()


def delete_book(id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "delete from books where id=%s"

    cursor.execute(sql, (id,))
    connection.commit()

    cursor.close()
    connection.close()


def search_book(title):
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT * FROM books WHERE title LIKE %s"

    title2 = "%" + title + "%"

    cursor.execute(sql, (title2,))

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def list_book():
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT ISBN,title,author,publisher FROM books"

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
    



