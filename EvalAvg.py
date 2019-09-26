import sqlite3
from time import sleep

conn = sqlite3.connect("SDVXRanking.db")
cur = conn.cursor()

"""
sql1 = 'CREATE TABLE UserInfo_B AS SELECT UserNumber,UserID,UserName,PUCcount,PUCEXHupperCount,FirstRankCount FROM UserInfo;'
sql2 = 'DROP TABLE UserInfo;'
sql3 = 'ALTER TABLE UserInfo_B RENAME TO UserInfo;'

cur.execute(sql1)
cur.execute(sql2)
cur.execute(sql3)

for i in range(1,21):
    sql = "ALTER TABLE UserInfo ADD COLUMN Avg"+str(i)+" INTEGER;"
    cur.execute(sql)
"""


sql = "select UserNumber from UserInfo;"
cur.execute(sql)
UserList = cur.fetchall()
UserCount = len(UserList)

for usr in range(1,20):
    print('Loading..'+str(usr))
    SumList = [0]*21
    CountList = [0]*21
    sql = "select * from TrackList;"
    cur.execute(sql)
    TrackList = cur.fetchall()

    sql = "select TrackID, Difficulty, Score from ScoreData where UserNumber=?;"
    cur.execute(sql, (usr,))
    ScoreList = cur.fetchall()

    for score in ScoreList:
        sql = "select "+score[1]+" from TrackList where TrackID = "+score[0]+";"
        cur.execute(sql)
        Level = cur.fetchone()[0]
        SumList[int(Level)]=SumList[int(Level)]+ int(score[2])
        CountList[int(Level)] = CountList[int(Level)] + 1
    AvgList = [0]*21
    for i in range(1,21):
        if CountList[i] is not 0:
            AvgList[i] = int(SumList[i]/CountList[i])
    for i in range(1,21):
        sql = "insert into AvgData VALUES (?, ?, ?, ?, ?);"
        cur.execute(sql, (str(usr)+str(i).zfill(2),usr,i,AvgList[i],CountList[i]))

conn.commit()
conn.close()