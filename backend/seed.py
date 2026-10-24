from datetime import date, timedelta
import uuid
from db import connect, init_db

def seed():
    init_db()
    with connect() as db:
        db.execute("DELETE FROM runs")
        db.execute("DELETE FROM pledges")
        db.execute("DELETE FROM runners")
        db.execute("DELETE FROM events")
        db.execute("INSERT INTO events VALUES (1,?,?,?)", ("Campus Forest Marathon", str(date.today()), "Oslo, Norway"))
        db.execute("INSERT INTO events VALUES (2,?,?,?)", ("Fjord Steps Challenge", str(date.today()+timedelta(days=14)), "Bergen, Norway"))
        runners = [
            (1001,"Ingrid Larsen","Faculty of Science",1),
            (1002,"Jonas Berg","School of Business",1),
            (1003,"Amira Haddad","Faculty of Medicine",1),
            (1004,"Elias Nilsen","School of Business",1),
            (1005,"Sofie Dahl","Faculty of Humanities",2),
            (1006,"Noah Hansen","Faculty of Medicine",2),
        ]
        db.executemany("INSERT INTO runners(bib,name,faculty,event_id) VALUES (?,?,?,?)", runners)
        today=date.today()
        runs = [(1001,8.5,1),(1001,5.2,3),(1002,9.4,2),(1003,12.0,1),(1003,7.5,2),
                (1004,4.5,4),(1005,15.2,1),(1006,6.4,2)]
        for bib,km,days_ago in runs:
            rid=db.execute("SELECT id FROM runners WHERE bib=?",(bib,)).fetchone()["id"]
            db.execute("INSERT INTO runs(runner_id,km,run_date) VALUES (?,?,?)",(rid,km,str(today-timedelta(days=days_ago))))
        for ev,sponsor,rate,cap,bib,age in [
            (1,"Kafé Lyng",20,2000,None,12),(1,"Grandma Berit",50,1000,1001,12),
            (1,"Student Union",30,None,1003,1),(1,"Uncle Ole",25,500,1002,12),
            (2,"Fjord Sports AS",40,1500,None,12),(2,"Mum & Dad",60,None,1005,3)]:
            rid=db.execute("SELECT id FROM runners WHERE bib=?",(bib,)).fetchone()["id"] if bib else None
            db.execute("INSERT INTO pledges VALUES (?,?,?,?,?,?,?)",
                       (str(uuid.uuid4()),ev,rid,sponsor,rate,cap,str(today-timedelta(days=age))))
    print("Seeded demo events, runners, runs, and pledges.")
if __name__=="__main__": seed()
