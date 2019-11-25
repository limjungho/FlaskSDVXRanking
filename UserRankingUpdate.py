import sqlite3
from time import sleep

def UpdateRanking(AnzuID):
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select UserNumber from UserInfo;"
    cur.execute(sql)
    UserList = cur.fetchall()
    UserCount = len(UserList)+1

    sql = "select UserNumber from UserInfo where UserID = ?;"
    cur.execute(sql, (AnzuID,))
    UserNum = str(cur.fetchone()[0])

    sql = "select ScoreID from ScoreData where UserNumber=? and Complete='PUC';"
    cur.execute(sql,(UserNum,))
    PUCList = cur.fetchall()
    PUCCount = len(PUCList)
    sql = "update UserInfo SET PUCCount = ? where UserNumber=?;"
    cur.execute(sql,(PUCCount,UserNum))

    sql = "select ScoreID from ScoreData where UserNumber=? and Complete='PUC' and Difficulty != 'NOV' and Difficulty != 'ADV';"
    cur.execute(sql, (UserNum,))
    PUCList = cur.fetchall()
    PUCCount = len(PUCList)
    sql = "update UserInfo SET PUCEXHupperCount = ? where UserNumber=?;"
    cur.execute(sql, (PUCCount, UserNum))

    for i in range(1,UserCount):
        SumList = [0] * UserCount
        CountList = [0] * UserCount
        sql = "select TrackID, Difficulty, Score from ScoreData where UserNumber=?;"
        cur.execute(sql, (UserNum,))
        ScoreList = cur.fetchall()
        for score in ScoreList:
            sql = "select " + score[1] + " from TrackList where TrackID = " + score[0] + ";"
            cur.execute(sql)
            Level = cur.fetchone()[0]
            SumList[int(Level)] = SumList[int(Level)] + int(score[2])
            CountList[int(Level)] = CountList[int(Level)] + 1
        AvgList = [0] * UserCount
        for i in range(1, UserCount):
            if CountList[i] is not 0:
                AvgList[i] = int(SumList[i] / CountList[i])
        for i in range(1, UserCount):
            sql = "select * from AvgData where UserNumber=?;"
            cur.execute(sql, (UserNum,))
            checkList = cur.fetchall()
            if not checkList:
                for j in range(1,21):
                    sql = "INSERT INTO AvgData VALUES(?, ?, ?, ?, ?, ?);"
                    cur.execute(sql, (str(UserNum)+str(j).zfill(2), UserNum, j, 0,0,0))
            sql = "update AvgData SET Average=?, Count=?, Sum=? where UserNumber=? and Level=?;"
            cur.execute(sql, (AvgList[i],CountList[i],SumList[i],UserNum,i))

    conn.commit()
    conn.close()

def UpdateFirstRanking():
    DiffList = ['EXH', 'MXM', 'INF', 'GRV', 'HVN', 'VVD']

    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select UserNumber from UserInfo;"
    cur.execute(sql)
    UserList = cur.fetchall()
    UserCount = len(UserList)

    sql = "select TrackID from TrackList;"
    cur.execute(sql)
    TrackList = cur.fetchall()
    FirstRankList = [0] * (UserCount + 1)
    for tidtup in TrackList:
        tid = tidtup[0]

        if tid % 100 == 0:
            print(tid)

        for diff in DiffList:
            topList = []
            sql = "select UserNumber, Score from ScoreData where TrackID = ? AND Difficulty = ?;"
            cur.execute(sql, (tid, diff))
            UserList = cur.fetchall()
            if not UserList:
                continue
            sortedUserList = sorted(UserList, key=lambda x: x[1], reverse=True)
            topList.append(sortedUserList[0][0])
            for i in range(1, len(sortedUserList)):
                if sortedUserList[i][1] == sortedUserList[i - 1][1]:
                    topList.append(sortedUserList[i][0])
                else:
                    break
            for user in topList:
                FirstRankList[int(user)] = FirstRankList[int(user)] + 1
    for i, firstcount in enumerate(FirstRankList[1:]):
        sql = "update UserInfo SET FirstRankCount=? where UserNumber=?;"
        cur.execute(sql, (firstcount, i + 1))

    conn.commit()
    conn.close()


def UpdateFirst18LvRanking():
    DiffList = ['EXH', 'MXM', 'INF', 'GRV', 'HVN', 'VVD']

    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

    sql = "select UserNumber from UserInfo;"
    cur.execute(sql)
    UserList = cur.fetchall()
    UserCount = len(UserList)

    sql = "select TrackID from TrackList;"
    cur.execute(sql)
    TrackList = cur.fetchall()
    FirstRankList = [0] * (UserCount + 1)
    for tidtup in TrackList:
        tid = tidtup[0]
        for diff in DiffList:
            sql = "select "+diff+" from TrackList where TrackID = ?;"
            cur.execute(sql, (tid, ))
            chDiff18 = cur.fetchone()
            if not chDiff18[0]:
                continue
            if int(chDiff18[0]) != 18:
                continue

            topList = []
            sql = "select UserNumber, Score from ScoreData where TrackID = ? AND Difficulty = ?;"
            cur.execute(sql, (tid, diff))
            UserList = cur.fetchall()
            if not UserList:
                continue
            sortedUserList = sorted(UserList, key=lambda x: x[1], reverse=True)
            topList.append(sortedUserList[0][0])
            for i in range(1, len(sortedUserList)):
                if sortedUserList[i][1] == sortedUserList[i - 1][1]:
                    topList.append(sortedUserList[i][0])
                else:
                    break
            for user in topList:
                FirstRankList[int(user)] = FirstRankList[int(user)] + 1
    for i, firstcount in enumerate(FirstRankList[1:]):
        sql = "update UserInfo SET First18LvCount=? where UserNumber=?;"
        cur.execute(sql, (firstcount, i + 1))

    conn.commit()
    conn.close()

'''
conn = sqlite3.connect("SDVXRanking.db")
cur = conn.cursor()

sql = "select UserNumber from UserInfo;"
cur.execute(sql)
UserList = cur.fetchall()
UserCount = len(UserList)

for i in range(1,UserCount+1):
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()
    sql = "select UserID from UserInfo where UserNumber=?"
    cur.execute(sql,(i,))
    AnzuID = cur.fetchone()[0]
    conn.close()
    UpdateRanking(AnzuID)

UpdateFirstRanking()
'''

