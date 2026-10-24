from datetime import date, timedelta
import uuid
import os
import hmac
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from db import connect, init_db

app=FastAPI(title="Green Steps Run API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
init_db()

class RunIn(BaseModel):
    bib:int
    km:float=Field(gt=0, le=300)
    pin:str=Field(min_length=1, max_length=32)
    run_date:date|None=None

class PledgeIn(BaseModel):
    event_id:int
    runner_bib:int|None=None
    sponsor_name:str=Field(min_length=1,max_length=100)
    nok_per_km:float=Field(gt=0,le=100000)
    max_cap:float|None=Field(default=None,gt=0)

def rows(sql,args=()):
    with connect() as db: return [dict(r) for r in db.execute(sql,args).fetchall()]
def one(sql,args=()):
    r=rows(sql,args); return r[0] if r else None

def runner_public(r):
    runs=rows("SELECT km,run_date FROM runs WHERE runner_id=?",(r["id"],))
    km=round(sum(x["km"] for x in runs),1)
    pledges=rows("SELECT nok_per_km,max_cap FROM pledges WHERE runner_id=? OR (event_id=? AND runner_id IS NULL)",(r["id"],r["event_id"]))
    raised=0
    for p in pledges:
        amount=sum(x["km"] for x in runs)*p["nok_per_km"]
        raised+=min(amount,p["max_cap"]) if p["max_cap"] else amount
    return {"id":r["id"],"bib":r["bib"],"name":r["name"],"faculty":r["faculty"],"event_id":r["event_id"],"total_km":km,"trees":int(raised//50),"raised_nok":round(raised,2)}

@app.get("/api/health")
def health(): return {"ok":True}
@app.get("/api/events")
def events():
    out=[]
    for e in rows("SELECT * FROM events ORDER BY id"):
        rs=rows("SELECT * FROM runners WHERE event_id=?",(e["id"],))
        out.append({**e,"runner_count":len(rs),"total_km":round(sum(runner_public(r)["total_km"] for r in rs),1)})
    return out
@app.get("/api/leaderboard")
def leaderboard(event_id:int|None=None):
    rs=rows("SELECT * FROM runners"+(" WHERE event_id=?" if event_id else ""),((event_id,) if event_id else ()))
    return sorted([runner_public(r) for r in rs],key=lambda x:(-x["trees"],-x["total_km"]))
@app.get("/api/runners/{bib}")
def runner(bib:int):
    r=one("SELECT * FROM runners WHERE bib=?",(bib,))
    if not r: raise HTTPException(404,"Runner not found")
    return {**runner_public(r),"runs":rows("SELECT km,run_date FROM runs WHERE runner_id=? ORDER BY run_date DESC",(r["id"],))}
@app.post("/api/runs")
def log_run(payload:RunIn):
    expected=os.getenv("ORGANIZER_PIN", "1234")
    if not hmac.compare_digest(payload.pin, expected):
        raise HTTPException(401, "Incorrect organiser PIN")
    r=one("SELECT * FROM runners WHERE bib=?",(payload.bib,))
    if not r: raise HTTPException(404,"Runner bib not found")
    with connect() as db: db.execute("INSERT INTO runs(runner_id,km,run_date) VALUES (?,?,?)",(r["id"],payload.km,str(payload.run_date or date.today())))
    return {"ok":True,"runner":runner_public(r)}
@app.post("/api/pledges")
def create_pledge(p:PledgeIn):
    if not one("SELECT id FROM events WHERE id=?",(p.event_id,)): raise HTTPException(404,"Event not found")
    rid=None
    if p.runner_bib:
        r=one("SELECT * FROM runners WHERE bib=? AND event_id=?",(p.runner_bib,p.event_id))
        if not r: raise HTTPException(404,"Runner not found in this event")
        rid=r["id"]
    pid=str(uuid.uuid4())
    with connect() as db:
        db.execute("INSERT INTO pledges VALUES (?,?,?,?,?,?,?)",(pid,p.event_id,rid,p.sponsor_name.strip(),p.nok_per_km,p.max_cap,str(date.today())))
    return {"id":pid,"url":f"/thanks/{pid}"}
@app.get("/api/pledges/{pid}")
def pledge_thanks(pid:str):
    p=one("SELECT p.*,r.bib runner_bib,r.name runner_name,e.name event_name FROM pledges p LEFT JOIN runners r ON r.id=p.runner_id JOIN events e ON e.id=p.event_id WHERE p.id=?",(pid,))
    if not p: raise HTTPException(404,"Pledge not found")
    km=one("SELECT COALESCE(SUM(r.km),0) km FROM runs r JOIN runners u ON u.id=r.runner_id WHERE (? IS NULL OR r.runner_id=?) AND (? IS NOT NULL OR u.event_id=?)",(p["runner_id"],p["runner_id"],p["runner_id"],p["event_id"]))["km"]
    amount=km*p["nok_per_km"]
    if p["max_cap"]: amount=min(amount,p["max_cap"])
    trees=int(amount//50)
    return {"pledge":{**p,"current_amount":round(amount,2)},"event_name":p["event_name"],"trees":trees,"km_counted":round(km,1),"km_per_tree":round(50/p["nok_per_km"],2)}
@app.get("/api/recap")
def recap(period:str="last7"):
    today=date.today(); start=today-timedelta(days=6 if period=="last7" else today.weekday())
    runs=rows("SELECT r.km,u.id runner_pk,u.event_id,u.name,u.bib,u.faculty FROM runs r JOIN runners u ON u.id=r.runner_id WHERE r.run_date>=?",(str(start),))
    pledges=rows("SELECT runner_id,event_id,nok_per_km FROM pledges")
    by={}; fac={}
    for x in runs:
        rate=sum(p["nok_per_km"] for p in pledges if p["runner_id"]==x["runner_pk"] or (p["runner_id"] is None and p["event_id"]==x["event_id"]))
        a=by.setdefault(x["bib"],{"bib":x["bib"],"name":x["name"],"faculty":x["faculty"],"km":0,"nok":0})
        a["km"]+=x["km"]; a["nok"]+=x["km"]*rate
        f=fac.setdefault(x["faculty"],{"faculty":x["faculty"],"km":0,"nok":0})
        f["km"]+=x["km"]; f["nok"]+=x["km"]*rate
    for d in list(by.values())+list(fac.values()):
        d["trees_gained"]=int(d["nok"]//50); d["km"]=round(d["km"],1); d["nok"]=round(d["nok"],2)
    ranked=list(by.values()); total=sum(a["nok"] for a in ranked)
    return {"period":period,"start":str(start),"end":str(today),"new_km":round(sum(x["km"] for x in runs),1),"new_trees":int(total//50),"new_nok":round(total,2),
            "top_runner_by_trees":max(ranked,key=lambda x:(x["trees_gained"],x["km"]),default=None),
            "top_runner_by_km":max(ranked,key=lambda x:x["km"],default=None),
            "fastest_faculty":max(fac.values(),key=lambda x:(x["trees_gained"],x["km"]),default=None)}
@app.get("/api/faculty")
def faculty(name:str):
    rs=rows("SELECT * FROM runners WHERE faculty=?",(name,))
    if not rs: raise HTTPException(404,"Faculty not found")
    all_fac=[]
    for f in sorted(set(x["faculty"] for x in rows("SELECT faculty FROM runners"))):
        fr=rows("SELECT * FROM runners WHERE faculty=?",(f,))
        all_fac.append({"faculty":f,"trees":sum(runner_public(r)["trees"] for r in fr),"total_km":sum(runner_public(r)["total_km"] for r in fr)})
    all_fac.sort(key=lambda x:(-x["trees"],-x["total_km"]))
    item=next(x for x in all_fac if x["faculty"]==name); rank=all_fac.index(item)+1
    rival=all_fac[rank-2] if rank>1 else (all_fac[1] if len(all_fac)>1 else None)
    return {"faculty":name,"runner_count":len(rs),"total_km":round(sum(runner_public(r)["total_km"] for r in rs),1),"raised_nok":sum(runner_public(r)["raised_nok"] for r in rs),"trees":item["trees"],"rank":rank,"faculty_count":len(all_fac),"rival_name":rival["faculty"] if rival else None,"rival_gap":abs(item["trees"]-rival["trees"]) if rival else 0,"runners":[runner_public(r) for r in rs]}
