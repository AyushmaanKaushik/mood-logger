from enum import unique
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import count
import datetime


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://new:123@localhost/mood_logger'
db=SQLAlchemy(app)

class Record(db.Model):
    __tablename__="logs"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), unique=True)
    mood=db.Column(db.Integer)
    timestamp=db.Column(db.String(50))

    def __init__(self,name_,mood_,timestamp_):
        self.name=name_
        self.mood=mood_
        self.timestamp=timestamp_

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit_page",methods=["POST"])
def submit():
    if request.method=='POST':
        name=request.form['username']
        mood=request.form['mood']
        timestamp=datetime.datetime.now()
        record=Record(name,mood,timestamp) 
        db.session.add(record)
        db.session.commit()
        print(record)
        return render_template("submit_page.html")



if __name__=="__main__":
    app.debug=True
    app.run()