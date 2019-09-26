import os
from threading import Thread
from time import sleep
from flask import Flask, render_template, current_app, g, request, redirect, url_for
import sqlite3
from UserUpdate import UserUpdateProc, TrackRendering, PUCTrackRendering
from UserRankingUpdate import UpdateRanking, UpdateFirstRanking
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
    ViewPageLen = 40
    page = request.args.get('page')
    if page == None:
        page = 1
    tidpage = 1000+(int(page)-1)*ViewPageLen

    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select * from TrackList"
    cur.execute(sql)
    rows = cur.fetchall()
    TrackLen = int((len(rows) + ViewPageLen - 1) / ViewPageLen)
    AllTrack = range(0, TrackLen)

    sql = "select * from TrackList where TrackID >= ? AND TrackID <= ?;"
    cur.execute(sql,(str(tidpage+1),str(tidpage+ViewPageLen)))
    PageTrack = cur.fetchall()

    conn.close()

    NewPageTrack = TrackRendering(PageTrack)

    #print(PageTrack[0])
    #sleep(500)

    return render_template('index.html',AllTrack=AllTrack,PageTrack=NewPageTrack,DiffList=DiffList,page=page)

@app.route('/RankingPage',methods = ['GET'])
def RenderRanking():
    tid = request.args.get('tid')
    diff = request.args.get('diff')
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select UserNumber, Score, Grade, Complete from ScoreData where TrackID=? AND Difficulty=?;"
    cur.execute(sql,(tid,diff))
    RankList = cur.fetchall()
    sortedRankList = sorted(RankList, key=lambda x: x[1], reverse=True)

    sql = "select TrackTitle, {} from TrackList where TrackID= ?;".format(diff)
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

@app.route('/TrackTitleSearch', methods = ['GET'])
def TrackTitleSearch():
    ViewPageLen=40
    SearchTitle=request.args.get('title')
    SearchTitle = urllib.parse.unquote(SearchTitle)

    page = request.args.get('page')
    if page is None:
        page = 1

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

    newSearchTrackList = TrackRendering(SearchTrackList)
    newSearchTrackList = newSearchTrackList[ViewPageLen * (int(page) - 1):ViewPageLen * int(page)]

    TrackLen = int((len(SearchTrackList) + ViewPageLen) / ViewPageLen)
    AllTrack = range(0, TrackLen)

    conn.close()
    return render_template('FindTitleIndex.html',AllTrack=AllTrack,SearchTrackList=newSearchTrackList,
                           DiffList=DiffList,SearchTitle=SearchTitle,page=page)

@app.route('/TrackLevelSearch', methods = ['GET'])
def TrackLevelSearch():
    ViewPageLen = 40
    SearchLevel = request.args.get('level')
    if SearchLevel.isdigit() == False:
        return redirect(url_for('MainIndex'))

    page = request.args.get('page')
    if page is None:
        page = 1
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = """select * from TrackList where NOV=? OR ADV=? OR EXH=? OR MXM=? OR INF=? OR GRV=? OR HVN=? OR VVD=?;"""
    leveltuple = (SearchLevel,)*8
    cur.execute(sql,leveltuple)
    SearchTrackList = cur.fetchall()

    newSearchTrackList = TrackRendering(SearchTrackList)

    TrackLen = int((len(SearchTrackList) + ViewPageLen-1) / ViewPageLen)
    AllTrack = range(0, TrackLen)

    newSearchTrackList = newSearchTrackList[ViewPageLen*(int(page)-1):ViewPageLen*int(page)]

    conn.close()
    return render_template('FindLevelIndex.html',AllTrack=AllTrack,SearchTrackList=newSearchTrackList,
                           DiffList=DiffList,SearchLevel=SearchLevel,page=page)

@app.route('/UserRanking', methods = ['GET'])
def UserRanking():
    RankList = []
    level = 0
    typ = request.args.get('type')
    if typ is None:
        typ = '0'
    if typ == '1':
        RankList = EvalRankList('PUCCount')
    elif typ == '2':
        RankList = EvalRankList('PUCEXHupperCount')
    elif typ == '3':
        RankList = EvalRankList('FirstRankCount')
    elif typ == '4':
        level = request.args.get('level')
        if level is None:
            level = 0
        RankList = EvalAvgRankList(level)

    return render_template('UserRanking.html', RankList=RankList, type=typ, level=level)

