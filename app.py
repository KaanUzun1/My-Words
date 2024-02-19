from flask import redirect, render_template, session, request, session, Flask
from functools import wraps
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
import datetime as dt


app = Flask(__name__)


app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///users.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Show the three table"""

    """Getting the words and their ids in the database"""
    users_words = db.execute("SELECT * FROM words WHERE user_id = ?", session["user_id"])
    if users_words:
        word_ids = [user_word["word_id"] for user_word in users_words]
        words = [user_word["word"] for user_word in users_words]

        length = len(users_words)

        #Putting every word's column into the columns list
        columns = []
        for word_id in word_ids:
            column = db.execute("SELECT column FROM columns WHERE word_id = ?", word_id)
            column = column[0]["column"]
            columns.append(column)


        #Putting every word's date into the dates list
        dates = []
        for word_id in word_ids:
            date = db.execute("SELECT date FROM date WHERE word_id = ?", word_id)
            date = date[0]["date"]
            dates.append(date)


        #Putting every word's usage in example/examples into the examples list
        examples = []
        for word_id in word_ids:
            example = db.execute("SELECT example FROM examples WHERE word_id = ?", word_id)
            if example:
                if len(example) > 1:
                    example = [element["example"] for element in example]
                else:
                    example = example[0]["example"]
                examples.append(example)
            else:
                example = " "
                examples.append(example)

        
        meanings = []
        for word_id in word_ids:
            meaning = db.execute("SELECT meaning FROM meanings WHERE word_id = ?", word_id)
            if not meaning:
                meaning = " "
            else:
                meaning = meaning[0]["meaning"]
            meanings.append(meaning)

        
        mustPractice2days = []
        mustPractice7days = []
        word_ids_2days = []
        word_ids_7days = []


        #Checking every word's last practiced time to see whether today is the practice day
        today = dt.date.today()

        for i in range(length):
            date = dt.datetime.strptime(dates[i], "%Y-%m-%d").date()
            difference = today - date

            if columns[i] == "LearningWords" and difference.days >= 2:
                mustPractice2days.append(words[i])
                word_ids_2days.append(word_ids[i])

            if columns[i] == "MasteredWords" and difference.days >= 7:
                mustPractice7days.append(words[i])
                word_ids_7days.append(word_ids[i])

        #Changing the word's last practiced time
        today = today.strftime("%Y-%m-%d")
        if len(mustPractice2days) != 0 or len(mustPractice7days) != 0:

            for word_id in word_ids_2days:
                db.execute("UPDATE date SET date = ? WHERE word_id = ?", today, word_id)

            for word_id in word_ids_7days:
                db.execute("UPDATE date SET date = ? WHERE word_id = ?",today, word_id)

            return render_template("index.html",word_ids=word_ids, columns=columns, words=words, mustPractice2days=mustPractice2days, mustPractice7days=mustPractice7days, length=length, examples=examples, meanings=meanings)

        return render_template("index.html",word_ids=word_ids, columns=columns, words=words, length=length, examples=examples, meanings=meanings)
    else:
        return render_template("index.html")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        #Registering the user
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")


        #Checking whether the username and password that the user entered meet requirements
        if not username or not password:
            return render_template("register.html", fail_message="Must provide a username and/or password")
        
        if db.execute("SELECT username FROM users WHERE username = ?", username):
            return render_template("register.html", fail_message="Username is already taken")

        if password != password_confirmation:
            return render_template("register.html", fail_message="Passwords do not match")
        
        if len(password) <= 8:
            return render_template("register.html", fail_message="Password should be longer than 8")
        
        lower = 0
        upper = 0
        digit = 0
        for i in password:
            if i.islower():
                lower = 1
            if i.isupper():
                upper = 1
            if i.isdigit():
                digit = 1
        
        if lower == 0 or upper == 0 or digit == 0:
            return render_template("register.html", fail_message="Password has to contain at least one uppercase one lowercase and a number")

        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, password_hash)

        #Logging in the user
        id = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]
        session["user_id"] = id

        return redirect("/")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session.clear()
        return render_template("login.html")
    
    else:
        #Checking whether the password and the username correct
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", fail_message="Your password or/and username is wrong")
        
        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            return render_template("login.html", fail_message="Your password or/and username is wrong")
        
        #Logging in the user
        session["user_id"] = user[0]["id"]

        return redirect("/")


