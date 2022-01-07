from enum import unique
from ssl import Options
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from pandas.core.dtypes.common import classes
from sqlalchemy.sql.functions import count
import datetime
import psycopg2
import pandas as pd
import json
import plotly
import plotly.express as px

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://new:123@localhost/mood_logger'
db=SQLAlchemy(app)

# Creating a dataframe from the database
param_dic = {
    "host"      : "localhost",
    "database"  : "mood_logger",
    "user"      : "new",
    "password"  : "123"
}
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


conn = psycopg2.connect(**param_dic)
df=pd.read_sql("SELECT * FROM logs",conn, parse_dates=['timestamp'])


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit",methods=["POST"])
def submit():
    if request.method=='POST':
        name=request.form['username']
        mood=request.form['mood']
        timestamp=datetime.datetime.now()
        record=Record(name,mood,timestamp) 
        db.session.add(record)
        db.session.commit()
        # Average ratings per day
        df["Day"] = df[(df['name']==name)]['timestamp'].dt.date
        global day_avg
        day_avg=df.groupby(['Day']).mean()
        global df2 
        df2 = df[df['name']==name].groupby(['mood']).mean().reset_index()
        return render_template("submit_page.html")

@app.route('/pie')
def pie_data():
    fig_pie = px.pie(df2, values='id', names='mood')
    graphJSON = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("pie.html", graphJSON=graphJSON)

@app.route('/line')
def line_data():
    fig_line=px.line(day_avg,y="mood",title="Your average mood daily")
    graphJSON = json.dumps(fig_line, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("pie.html", graphJSON=graphJSON)

if __name__=="__main__":
    app.debug=True
    app.run()