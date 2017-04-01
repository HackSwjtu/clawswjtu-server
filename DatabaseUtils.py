#!/usr/bin/python3
# -*- encoding: utf-8 -*-
from sqlalchemy import create_engine
import pymysql
from datetime import *


engine = create_engine("mysql+pymysql://root:password@ip:port/db?charset=utf8", encoding='utf-8', pool_size=100, pool_recycle=3600, echo=True)

def getlastweeklecture():
    conn = engine.raw_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Lecture WHERE lecturetime <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) order by lecturetime")
    lecture = []

    for each in cur.fetchall():
        #print(each)
        id = each[0]
        title = each[1]
        time = datetime.strftime(each[2], '%Y-%m-%d %H:%M')
        place = each[3]
        speaker = each[4]
        speakerbrif = each[5]
        detail = each[6]
        lecture.append({"id": id, "title": title, "time": time, "place": place, "speaker": speaker, "speakerbrif": speakerbrif, "detail": detail})
    data = {"lecture": lecture}
    print(data)
    conn.close()
    return data

def searchlecture(keyword):
    conn = engine.raw_connection()
    cur = conn.cursor()
    keyword = str(keyword).replace(" ","%")
    keyword = "%" + keyword + "%"
    cur.execute("SELECT * FROM Lecture WHERE title LIKE %s", (keyword))
    lecture = []

    for each in cur.fetchall():
        id = each[0]
        title = each[1]
        time = datetime.strftime(each[2], '%Y-%m-%d %H:%M')
        place = each[3]
        speaker = each[4]
        speakerbrif = each[5]
        detail = each[6]
        lecture.append({"id": id, "title": title, "time": time, "place": place, "speaker": speaker, "speakerbrif": speakerbrif, "detail": detail})
    data = {"lecture": lecture}
    print(data)
    conn.close()
    return data

def test():
    getlastweeklecture()