@app.route("/add_words", methods=["POST"])
@login_required
def add():
    #Adding the new word to the database
    if request.form.get("AddWord"):
        word = request.form.get("AddWord")
        meaning = request.form.get("meaning")
        example = request.form.get("example")
        column = request.form.get("collumn")


        in_words = db.execute("SELECT * FROM words WHERE user_id = ?", session["user_id"])
        in_words = [in_word["word"] for in_word in in_words]

        #Checking if the new word already exist in the database
        if word in in_words:
            return redirect("/")

        #Adding the new word to the database
        db.execute("INSERT INTO words(user_id, word) VALUES(?, ?)", session["user_id"], word)

        word_id = db.execute("SELECT word_id FROM words WHERE user_id = ? AND word = ?",session["user_id"], word)[0]["word_id"]

        date_object = dt.datetime.now()

        date_object = date_object + dt.timedelta(days=2)

        date = date_object.strftime("%Y-%m-%d")

        db.execute("INSERT INTO date(word_id, date) VALUES(?, ?)", word_id, date)

        db.execute("INSERT INTO columns(word_id, column) VALUES(?,?)",word_id, column)

        db.execute("INSERT INTO examples(word_id, example) VALUES(?,?)", word_id, example)

        db.execute("INSERT INTO meanings(word_id, meaning) VALUES(?, ?)", word_id, meaning)


    return redirect("/")


@app.route("/add_example", methods=["POST"])
def add_example():
    example = request.form.get("example")
    word_id = int(request.form.get("word_id"))

    word_ids = db.execute("SELECT word_id FROM words WHERE user_id = ?", session["user_id"])
    word_ids = [lmnt["word_id"] for lmnt in word_ids]

    #Making sure user can't reach another word outside of his/her vocabulary
    if word_id in word_ids:
        db.execute("INSERT INTO examples(word_id, example) VALUES(?, ?)", word_id, example)
        return redirect("/")

    else:
        return redirect("/")
    

@app.route("/change_column", methods=["POST"])
def change_column():
    word_id = int(request.form.get("word_id"))
    column = request.form.get("column")

    word_ids = db.execute("SELECT word_id FROM words WHERE user_id = ?", session["user_id"])
    word_ids = [lmnt["word_id"] for lmnt in word_ids]


    #Making sure user can't reach another word outside of his/her vocabulary
    if word_id in word_ids:
        db.execute("UPDATE columns SET column = ? WHERE word_id = ?", column, word_id)
        return redirect("/")

    else:
        return redirect("/")


@app.route("/change_meaning", methods=["POST"])
def change_meaning():
    word_id = int(request.form.get("word_id"))
    meaning = request.form.get("meaning")

    word_ids = db.execute("SELECT word_id FROM words WHERE user_id = ?", session["user_id"])
    word_ids = [lmnt["word_id"] for lmnt in word_ids]


    #Making sure user can't reach another word outside of his/her vocabulary
    if word_id in word_ids:
        db.execute("UPDATE meanings SET meaning = ? WHERE word_id = ?", meaning, word_id)
        return redirect("/")

    else:
        return redirect("/")



@app.route("/delete_example", methods=["POST"])
def delete_example():
    example = request.form.get("example")
    word_id = int(request.form.get("word_id"))

    word_ids = db.execute("SELECT word_id FROM words WHERE user_id = ?", session["user_id"])
    word_ids = [lmnt["word_id"] for lmnt in word_ids]


    #Making sure user can't reach another word outside of his/her vocabulary
    if word_id in word_ids:
        db.execute("DELETE FROM examples WHERE example = ? AND word_id = ?", example, word_id)
        return redirect("/")

    else:
        return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    word_id = int(request.form.get("word_id"))

    word_ids = db.execute("SELECT word_id FROM words WHERE user_id = ?", session["user_id"])
    word_ids = [lmnt["word_id"] for lmnt in word_ids]


    #Making sure user can't reach another word outside of his/her vocabulary
    if word_id in word_ids:
        db.execute("DELETE FROM meanings WHERE word_id = ?", word_id)
        db.execute("DELETE FROM examples WHERE word_id = ?", word_id)
        db.execute("DELETE FROM words WHERE word_id = ?", word_id)
        db.execute("DELETE FROM columns WHERE word_id = ?", word_id)
        db.execute("DELETE FROM date WHERE word_id = ?", word_id)

        return redirect("/")

    else:
        return redirect("/")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return redirect("/")