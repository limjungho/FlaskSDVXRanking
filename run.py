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
DiffList = ['NOV', 'ADV', 'EXH', 'MXM', 'INF', 'GRV', 'HVN', 'VVD']

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
    #print(PageTrack[0])
    #sleep(500)
    conn.close()

    return render_template('index.html',AllTrack=AllTrack,PageTrack=PageTrack,DiffList=DiffList)

@app.route('/RankingPage.html',methods = ['GET'])
def RenderRanking():
    tid = request.args.get('tid')
    diff = request.args.get('diff')
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select UserNumber, Score, Grade, Complete from ScoreData where TrackID=? AND Difficulty=?;"
    cur.execute(sql,(tid,diff))
    RankList = cur.fetchall()
    sortedRankList = sorted(RankList, key=lambda x: x[1], reverse=True)

    sql = "select TrackTitle from TrackList where TrackID=?;"
    cur.execute(sql, (tid,))
    TrackTitle = cur.fetchone()[0]

    UserNameList =[]

    for rank, data in enumerate(sortedRankList):
        sql = "select UserName from UserInfo where UserNumber = ?;"
        cur.execute(sql, (data[0],))
        UserName = cur.fetchone()[0]
        UserNameList.append((rank+1,UserName))

    conn.close()
    return render_template('RankingPage.html',
                           sortedRankList=sortedRankList,
                           tid=tid,
                           title=TrackTitle,
                           diff=diff,
                           UserNameList=UserNameList)


if __name__ == "__main__":
    app.run(debug=True)