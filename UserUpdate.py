from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import sqlite3
from time import sleep
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