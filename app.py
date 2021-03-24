from flask import *
from flask import Flask, render_template,escape
from datetime import datetime
from flask_bcrypt import Bcrypt
from bs4 import BeautifulSoup
import sqlite3
import feedparser
from flask_apscheduler import APScheduler
from jinja2 import Environment


app = Flask(__name__)
jinja_env = Environment(extensions=['jinja2.ext.loopcontrols'])
scheduler = APScheduler()
bcrypt = Bcrypt()
app.secret_key = "invoker"


# login page
@app.route("/")  
def login():  
    return session_check()


# checking if user is already logged in
def session_check():
    try:
        role = session['role']
        if ((session['username']) and (role == "Admin")):
            return admin_homepage_redirect()
        elif ((session['username']) and (role == "User")):
            return view()
    except:
        return render_template("login.html")


# register page
@app.route("/register")  
def add():  
    return render_template("register.html") 


# registering user to database
@app.route("/savedetails",methods = ["POST","GET"])  
def saveDetails():  
    msg = "msg"  
    if request.method == "POST":  
        try:  
            email = request.form["email"]  
            password = bcrypt.generate_password_hash(request.form["password"])
            role = request.form["role"]  
            with sqlite3.connect("aggregatefeed.db") as con:  
                cur_fetch = con.cursor()
                cur_fetch.execute("SELECT * FROM users where email = (?) ",(email,)) 
                row = cur_fetch.fetchall()  
                if(row):
                    msg = "User already exists" 
                    return render_template("register.html",msg = msg)
                else:
                    cur = con.cursor()
                    cur.execute("INSERT into users (email,password,role) values (?,?,?)",(email,password,role))
                    con.commit()
                    msg = "Registration successful" 
                    return render_template("login.html",msg = msg)
        except:  
           msg = "Unable to register"
           return render_template("register.html",msg = msg)
        finally:  
            con.close()


# login credentials check based on role and starting session
@app.route("/mainpage",methods = ["POST","GET"])  
def loginCheck():  
    con = sqlite3.connect("aggregatefeed.db")  
    con.row_factory = sqlite3.Row  

    # Query to fetch all users
    cur_all_users = con.cursor()  
    cur_all_users.execute("select COUNT(*) AS count_users from users")
    rows_all_users = cur_all_users.fetchone()

    # Query to fetch popular article
    cur_pop_article = con.cursor()  
    cur_pop_article.execute("select COUNT(*) AS count_users from users")
    rows_pop_article = cur_pop_article.fetchone()

    # Query to fetch popular source
    cur_pop_source = con.cursor()  
    cur_pop_source.execute("select COUNT(*) AS count_users from users")
    rows_pop_source = cur_pop_source.fetchone()

    if request.method == "POST":  
        try:  
            email = request.form["email"]  
            password = request.form["password"]
            with sqlite3.connect("aggregatefeed.db") as con:  
                cur = con.cursor()  
                cur.execute("SELECT * FROM users where email = (?) ",(email,))
                row = cur.fetchone()  
                con.commit()
                if (bcrypt.check_password_hash(row[2],password) and row[3] == "Admin"):
                    session['username'] = row[0]
                    session['role'] = row[3]
                    return render_template("admin_homepage.html",rows_all_users = rows_all_users, rows_pop_article = rows_pop_article, rows_pop_source = rows_pop_source)
                elif (bcrypt.check_password_hash(row[2],password) and row[3] == "User"): 
                    session['username'] = row[0]
                    session['role'] = row[3]
                    return view()
                else:     
                    msg = "Wrong Credentials" 
                    return render_template("login.html",msg = msg)
        # except:
        #     msg = "Unable to login"
        #     return render_template("login.html",msg = msg)
        finally:  
            con.close()


