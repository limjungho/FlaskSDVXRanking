import os
from threading import Thread
from time import sleep
from flask import Flask, render_template, current_app, g, request, redirect, url_for
import sqlite3
from UserUpdate import UserUpdateProc
import urllib.parse


app = Flask(__name__, static_url_path='/static')

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

    sql = "select TrackTitle, "+diff+" from TrackList where TrackID=?;"
    cur.execute(sql, (tid,))
    TrackTitle, TrackLv = cur.fetchone()

    UserNameList =[]
    prevRank = 1
    nowRank = 1
    prevScore = 10000000

    CompleteImgDict = dict()
    CompleteImgList = ['PUC', 'UC', 'COMP_EX', 'COMP', 'PLAY']
    CompleteImgValueList = ['rival_mark_per.png', 'rival_mark_uc.png', 'rival_mark_comp_ex.png', 'rival_mark_comp.png',
                            'rival_mark_play.png']
    for i in range(0, 5):
        CompleteImgDict[CompleteImgList[i]] = CompleteImgValueList[i]

    GradeImgDict = dict()
    GradeImgList = ['S', 'AAA+', 'AAA', 'AA+', 'AA', 'A+', 'A', 'B', 'C', 'D']
    GradeImgValueList = ['rival_grade_s.png', 'rival_grade_aaa_plus.png', 'rival_grade_aaa.png',
                         'rival_grade_aa_plus.png',
                         'rival_grade_aa.png', 'rival_grade_a_plus.png', 'rival_grade_a.png', 'rival_grade_b.png',
                         'rival_grade_c.png',
                         'rival_grade_d.png']
    for i in range(0, 10):
        GradeImgDict[GradeImgList[i]] = GradeImgValueList[i]

    for rank, data in enumerate(sortedRankList):
        sql = "select UserName from UserInfo where UserNumber = ?;"
        cur.execute(sql, (data[0],))
        UserName = cur.fetchone()[0]
        if data[1] == prevScore:
            nowRank = prevRank
        else:
            nowRank = rank + 1
            prevRank = nowRank
            prevScore = data[1]
        UserNameList.append((nowRank,UserName))

    conn.close()
    return render_template('RankingPage.html',
                           sortedRankList=sortedRankList,
                           tid=tid,
                           title=TrackTitle,
                           TrackLv=TrackLv,
                           diff=diff,
                           UserNameList=UserNameList,
                           CompleteImgDict=CompleteImgDict,
                           GradeImgDict=GradeImgDict)

@app.route('/TrackSearch',methods = ['GET'])
def TrackSearch():
    SearchTitle=request.args.get('title')
    SearchTitle = urllib.parse.unquote(SearchTitle)
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()
    newSearchTitle = SearchTitle
    SpecialChr=['|','*', '/', '%', '+', '-', '<', '>','&','!','"','_']
    for i in SpecialChr:
        newSearchTitle = newSearchTitle.replace(i,"\\"+i)
    newSearchTitle=newSearchTitle.replace("'","''")
    sql = """select * from TrackList where TrackTitle LIKE '%"""+newSearchTitle+"""%' ESCAPE '\\';"""
    cur.execute(sql)
    SearchTrackList = cur.fetchall()
    #print(SearchTrackList)

    TrackLen = int((len(SearchTrackList) + 49) / 50)
    AllTrack = range(0, TrackLen)

    conn.close()
    return render_template('FindTitleIndex.html',AllTrack=AllTrack,SearchTrackList=SearchTrackList,
                           DiffList=DiffList,SearchTitle=SearchTitle)


@app.route('/UserInfo.html')
def UserInfo():
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select * from UserInfo;"
    cur.execute(sql)
    UserList = cur.fetchall()

    conn.close()

    return render_template('UserInfo.html', UserList=UserList)


@app.route('/UserUpdate.html',methods = ['GET'])
def UserUpdate():
    updateuser = request.args.get('user')
    LoadingProc = "Loading..."
    return render_template('UserUpdate.html', updateuser=updateuser, LoadingProc=LoadingProc)

@app.route('/UserUpdatePROC',methods = ['GET'])
def UserUpdateProcess():
    updateuser = request.args.get('user')
    UserUpdateProc(updateuser)
    LoadingProc = "Finished!!"
    return render_template('UserUpdateFin.html', updateuser=updateuser, LoadingProc=LoadingProc)

@app.route('/About',methods = ['GET'])
def About():
    return render_template('About.html')

if __name__ == "__main__":
    app.run(debug=True)