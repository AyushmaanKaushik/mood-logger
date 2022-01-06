from enum import unique
from ssl import Options
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from pandas.core.dtypes.common import classes
from sqlalchemy.sql.functions import count
import datetime
import psycopg2
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.embed import components

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
        day_avg=df.groupby(['Day']).mean()
        plot = figure(plot_width=400, plot_height=400,title=None, toolbar_location="below")
        plot.line(day_avg.index,day_avg['mood'])
        script, div = components(plot)  
        kwargs = {'script': script, 'div': div}
        kwargs['title'] = 'bokeh-with-flask'
        return render_template("submit_page.html", **kwargs)

if __name__=="__main__":
    app.debug=True
    app.run()