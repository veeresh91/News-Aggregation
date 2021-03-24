import sqlite3  
  
con = sqlite3.connect("aggregatefeed.db")  
print("Database opened successfully")  
con.execute("create table register (id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,role TEXT NOT NULL)")    
con.execute("create table article (articleid INTEGER PRIMARY KEY AUTOINCREMENT,headline TEXT NOT NULL,summary TEXT NOT NULL, published_date DATETIME NOT NULL,url TEXT NOT NULL,image_url TEXT NOT NULL,news_source TEXT NOT NULL, count INTEGER)")   
con.execute("create table bookmarked (id INTEGER PRIMARY KEY AUTOINCREMENT,article_id INTEGER NOT NULL,user_id INTEGER NOT NULL)")
con.execute("create table upvote (id INTEGER PRIMARY KEY AUTOINCREMENT,article_id INTEGER NOT NULL,user_id INTEGER NOT NULL)")

 
con.execute('''create table url_list (id INTEGER PRIMARY KEY AUTOINCREMENT, 
url TEXT NOT NULL,
source_name TEXT NOT NULL,
category TEXT NOT NULL,
created_by TEXT NOT NULL,
role TEXT NOT NULL);''')  

con.execute('''create table users (id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,role TEXT NOT NULL)''')  

print("Tables created successfully")  
  
con.close()  