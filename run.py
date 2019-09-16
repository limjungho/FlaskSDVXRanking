#import os
from time import sleep
from flask import Flask, render_template, current_app, g, request
import sqlite3


app = Flask(__name__)
'''
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'SDVXRanking.db')
))
'''


@app.route('/',methods = ['GET'])
def MainIndex():
    ViewPageLen = 50
    page = request.args.get('page')
    if page == None:
        page = 1
    page = 1000+(int(page)-1)*ViewPageLen

    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select * from TrackList"
    cur.execute(sql)
    rows = cur.fetchall()
    TrackLen = int((len(rows) + 49) / 50)
    AllTrack = range(0, TrackLen)

    sql = "select * from TrackList where TrackID >= ? AND TrackID <= ?;"
    cur.execute(sql,(str(page+1),str(page+ViewPageLen)))
    PageTrack = cur.fetchall()
    for i in range(0,len(PageTrack)):
        PageTrack[i] = PageTrack[i][1:]
    #print(PageTrack[0])
    #sleep(500)
    conn.close()

    return render_template('index.html',AllTrack=AllTrack,PageTrack=PageTrack)

if __name__ == "__main__":
    app.run(debug=True)