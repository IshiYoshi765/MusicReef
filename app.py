from flask import Flask, render_template, request
import random,string
import tags

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

@app.route("/", methods=["GET"])
def index():
    msg = request.args.get("msg")
    if msg == None:
        return render_template("index.html")
    else:
        return render_template("index.html", msg=msg)

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