def EvalAvgRankList(Avglv):
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()
    RankList = []
    if int(Avglv) is 0:
        return RankList
    sql = "select UserNumber, Average, Count from AvgData where Level=?;"
    cur.execute(sql, (Avglv,))
    AvgList = cur.fetchall()

    sortedList = sorted(AvgList, key=lambda x: x[1], reverse=True)
    sql = "select UserName from UserInfo where UserNumber=?;"
    cur.execute(sql, (sortedList[0][0],))
    UserName = cur.fetchone()[0]
    RankList.append((1, UserName, sortedList[0][1], sortedList[0][2]))

    prevRank = 1
    prevUser = sortedList[0][1]
    for rnk, user in enumerate(sortedList[1:]):
        sql = "select UserName from UserInfo where UserNumber=?;"
        cur.execute(sql, (user[0],))
        UserName = cur.fetchone()[0]
        if prevUser == user[1]:
            RankList.append((prevRank, UserName, user[1], user[2]))
        else:
            prevRank = rnk + 2
            prevUser = user[1]
            RankList.append((prevRank, UserName, user[1], user[2]))
    return RankList

def EvalRankList(rankfactor):
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select UserName, "+rankfactor+" from UserInfo;"
    cur.execute(sql)
    UserList = cur.fetchall()
    sortedList = sorted(UserList, key=lambda x: x[1], reverse=True)
    RankList = []
    RankList.append((1, sortedList[0][0], sortedList[0][1]))
    prevRank = 1
    prevUser = sortedList[0][1]
    for rnk, user in enumerate(sortedList[1:]):
        if prevUser == user[1]:
            RankList.append((prevRank, user[0], user[1]))
        else:
            prevRank = rnk + 2
            prevUser = user[1]
            RankList.append((prevRank, user[0], user[1]))
    return RankList

@app.route('/FirstRankUpdate')
def FirstRankUpdate():
    UpdateFirstRanking()
    return redirect(url_for('UserRanking', type = '3'))

@app.route('/UserInfoUpdate')
def UserInfoUpdate():
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select * from UserInfo;"
    cur.execute(sql)
    UserList = cur.fetchall()

    conn.close()

    return render_template('UserInfoUpdate.html', UserList=UserList)

@app.route('/UserPUCList', methods = ['GET'])
def UserPUCList():
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    ViewPageLen = 40
    user = request.args.get('user')
    page = request.args.get('page')
    if page == None:
        page = 1
    page = int(page)

    sql = "select UserNumber from UserInfo where UserName = ?;"
    cur.execute(sql,(user,))
    UserNum = cur.fetchone()[0]

    sql = """select TrackID, Difficulty from ScoreData where UserNumber=? and Complete='PUC' 
    and Difficulty != 'NOV' and Difficulty != 'ADV';"""
    cur.execute(sql,(UserNum,))
    PUCList = cur.fetchall()
    TrackLen = int((len(PUCList) + ViewPageLen - 1) / ViewPageLen)
    AllTrack = range(0, TrackLen)

    PUCList = PUCList[ViewPageLen*(page-1):ViewPageLen*page]
    newPUCList = []
    for track in PUCList:
        sql = "select * from TrackList where TrackID = ?;"
        cur.execute(sql, (track[0],))
        newPUCList.append(cur.fetchone()+(track[1],))
    conn.close()
    newPUCList =  PUCTrackRendering(newPUCList,user)
    return render_template('UserPUCList.html', AllTrack=AllTrack, userName=user,PageTrack=newPUCList, page=page)

@app.route('/UserUpdate',methods = ['GET'])
def UserUpdate():
    updateuser = request.args.get('user')
    LoadingProc = "Loading..."
    return render_template('UserUpdate.html', updateuser=updateuser, LoadingProc=LoadingProc)

@app.route('/UserUpdatePROC',methods = ['GET'])
def UserUpdateProcess():
    updateuser = request.args.get('user')
    UserUpdateProc(updateuser)
    UpdateRanking(updateuser)
    LoadingProc = "Finished!!"
    return render_template('UserUpdateFin.html', updateuser=updateuser, LoadingProc=LoadingProc)

@app.route('/About',methods = ['GET'])
def About():
    return render_template('About.html')

if __name__ == "__main__":
    app.run(debug=True)