# admin homepage redirect
@app.route("/admin_homepage_redirect")  
def admin_homepage_redirect():
    con = sqlite3.connect("aggregatefeed.db")  
    con.row_factory = sqlite3.Row  

    # Query to fetch all users
    cur_all_users = con.cursor()  
    cur_all_users.execute("select COUNT(*) AS count_users from users")
    rows_all_users = cur_all_users.fetchone()

    # Query to fetch popular artice
    cur_pop_article = con.cursor()  
    cur_pop_article.execute("select COUNT(*) AS count_users from users")
    rows_pop_article = cur_pop_article.fetchone()

    # Query to fetch popular source
    cur_pop_source = con.cursor()  
    cur_pop_source.execute("select COUNT(*) AS count_users from users")
    rows_pop_source = cur_pop_source.fetchone()
    
    try:
        if(session['username']):
            return render_template("admin_homepage.html",rows_all_users = rows_all_users, rows_pop_article = rows_pop_article, rows_pop_source = rows_pop_source)
    except:
        msg = "Please login to continue."
        return render_template("login.html", msg = msg)

# URL adding form
@app.route('/add_url_form')
def add_url_form():
    return render_template('add_url_form.html')


# adding URL to database
@app.route('/send_url_form',methods = ["POST","GET"])
def add_url(): 
    if request.method == "POST":  
        try:  
            url = request.form["url"]  
            source_name = request.form["source_name"]  
            category = request.form["category"]
            user = session['username']
            role = session['role']
            with sqlite3.connect("aggregatefeed.db") as con:
                cur = con.cursor()  
                cur.execute("INSERT into url_list (url, source_name, category, created_by, role) values (?,?,?,?,?)",(url,source_name,category,user,role))
                con.commit() 
        except:  
           msg = "Unable to insert" 
           return render_template("add_url_form.html", msg = msg)
        finally:  
            return view_all_url()


# viewing all URL's
@app.route('/view_all_url')
def view_all_url():
    con = sqlite3.connect("aggregatefeed.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from url_list")  
    rows = cur.fetchall()  
    return render_template("view_all_url.html",rows = rows)


# deleting the URL
@app.route('/delete_url',methods = ["POST"])
def delete_url():
    id = request.form["id_to_del"] 
    try:  
        with sqlite3.connect("aggregatefeed.db") as con:
            cur = con.cursor()  
            cur.execute("delete from url_list where id = ?",id)  
            con.commit()
    except:
        msg = "Unable to delete"
        return render_template("view_all_url.html", msg = msg)
    finally:  
        return view_all_url()


# site analytics
@app.route('/site_analytics')
def site_analytics():
    con = sqlite3.connect("aggregatefeed.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select COUNT(*) AS count_users from users")  
    rows = cur.fetchone()
    return render_template('admin_homepage.html',rows = rows)


# entering all articles after parsing (doesn't allow duplicate news)
def articlestodb():
    with sqlite3.connect("aggregatefeed.db") as con:  
        cur = con.cursor()  
        cur.execute("SELECT * FROM url_list ")
        row_url = cur.fetchall() 
    for news_url in row_url:
        parsed =  feedparser.parse(news_url[1])
        entries = parsed['entries']

        for entry in entries:
            headline = entry['title']
            cur.execute("SELECT headline FROM article where  headline = (?) ",(headline,))
            row_headline = cur.fetchall() 
            
            if(row_headline):
                continue
            else:
                count = 0
                summary_to_filter = BeautifulSoup(entry['summary'])
                texts = summary_to_filter.findAll(text = True)
                summary = ''.join(texts)
                published_datetime = datetime(entry['published_parsed'][0], entry['published_parsed'][1], entry['published_parsed'][2],entry['published_parsed'][3], entry['published_parsed'][4], entry['published_parsed'][5])
                
                headline = entry['title']
                db_summary = summary
                db_date = published_datetime
                db_source = news_url[1]
                db_image_url = "hello"
                db_url = entry['link']
                with sqlite3.connect("aggregatefeed.db") as con:  
                    cur = con.cursor()  
                    cur.execute("INSERT into article (headline, summary, published_date,url,image_url,news_source,count) values (?,?,?,?,?,?,?)",(headline,db_summary,db_date,db_source,db_image_url,db_url,count))  
                    con.commit()


