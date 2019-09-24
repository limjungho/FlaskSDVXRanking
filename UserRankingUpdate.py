import sqlite3
from time import sleep

def UpdateRanking(AnzuID):
    UserCount = 19
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()

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

    DiffList = ['EXH', 'MXM', 'INF', 'GRV', 'HVN', 'VVD']

    sql = "update UserInfo SET FirstRankCount=0;"
    cur.execute(sql)
    conn.commit()

    sql = "select TrackID from TrackList;"
    cur.execute(sql)
    TrackList = cur.fetchall()
    FirstRankList = [0]*(UserCount+1)
    for tidtup in TrackList:
        tid = tidtup[0]
        if tid%20==0:
            print(tid)
        for diff in DiffList:
            topList = []
            sql = "select UserNumber, Score from ScoreData where TrackID = ? AND Difficulty = ?;"
            cur.execute(sql,(tid,diff))
            UserList = cur.fetchall()
            UserList = []

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
                FirstRankList[int(user)]=FirstRankList[int(user)]+1

    for i, firstcount in enumerate(FirstRankList[1:]):
        sql = "update UserInfo SET FirstRankCount=? where UserNumber=?;"
        cur.execute(sql, (firstcount,i+1))

    conn.commit()
    conn.close()


for i in range(1,20):
    print('Loading...'+str(i))
    conn = sqlite3.connect("SDVXRanking.db")
    cur = conn.cursor()
    sql = "select UserID from UserInfo where UserNumber=?"
    cur.execute(sql,(i,))
    AnzuID = cur.fetchone()[0]
    conn.close()
    UpdateRanking(AnzuID)