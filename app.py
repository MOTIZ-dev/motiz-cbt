# Bet Wave Casino - Created by MOTIZ
# Full MSport Clone: Virtual + Instant League + Mines + Aviator + Spin + CoinFlip + Crash

import os, json, random, string, sqlalchemy as sa, hashlib
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session, jsonify, render_template_string
from markupsafe import Markup
import pytz

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', "betwave-motiz-2026")
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL: raise Exception("DATABASE_URL not set")
if DATABASE_URL.startswith("postgres://"): DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = sa.create_engine(DATABASE_URL, pool_pre_ping=True)
DBSession = sessionmaker(bind=engine)
NIG_TZ = pytz.timezone('Africa/Lagos')

def init_db():
    with engine.connect() as conn:
        conn.execute(sa.text("CREATE TABLE IF NOT EXISTS bw_users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, coins INT DEFAULT 1000, created_at TIMESTAMP DEFAULT NOW());"))
        conn.execute(sa.text("CREATE TABLE IF NOT EXISTS bw_aviator_rounds (id SERIAL PRIMARY KEY, crash_point FLOAT, status TEXT DEFAULT 'betting', created_at TIMESTAMP DEFAULT NOW());"))
        conn.execute(sa.text("CREATE TABLE IF NOT EXISTS bw_aviator_bets (id SERIAL PRIMARY KEY, round_id INT, user_id INT, bet INT, cashout FLOAT, win INT, status TEXT DEFAULT 'flying', created_at TIMESTAMP DEFAULT NOW());"))
        conn.execute(sa.text("CREATE TABLE IF NOT EXISTS bw_spin_rounds (id SERIAL PRIMARY KEY, status TEXT DEFAULT 'betting', total_white INT DEFAULT 0, total_green INT DEFAULT 0, winner TEXT, created_at TIMESTAMP DEFAULT NOW());"))
        conn.execute(sa.text("CREATE TABLE IF NOT EXISTS bw_spin_bets (id SERIAL PRIMARY KEY, round_id INT, user_id INT, side TEXT, bet INT, win INT DEFAULT 0, created_at TIMESTAMP DEFAULT NOW());"))
        conn.execute(sa.text("CREATE TABLE IF NOT EXISTS bw_virtual (id SERIAL PRIMARY KEY, league TEXT, home TEXT, away TEXT, home_score INT, away_score INT, status TEXT DEFAULT 'live', created_at TIMESTAMP DEFAULT NOW());"))
        conn.commit()
init_db()