# viewing all articles after parsing 
@app.route("/home")  
def view():  
    userid = session['username']
    con = sqlite3.connect("aggregatefeed.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from article order by published_date DESC,count DESC")
    rows = cur.fetchall()  

    cur_book = con.cursor()  
    cur_book.execute("select article_id from bookmarked where user_id = (?)",(userid,))
    rows_book = cur_book.fetchall() 

    cur_upvote = con.cursor()  
    cur_upvote.execute("select article_id from upvote where user_id = (?)",(userid,))
    rows_upvote = cur_upvote.fetchall() 

    return render_template("homedb.html",rows = rows,rows_book = rows_book,rows_upvote = rows_upvote)


# bookmarking an article 
@app.route('/bookmark',methods = ["POST","GET"])
def add_book(): 
    if request.method == "POST":  
        try:    
            articleid = request.form["id_to_book"]  
            userid = session['username']
            with sqlite3.connect("aggregatefeed.db") as con:
                cur_fetch = con.cursor()
                cur_fetch.execute("SELECT * FROM bookmarked where article_id == :article_id and user_id == :user_id", {"article_id": articleid, "user_id": userid}) 
                row = cur_fetch.fetchall()  
                if(row):
                    pass
                else:
                    cur = con.cursor()  
                    cur.execute("INSERT into bookmarked (article_id,user_id) values (?,?)",(articleid,userid))
                    con.commit()  
        finally: 
           return view()


# viewing all bookmarks for particular user 
@app.route('/bookmarked')
def bookmarked():
    userid = session['username']
    con = sqlite3.connect("aggregatefeed.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from article where articleid in (select article_id from bookmarked where user_id=(?))", (userid,)) 
    rows = cur.fetchall()  
    return render_template('bookmarked.html',rows= rows)


# delete bookmark
@app.route('/delete_bookmarked',methods = ["POST"])
def delete_bookmark():
    id = request.form["id_to_del_bm"]
    userid = session['username'] 
    try:  
        with sqlite3.connect("aggregatefeed.db") as con:
            cur = con.cursor()  
            cur.execute("delete from bookmarked where article_id = (?) and user_id = (?)",(id,userid))
            con.commit()
    finally:  
        return bookmarked()
        

# upvoting an article 
@app.route('/upvote',methods = ["POST","GET"])
def add_upvote(): 
    if request.method == "POST":  
        try:    
            articleid = request.form["id_to_upvote"]  
            userid = session['username']
            with sqlite3.connect("aggregatefeed.db") as con:
                cur_fetch = con.cursor()
                cur_fetch.execute("SELECT * FROM upvote where article_id == :article_id and user_id == :user_id", {"article_id": articleid, "user_id": userid}) 
                row = cur_fetch.fetchall()  
                count = row['count']
                if(row):
                    pass
                else:
                    cur = con.cursor()  
                    cur.execute("INSERT into upvote (article_id,user_id) values (?,?)",(articleid,userid))
                    con.commit() 
                    count = count+1
                    cur_art_count = con.cursor()  
                    cur_art_count.execute("update article set count == :count where articleid == :articleid",{"count": count ,"articleid": articleid})
                    con.commit()  
        finally:  
           return view()

# viewing all liked posts 
@app.route("/liked")  
def like():  
    con = sqlite3.connect("aggregatefeed.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from article where articleid in (select article_id from upvote where user_id = 1)")  
    rows = cur.fetchall()
    return render_template("liked.html",rows = rows)


# logging out and ending session
@app.route("/logout")  
def logout():  
    session.pop('username', None)
    session.pop('role',None)
    msg = "Logged out successfully."
    return render_template("login.html", msg = msg)


if __name__ == "__main__":
    # setting and starting the scheduler to parse news for given time
    scheduler.add_job(id = "Scheduled Task", func = articlestodb, trigger = 'interval',minutes= 1)
    scheduler.start()
    app.run (debug=True)