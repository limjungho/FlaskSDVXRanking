from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import sqlite3
from time import sleep
import random
import sys

class SDVXTrack:
    def __init__(self):
        self.TrackID = 0
        self.TrackTitle = ''
        self.TrackDifficulty = []

    def set(self, id, title, diff, lev, score, grade, comp):
        self.TrackID = id
        self.TrackTitle = title
        self.TrackDifficulty.append((diff,lev,score,grade, comp))
    def setDiff(self,diff,lev,score,grade, comp):
        self.TrackDifficulty.append((diff, lev,score,grade,comp))
    def setID(self, id):
        self.TrackID = id

def DecideComp(tracks):
    TrackComp = tracks.find('div', attrs={'class': 'cp play'})
    if TrackComp is not None:
        return 'PLAY'
    TrackComp = tracks.find('div', attrs={'class': 'cp comp'})
    if TrackComp is not None:
        return 'COMP'
    TrackComp = tracks.find('div', attrs={'class': 'cp comp_ex'})
    if TrackComp is not None:
        return 'COMP_EX'
    TrackComp = tracks.find('div', attrs={'class': 'cp uc'})
    if TrackComp is not None:
        return 'UC'
    TrackComp = tracks.find('div', attrs={'class': 'cp puc'})
    if TrackComp is not None:
        return 'PUC'
    return None

def DecideDiff(tracks):
    TrackLevel = tracks.find('div', attrs={'class': 'lv mxm'})
    if TrackLevel is not None:
        return 'MXM',TrackLevel.text
    TrackLevel = tracks.find('div', attrs={'class': 'lv gra'})
    if TrackLevel is not None:
        return 'GRV',TrackLevel.text
    TrackLevel = tracks.find('div', attrs={'class': 'lv vvd'})
    if TrackLevel is not None:
        return 'VVD',TrackLevel.text
    TrackLevel = tracks.find('div', attrs={'class': 'lv hvn'})
    if TrackLevel is not None:
        return 'HVN',TrackLevel.text
    TrackLevel = tracks.find('div', attrs={'class': 'lv inf'})
    if TrackLevel is not None:
        return 'INF',TrackLevel.text
    TrackLevel = tracks.find('div', attrs={'class': 'lv exh'})
    if TrackLevel is not None:
        return 'EXH',TrackLevel.text
    TrackLevel = tracks.find('div', attrs={'class': 'lv adv'})
    if TrackLevel is not None:
        return 'ADV',TrackLevel.text
    TrackLevel = tracks.find('div', attrs={'class': 'lv nov'})
    if TrackLevel is not None:
        return 'NOV',TrackLevel.text

def UserUpdateProc(AnzuID):
    TrackDict = {}
    prevhtml = ''

    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    for i in range(1,100):
        req = Request('http://anzuinfo.me/myScore.html?search_id='+AnzuID+'&sort=update_up&page='+str(i))
        res = urlopen(req)
        html = res.read().decode('utf8')
        if prevhtml == html:
            break
        prevhtml = html

        # print('Loading...'+str(i))

        bs = BeautifulSoup(html, 'html.parser')
        TrackData = bs.findAll('table', attrs={'class': 'track'})

        for tracks in TrackData:
            TrackDifficulty, TrackLevel = DecideDiff(tracks)
            TrackTitle = tracks.find('div', attrs={'class': 'title'}).text
            TrackScore = tracks.find('div', attrs={'class': 'score'}).text
            TrackGrade = tracks.find('div', attrs={'class': 'grade'}).text
            TrackComp = DecideComp(tracks)
            sql = "select TrackID from TrackList where TrackTitle = ?;"
            cur.execute(sql,(TrackTitle,))
            TrackID = str(cur.fetchone()[0])

            if TrackTitle in TrackDict:
                TrackDict[TrackTitle].setDiff(TrackDifficulty, TrackLevel,TrackScore,TrackGrade,TrackComp)
            else:
                newTrack = SDVXTrack()
                newTrack.set(TrackID, TrackTitle, TrackDifficulty, TrackLevel,TrackScore,TrackGrade,TrackComp)
                TrackDict[TrackTitle] = newTrack
        sleep(0.01)

    TrackIdDict = {}
    TrackIdDict = dict((value.TrackID, value) for key, value in TrackDict.items())

    sql = "select UserNumber from UserInfo where UserID = ?;"
    cur.execute(sql, (AnzuID,))
    UserNum = str(cur.fetchone()[0])

    ScoreID = ''

    for id in TrackIdDict:
        for dff in TrackIdDict[id].TrackDifficulty:
            ScoreID = str(UserNum) + str(id) + dff[0]
            sql = 'select ScoreID from ScoreData where ScoreID = ?;'
            cur.execute(sql, (ScoreID,))
            checksid = cur.fetchone()
            if checksid is not None:
                sql = "update ScoreData SET Score = ?, Grade = ?, Complete = ? where ScoreID = ?;"
                cur.execute(sql, (str(dff[2]), dff[3], dff[4], str(ScoreID)))
            else:
                sql = "insert into ScoreData VALUES (?, ?, ?, ?, ?, ?, ?);"
                cur.execute(sql, (str(ScoreID), UserNum, id, dff[0], str(dff[2]), dff[3], dff[4]))
    conn.commit()

    conn.close()