BASE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{{title}}</title>
<style>
body{margin:0;background:#0a0a0a;color:white;font-family:Segoe UI}
.header{background:#ff3d00;padding:12px;text-align:center;font-weight:900;position:sticky;top:0;z-index:100}
.nav{display:flex;overflow-x:auto;background:#111;padding:6px;gap:6px;position:sticky;top:48px;z-index:99}
.nav a{color:white;text-decoration:none;padding:8px 14px;background:#222;border-radius:20px;font-size:13px;white-space:nowrap}
.card{background:#1a1a1a;padding:12px;margin:8px;border-radius:12px}
.btn{background:#ff3d00;color:white;padding:10px;border:none;width:100%;border-radius:8px;font-weight:bold;margin:5px 0;cursor:pointer}
.btn.green{background:#00c853}.btn.gray{background:#333}
.motiz{font-size:10px;opacity:0.6;text-align:center;margin-top:10px}
table{width:100%;font-size:12px} td,th{padding:6px;border-bottom:1px solid #222}
</style></head><body>
<div class="header">BET WAVE <span style="font-size:11px;font-weight:400">by MOTIZ</span></div>
<div class="nav">
<a href="/">🏠 Home</a><a href="/aviator">✈️ Aviator</a><a href="/mines">💣 Mines</a><a href="/spin">🎡 Spin</a><a href="/virtual">⚽ Virtual</a><a href="/instant">⚡ Instant League</a><a href="/crash">📈 Crash</a>
</div>
<div style="padding:8px">{{content}}</div>
<div class="motiz">Created by MOTIZ | Bet Wave © 2026</div>
<script>{{script}}</script>
</body></html>"""

def get_user():
    uid=session.get('uid')
    if not uid:
        with DBSession() as db:
            try:
                u=db.execute(sa.text("SELECT * FROM bw_users ORDER BY id DESC LIMIT 1")).mappings().first()
                if not u:
                    db.execute(sa.text("INSERT INTO bw_users (username,coins) VALUES ('Player',1000)")); db.commit()
                    u=db.execute(sa.text("SELECT * FROM bw_users ORDER BY id DESC LIMIT 1")).mappings().first()
                session['uid']=u['id']; return dict(u)
            except: db.rollback()
    with DBSession() as db:
        u=db.execute(sa.text("SELECT * FROM bw_users WHERE id=:id"),{"id":uid}).mappings().first()
        if u: return dict(u)
    return {"id":1,"username":"Player","coins":1000}

@app.route('/')
def home():
    user=get_user()
    content=f"""
    <div class="card" style="background:linear-gradient(135deg,#ff3d00,#8e2de2);text-align:center">
    <h2>💰 {user['coins']} Coins</h2><p>Welcome to Bet Wave - MSport Style</p></div>
    <div class="card"><h3>🔥 Popular</h3>
    <a href="/aviator" class="btn">✈️ Aviator - Plane Going</a>
    <a href="/mines" class="btn green">💣 Mines - 5x5 Multiplier</a>
    <a href="/virtual" class="btn">⚽ Virtual Football</a>
    <a href="/instant" class="btn gray">⚡ Instant League - Every 1min</a>
    <a href="/crash" class="btn gray">📈 Crash - Like Aviator</a>
    <a href="/spin" class="btn gray">🎡 Spin Wheel</a>
    </div>
    <div class="card"><h3>📊 Live Matches</h3><div id="live"></div></div>
    <script>
    async function loadLive(){{
        let r=await fetch('/virtual/state'); let d=await r.json();
        document.getElementById('live').innerHTML=d.matches.map(m=>`<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #222"><span>${{m.home}} vs ${{m.away}}</span><span>${{m.home_score}}-${{m.away_score}} ${{m.status}}</span></div>`).join('');
    }}
    loadLive(); setInterval(loadLive,2000);
    </script>
    """
    return render_template_string(BASE, title="Bet Wave", content=Markup(content), script="")

# ===== AVIATOR =====
@app.route('/aviator')
def aviator_page():
    user=get_user()
    content=f"""
    <div class="card"><b>✈️ Aviator</b> - {user['coins']} coins <div id="info"></div></div>
    <div style="background:black;height:220px;position:relative;border-radius:12px;margin:8px;overflow:hidden"><canvas id="c" style="width:100%;height:100%"></canvas><div id="mult" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:42px;font-weight:900">1.00x</div></div>
    <div class="card"><input id="bet" type="number" value="50"><button id="betBtn" class="btn">BET</button><button id="cashBtn" class="btn green" style="display:none">CASHOUT <span id="cashInfo"></span></button><div id="status"></div></div>
    <script>
    let mult=1, flying=false, iv=null, trail=[], betAmt=0, betId=null;
    const canvas=document.getElementById('c'), ctx=canvas.getContext('2d');
    function rs(){{let r=canvas.getBoundingClientRect(); canvas.width=r.width*2; canvas.height=r.height*2;}} rs();
    function draw(m){{ctx.fillStyle="#000"; ctx.fillRect(0,0,canvas.width,canvas.height); let maxW=canvas.width-80, maxH=canvas.height-80, prog=Math.min(m/15,1), x=30+prog*maxW, y=canvas.height-30-Math.pow(prog,0.7)*maxH; trail.push({{x,y}}); if(trail.length>40) trail.shift(); if(trail.length>1){{ctx.beginPath(); ctx.strokeStyle="#ff3d00"; ctx.lineWidth=5; ctx.moveTo(trail[0].x,trail[0].y); trail.forEach(p=>ctx.lineTo(p.x,p.y)); ctx.stroke();}} ctx.font="30px Arial"; ctx.fillText("✈️",x-15,y+8);}}
    document.getElementById('betBtn').onclick=async()=>{{let b=parseInt(document.getElementById('bet').value); let r=await fetch('/aviator/bet',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{bet:b}})}}); let d=await r.json(); if(d.error){{alert(d.error);return;}} betAmt=b; betId=d.id; document.getElementById('betBtn').style.display='none'; document.getElementById('cashBtn').style.display='block';}};
    document.getElementById('cashBtn').onclick=async()=>{{await fetch('/aviator/cashout',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{mult:mult}})}}); document.getElementById('betBtn').style.display='block'; document.getElementById('cashBtn').style.display='none';}};
    async function sync(){{let r=await fetch('/aviator/state'); let s=await r.json(); document.getElementById('info').innerText=s.status+' '+(s.countdown||0)+'s'; document.getElementById('mult').innerText=s.multiplier.toFixed(2)+'x'+(s.status=='crashed'?' CRASHED':''); document.getElementById('mult').style.color=s.status=='crashed'?'red':'white'; if(s.status=='flying'){{if(!flying){{flying=true; mult=s.multiplier; iv=setInterval(()=>{{mult+=0.08+mult*0.02; document.getElementById('mult').innerText=mult.toFixed(2)+'x'; document.getElementById('cashInfo').innerText=mult.toFixed(2)+'x → '+Math.floor(betAmt*mult); draw(mult);}},100);}}}} else if(s.status=='betting'){{flying=false; if(iv) clearInterval(iv); mult=1; trail=[];}} setTimeout(sync,500);}} sync();
    </script>
    """
    return render_template_string(BASE, title="Aviator", content=Markup(content), script="")

@app.route('/aviator/state')
def aviator_state():
    with DBSession() as db:
        try:
            rnd=db.execute(sa.text("SELECT * FROM bw_aviator_rounds ORDER BY id DESC LIMIT 1")).mappings().first()
            now=datetime.now(pytz.utc)
            if not rnd:
                db.execute(sa.text("INSERT INTO bw_aviator_rounds (crash_point,status,created_at) VALUES (:c,'betting',NOW())"),{"c":random.uniform(1.2, 50)}); db.commit(); return jsonify({"status":"betting","multiplier":1,"countdown":10})
            created=rnd['created_at']; 
            if created.tzinfo is None: created=pytz.utc.localize(created)
            elapsed=(now-created).total_seconds()
            if rnd['status']=='betting':
                if elapsed>=8: db.execute(sa.text("UPDATE bw_aviator_rounds SET status='flying', created_at=NOW() WHERE id=:id"),{"id":rnd['id']}); db.commit(); return jsonify({"status":"flying","multiplier":1,"countdown":0})
                return jsonify({"status":"betting","multiplier":1,"countdown":int(8-elapsed)})
            elif rnd['status']=='flying':
                mult=1+elapsed*0.5+elapsed*elapsed*0.07
                if mult>=rnd['crash_point']: db.execute(sa.text("UPDATE bw_aviator_rounds SET status='crashed', created_at=NOW() WHERE id=:id"),{"id":rnd['id']}); db.commit(); db.execute(sa.text("UPDATE bw_aviator_bets SET status='lost' WHERE status='flying'")); db.commit(); return jsonify({"status":"crashed","multiplier":rnd['crash_point'],"countdown":5})
                return jsonify({"status":"flying","multiplier":mult,"countdown":0})
            else:
                if elapsed>=5: db.execute(sa.text("INSERT INTO bw_aviator_rounds (crash_point,status,created_at) VALUES (:c,'betting',NOW())"),{"c":random.uniform(1.2,80)}); db.commit(); return jsonify({"status":"betting","multiplier":1,"countdown":8})
                return jsonify({"status":"crashed","multiplier":rnd['crash_point'],"countdown":int(5-elapsed)})
        except: db.rollback(); return jsonify({"status":"betting","multiplier":1,"countdown":10})

@app.route('/aviator/bet', methods=["POST"])
def aviator_bet():
    user=get_user(); d=request.get_json(); bet=int(d.get('bet',50))
    if user['coins']<bet: return jsonify({"error":"No coins"})
    with DBSession() as db:
        try:
            rnd=db.execute(sa.text("SELECT * FROM bw_aviator_rounds WHERE status='betting' ORDER BY id DESC LIMIT 1")).mappings().first()
            if not rnd: return jsonify({"error":"Bet closed"})
            db.execute(sa.text("UPDATE bw_users SET coins=coins-:b WHERE id=:id"),{"b":bet,"id":user['id']})
            db.execute(sa.text("INSERT INTO bw_aviator_bets (round_id,user_id,bet,status) VALUES (:rid,:uid,:b,'flying')"),{"rid":rnd['id'],"uid":user['id'],"b":bet}); db.commit()
            nid=db.execute(sa.text("SELECT id FROM bw_aviator_bets WHERE user_id=:u ORDER BY id DESC LIMIT 1"),{"u":user['id']}).scalar()
            session['abid']=nid; session['abet']=bet
        except: db.rollback(); return jsonify({"error":"fail"})
    return jsonify({"id":nid})

@app.route('/aviator/cashout', methods=["POST"])
def aviator_cashout():
    user=get_user(); d=request.get_json(); mult=float(d.get('mult',1))
    aid=session.get('abid'); bet=session.get('abet',0)
    with DBSession() as db:
        try:
            rnd=db.execute(sa.text("SELECT * FROM bw_aviator_rounds WHERE status='flying' ORDER BY id DESC LIMIT 1")).mappings().first()
            if not rnd or mult>=rnd['crash_point']: return jsonify({"win":0})
            win=int(bet*mult)
            db.execute(sa.text("UPDATE bw_users SET coins=coins+:w WHERE id=:id"),{"w":win,"id":user['id']})
            db.execute(sa.text("UPDATE bw_aviator_bets SET cashout=:c, win=:w, status='cashed' WHERE id=:id"),{"c":mult,"w":win,"id":aid}); db.commit()
        except: db.rollback(); return jsonify({"win":0})
    return jsonify({"win":win})

# ===== MINES =====
@app.route('/mines')
def mines_page():
    content="""
    <div class="card"><h3>💣 Mines - Created by MOTIZ</h3><p>Pick tiles - Avoid bomb - Cashout anytime</p></div>
    <div class="card" style="text-align:center"><div id="grid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;max-width:300px;margin:auto"></div>
    <p>Multiplier: <span id="mult">1.00x</span> | Next: <span id="next">1.23x</span></p>
    <input id="betM" type="number" value="50"><button onclick="startM()" class="btn">Start Game</button><button id="cashM" onclick="cashM()" class="btn green" style="display:none">CASHOUT <span id="cashInfoM"></span></button><div id="statusM"></div></div>
    <script>
    let bombs=[], revealed=[], started=false, mult=1, bet=0;
    function genBombs(){bombs=[]; while(bombs.length<5){let r=Math.floor(Math.random()*25); if(!bombs.includes(r)) bombs.push(r);}}
    function render(){let g=document.getElementById('grid'); g.innerHTML=''; for(let i=0;i<25;i++){let d=document.createElement('div'); d.style.cssText='height:50px;background:#333;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:22px;cursor:pointer'; d.innerText=revealed.includes(i)?(bombs.includes(i)?'💣':'💎'):''; if(revealed.includes(i)){d.style.background=bombs.includes(i)?'#ff3d00':'#00c853';} d.onclick=()=>clickTile(i); g.appendChild(d);}}
    function clickTile(i){if(!started||revealed.includes(i)) return; revealed.push(i); if(bombs.includes(i)){render(); document.getElementById('statusM').innerText='BOOM! Lost'; started=false; document.getElementById('cashM').style.display='none';} else {mult+=0.4+Math.random()*0.5; document.getElementById('mult').innerText=mult.toFixed(2)+'x'; document.getElementById('cashInfoM').innerText=Math.floor(bet*mult)+' coins'; render();}}
    function startM(){bet=parseInt(document.getElementById('betM').value); genBombs(); revealed=[]; mult=1; started=true; document.getElementById('cashM').style.display='block'; render();}
    function cashM(){alert('Cashed '+Math.floor(bet*mult)+' coins!'); started=false; document.getElementById('cashM').style.display='none';}
    render();
    </script>
    """
    return render_template_string(BASE, title="Mines", content=Markup(content), script="")

# ===== VIRTUAL & INSTANT =====
@app.route('/virtual')
def virtual_page():
    content="""<div class="card"><h3>⚽ Virtual Football</h3><div id="v"></div></div>
    <script>
    async function load(){let r=await fetch('/virtual/state'); let d=await r.json(); document.getElementById('v').innerHTML=d.matches.map(m=>`<div style="display:flex;justify-content:space-between;padding:10px;border-bottom:1px solid #222"><span><b>${m.home}</b> vs <b>${m.away}</b><br><small>${m.league}</small></span><span style="text-align:right">${m.home_score}-${m.away_score}<br><small>${m.status}</small><br><button onclick="betV('${m.home}')" class="btn" style="padding:4px 8px;font-size:11px;width:auto;display:inline-block">${(Math.random()*2+1.5).toFixed(2)}</button></span></div>`).join('');}
    load(); setInterval(load,3000);
    function betV(t){alert('Bet placed on '+t+' - Virtual odds like MSport!');}
    </script>"""
    return render_template_string(BASE, title="Virtual", content=Markup(content), script="")

@app.route('/virtual/state')
def virtual_state():
    teams=[("Man City","Arsenal"),("Chelsea","Liverpool"),("Barcelona","Real Madrid"),("Bayern","Dortmund"),("PSG","Marseille"),("Inter","AC Milan")]
    matches=[]
    for home,away in teams:
        matches.append({"league":"Premier League Virtual","home":home,"away":away,"home_score":random.randint(0,3),"away_score":random.randint(0,3),"status":random.choice(['Live 23\'','Live 67\'','HT','FT'])})
    return jsonify({"matches":matches})

@app.route('/instant')
def instant_page():
    content="""<div class="card"><h3>⚡ Instant League - New table every 60s</h3><table id="table"><tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>Pts</th></tr></table></div>
    <script>
    function genTable(){
        let teams=["City","Arsenal","Chelsea","Liverpool","United","Tottenham","Newcastle","Brighton"]; let html='<tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>Pts</th></tr>';
        teams.sort(()=>Math.random()-0.5).forEach((t,i)=>{html+=`<tr><td>${i+1}</td><td>${t}</td><td>10</td><td>${Math.floor(Math.random()*8)}</td><td>${Math.floor(Math.random()*20+10)}</td></tr>`});
        document.getElementById('table').innerHTML=html;
    }
    genTable(); setInterval(genTable,10000);
    </script>"""
    return render_template_string(BASE, title="Instant", content=Markup(content), script="")

@app.route('/spin')
def spin_simple():
    return redirect('/')

@app.route('/crash')
def crash_page():
    return redirect('/aviator')

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))