DiffList = ['NOV', 'ADV', 'EXH', 'MXM', 'INF', 'GRV', 'HVN', 'VVD']

def PUCTrackRendering(PageTrack, showtop):
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    NewPageTrack = []

    for i, track in enumerate(PageTrack):
        if i>0:
            if track[1] == PageTrack[i-1][1]:
                continue
        if i<len(PageTrack)-1:
            if track[1] == PageTrack[i+1][1]:
                MXMLv = '??'
                RealDiff = '??'
                for j in range(5, 10):
                    if PageTrack[i+1][j] is not None:
                        MXMLv = PageTrack[i+1][j]
                        RealDiff = DiffList[j - 2]
                        break
                NewPageTrack.append((track[1], track[4], MXMLv, track[0], RealDiff, showtop, showtop))
                #print(NewPageTrack[-1])
                continue

        EXHLv = '??'
        MXMLv = '??'
        diff = track[-1]
        if diff == 'EXH':
            EXHLv = track[4]
        else:
            for i in range(5, 10):
                if track[i] is not None:
                    MXMLv = track[i]
        NewPageTrack.append((track[1], EXHLv, MXMLv, track[0], diff, showtop, showtop))

    conn.close()

    return NewPageTrack


def TrackRendering(PageTrack):
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    NewPageTrack = []

    for track in PageTrack:
        MXMLv = '??'
        RealDiff='??'
        for i in range(5,10):
            if track[i] is not None:
                MXMLv = track[i]
                RealDiff=DiffList[i-2]
        EXHtop = 'WF.XXXXX'
        MXMtop = 'WF.XXXXX'
        sql = "select UserNumber, Score from ScoreData where TrackID=? AND Difficulty=?;"
        cur.execute(sql, (track[0],'EXH'))
        UserEXHList = cur.fetchall()
        EXHtopList=[]
        MXMtopList=[]
        if UserEXHList:
            sortedEXHList = sorted(UserEXHList, key=lambda x: x[1], reverse=True)
            EXHtopList.append(sortedEXHList[0][0])
            for i in range(1,len(sortedEXHList)):
                if sortedEXHList[i][1] == sortedEXHList[i-1][1]:
                    EXHtopList.append(sortedEXHList[i][0])
                else:
                    break
            EXHtop = random.choice(EXHtopList)
            sql = "select UserName from UserInfo where UserNumber = ?;"
            cur.execute(sql, (EXHtop,))
            EXHtop = cur.fetchone()[0]
        if MXMLv is not '??':
            sql = "select UserNumber, Score from ScoreData where TrackID=? AND Difficulty=?;"
            cur.execute(sql, (track[0], RealDiff))
            UserMXMList = cur.fetchall()
            if UserMXMList:
                sortedMXMList = sorted(UserMXMList, key=lambda x: x[1], reverse=True)
                MXMtopList.append(sortedMXMList[0][0])
                for i in range(1, len(sortedMXMList)):
                    if sortedMXMList[i][1] == sortedMXMList[i - 1][1]:
                        MXMtopList.append(sortedMXMList[i][0])
                    else:
                        break
                MXMtop = random.choice(MXMtopList)
                sql = "select UserName from UserInfo where UserNumber = ?;"
                cur.execute(sql, (MXMtop,))
                MXMtop = cur.fetchone()[0]

        NewPageTrack.append((track[1], track[4], MXMLv, track[0],RealDiff,EXHtop,MXMtop))

    conn.close()

    return NewPageTrack