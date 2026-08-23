from flask import Flask, render_template_string, request, redirect
from markupsafe import Markup
from datetime import date, datetime, timedelta
import random, json, os
from functools import wraps

app = Flask(__name__)
DB_FILE = "/tmp/database.json" if os.environ.get('RENDER') else "database.json" # RENDER FIX

PALMPAY_ACCOUNT = "8908025244"
PALMPAY_NAME = "HAMZAT KOLADE AJIMOTI"
LESSON_PRICE = 1000
QUESTION_PRICE = 500
ADMIN_PASS = "24434" # Default password. Can be changed in admin
FREE_Q = 30
PAID_Q = 70

# ===== DATABASE =====
USER_DATA = {}
PAYMENT_REQUESTS = []
FRIEND_REQUESTS = []
POSTS = []
DMS = {}
GROUP_CHAT = []
LESSONS = []
ADS = ["Ad: Join MOTIZ WhatsApp Group!", "Ad: Get Past Questions"]
NOTICES = ["Welcome to MOTIZ E-LEARNING!", "Pay 500 for 70 Questions"]

def load_db():
    global USER_DATA, PAYMENT_REQUESTS, FRIEND_REQUESTS, POSTS, DMS, GROUP_CHAT, LESSONS, ADS, NOTICES, ADMIN_PASS
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: db = json.load(f)
            USER_DATA.update(db.get("users", {}))
            PAYMENT_REQUESTS[:] = db.get("payments", [])
            FRIEND_REQUESTS[:] = db.get("friend_requests", [])
            POSTS[:] = db.get("posts", [])
            DMS.update(db.get("dms", {}))
            GROUP_CHAT[:] = db.get("group_chat", [])
            LESSONS[:] = db.get("lessons", [])
            ADS[:] = db.get("ads", ADS)
            NOTICES[:] = db.get("notices", NOTICES)
            ADMIN_PASS = db.get("admin_pass", ADMIN_PASS) # Load admin pass
            print("Database Loaded Successfully")
        except Exception as e: print(f"DB Load Error: {e}")

def save_db():
    try:
        db = {"users": USER_DATA, "payments": PAYMENT_REQUESTS, "friend_requests": FRIEND_REQUESTS,
              "posts": POSTS, "dms": DMS, "group_chat": GROUP_CHAT, "lessons": LESSONS, "ads": ADS, "notices": NOTICES, "admin_pass": ADMIN_PASS}
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=2)
        print("Database Saved")
    except Exception as e: print(f"DB Save Error: {e}")

load_db()

CLASSES = ["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"]
SUBJECTS = {
    "JSS1": ["Mathematics", "English Language", "Basic Science", "Social Studies"],
    "JSS2": ["Mathematics", "English Language", "Basic Science", "Social Studies"],
    "JSS3": ["Mathematics", "English Language", "Basic Science", "Social Studies"],
    "SS1_Science": ["Mathematics", "English", "Physics", "Chemistry", "Biology"],
    "SS1_Commercial": ["Mathematics", "English", "Economics", "Commerce", "Accounting"],
    "SS1_Art": ["Mathematics", "English", "Literature", "Government", "History"],
    "SS2_Science": ["Mathematics", "English", "Physics", "Chemistry", "Biology"],
    "SS2_Commercial": ["Mathematics", "English", "Economics", "Commerce", "Accounting"],
    "SS2_Art": ["Mathematics", "English", "Literature", "Government", "History"],
    "SS3_Science": ["Mathematics", "English", "Physics", "Chemistry", "Biology"],
    "SS3_Commercial": ["Mathematics", "English", "Economics", "Commerce", "Accounting"],
    "SS3_Art": ["Mathematics", "English", "Literature", "Government", "History"]
}

PRACTICE_MAP = {"JSS1": "JSS2", "JSS2": "JSS3", "JSS3": "JSS3_BECE", "SS1": "SS2", "SS2": "SS3", "SS3": "SS3_WAEC"}
EMOJIS = ["😀","😂","😍","🥰","😘","😎","🤩","😊","😇","🙂","😉","😋","😛","😜","🤪","😝","🤑","🤗","🤔","🤭","🤫","🤐","😴","😪","😮‍💨","😤","😡","🤬","😈","👿","💀","☠️","👻","👽","🤖","🎃","😺","😸","😹","😻","😼","😽","🙀","😿","😾","👍","👎","❤️","🔥","💯"]

QUESTION_BANK = {
    "SS3_WAEC_Science_Mathematics": [{"q": f"WAEC: If x + {i} = 10, find x", "options": [str(10-i), str(10-i+1), str(10-i+2), str(10-i+3)], "ans": str(10-i), "exp": f"x = 10-{i}"} for i in range(1, 31)],
    "SS3_WAEC_Science_Physics": [{"q": f"WAEC Physics Q{i}: S.I Unit of Power?", "options": ["Joule","Watt","Newton","Volt"], "ans": "Watt", "exp": "Power = Work/Time"} for i in range(1, 31)],
    "SS3_WAEC_Science_Chemistry": [{"q": f"WAEC Chemistry Q{i}: Chemical formula of Water?", "options": ["H2O","CO2","NaCl","O2"], "ans": "H2O", "exp": "H2O = Water"} for i in range(1, 31)],
    "SS3_WAEC_Science_Biology": [{"q": f"WAEC Biology Q{i}: Power house of cell?", "options": ["Nucleus","Mitochondria","Ribosome","Cell Wall"], "ans": "Mitochondria", "exp": "Produces ATP"} for i in range(1, 31)],
    "SS3_WAEC_Science_English": [{"q": f"WAEC English Q{i}: Synonym of 'Big'?", "options": ["Small","Large","Tiny","Short"], "ans": "Large", "exp": "Large means Big"} for i in range(1, 31)],
    "JSS3_BECE_Mathematics": [{"q": f"BECE Math Q{i}: 5 + {i} =?", "options": [str(5+i), str(5+i+1), str(5+i+2), str(5+i+3)], "ans": str(5+i), "exp": "Simple Addition"} for i in range(1, 31)],
    "JSS3_BECE_English Language": [{"q": f"BECE English Q{i}: Plural of 'Child'?", "options": ["Childs","Children","Childrens","Child"], "ans": "Children", "exp": "Irregular plural"} for i in range(1, 31)],
}
QUESTIONS = {}
for cls in CLASSES:
    for dept in ["", "_Science", "_Commercial", "_Art"]:
        key_base = f"{cls}{dept}"
        subs = SUBJECTS.get(key_base, [])
        if not subs: continue
        practice_level = PRACTICE_MAP.get(cls, cls)
        for sub in subs:
            if practice_level == "SS3": q_key = f"SS3_WAEC{dept}_{sub}"
            elif practice_level == "JSS3_BECE": q_key = f"JSS3_BECE_{sub}"
            else: q_key = f"{practice_level}{dept}_{sub}"
            final_key = f"{key_base}_{sub}"
            QUESTIONS[final_key] = QUESTION_BANK.get(q_key, [{"q":f"{sub} Q{i}: Sample Question", "options":["A","B","C","D"],"ans":"A","exp":"This is a sample explanation"} for i in range(1, 71)])

def get_user():
    username = request.cookies.get("username")
    return username, USER_DATA.get(username)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        username, user = get_user()
        if not user: return redirect("/login")
        return f(username, user, *args, **kwargs)
    return wrapper

def check_lesson_access(user):
    if not user.get('lesson_expiry'): return False
    try:
        expiry_date = datetime.strptime(user['lesson_expiry'], '%Y-%m-%d').date()
        return date.today() <= expiry_date
    except: return False

SPLASH = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Welcome</title><meta http-equiv="refresh" content="3;url=/login">
<style>body{margin:0;background:linear-gradient(135deg,#0f3460,#16213e);color:white;font-family:Segoe UI;display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column;text-align:center}
.logo{font-size:2.8rem;font-weight:bold;animation:glow 2s ease-in-out infinite alternate}
@keyframes glow{from{text-shadow:0 0 10px #fff}to{text-shadow:0 0 30px #2196f3}}
.loader{border:4px solid #fff3;border-top:4px solid white;border-radius:50%;width:40px;height:40px;animation:spin 1s linear infinite;margin-top:20px}
@keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}</style>
</head><body><div class="logo">MOTIZ E-LEARNING</div><div>Learn. Practice. Excel.</div><div class="loader"></div></body></html>"""

BASE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{title}}</title><style>:root{--bg:#f0f2f5;--card:white;--text:#333} body.dark{--bg:#121212;--card:#1e1e1e;--text:#eee}
body{font-family:Segoe UI;background:var(--bg);color:var(--text);margin:0;padding:0;padding-bottom:80px}
.header{background:#0f3460;color:white;padding:10px;text-align:center;position:fixed;top:0;width:100%;z-index:1000}
.nav{display:flex;gap:5px;background:#16213e;padding:5px;flex-wrap:wrap;position:fixed;top:50px;width:100%;overflow-x:auto;z-index:999}
.nav a{color:white;text-decoration:none;padding:5px 8px;border-radius:10px;border:1px solid #fff3;font-size:0.8rem}
.container{padding:10px;padding-top:95px}
.card{background:var(--card);padding:12px;margin:8px 0;border-radius:10px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.btn{background:#28a745;color:white;padding:12px 15px;text-decoration:none;border-radius:8px;display:block;margin:8px 0;text-align:center;font-weight:bold;border:none;width:100%;cursor:pointer}
.btn.red{background:#e94560}.btn.blue{background:#2196f3}.btn.orange{background:#ff9800}
.locked{background:#fff3cd;border-left:5px solid #ff9800;padding:15px;border-radius:8px;margin:10px 0}
input,select,textarea{width:100%;padding:10px;margin:5px 0;border-radius:5px;border:1px solid #ccc;box-sizing:border-box;font-size:1rem}
.correct{background:#d4edda;border-left:5px solid #28a745}.wrong{background:#f8d7da;border-left:5px solid #e94560}
.emoji-btn{font-size:1.5rem;padding:5px;border:none;background:transparent;cursor:pointer}
.post{border-bottom:1px solid #ccc;padding:10px 0}.error{color:red;background:#f8d7da;padding:10px;border-radius:5px}.success{color:green;background:#d4edda;padding:10px;border-radius:5px}
.timer{background:#e94560;color:white;padding:12px;text-align:center;border-radius:8px;font-weight:bold;font-size:1.3rem;position:sticky;top:95px;z-index:999}</style>
</head><body>{{header}}<div class="container">{{content}}</div><script>{{timer_script}}</script></body></html>"""

def get_header(username,user):
    if not user: return ""
    return f"""<div class="header"><h1 style="margin:0;font-size:1.2rem">MOTIZ <button onclick="document.body.classList.toggle('dark')" style="float:right;border:none;background:transparent;color:white">🌙</button></h1></div>
<div class="nav"><a href="/main">🏠 Home</a><a href="/exam">✍️ CBT</a><a href="/lessons">🎓 Lessons</a><a href="/community">🌍 Community</a><a href="/friends">👥 Friends</a><a href="/profile">👤 Profile</a><a href="/admin">🔒 Admin</a><a href="/logout">🚪 Logout</a></div>"""

@app.route('/')
def splash(): return render_template_string(SPLASH)

@app.route('/main')
@login_required
def main(username, user):
    header = get_header(username,user)
    practice = PRACTICE_MAP.get(user['class'], user['class'])
    ads = "".join([f"<div style='background:#fff3cd;padding:10px;margin:8px 0;border-radius:8px'><b>📢 AD:</b> {a}</div>" for a in ADS])
    notices = "".join([f"<div class='card'><b>📢</b> {n}</div>" for n in NOTICES])
    content = f"<div class='card'><h2>Welcome {user['name']}</h2><p><b>Username:</b> {username}</p><p><b>Class:</b> {user['class']} {user.get('dept','')}</p><p><b>Practicing:</b> {practice} Level</p></div>{ads}<h3>Admin Notice</h3>{notices}<a class=btn href=/exam>Start CBT Exam</a>"
    return render_template_string(BASE, title="Home", header=Markup(header), content=Markup(content), timer_script="")

@app.route('/register', methods=["GET","POST"])
def register():
    if get_user()[1]: return redirect("/main")
    error = ""; success = ""
    if request.method == "POST":
        username = request.form.get("username","").strip().lower()
        surname = request.form.get("surname","").strip()
        other = request.form.get("other","").strip()
        pwd = request.form.get("password","")
        cls = request.form.get("class","")
        dept = request.form.get("dept","")

        if not username or not surname or not other or not pwd or not cls:
            error = "<div class=error>Please fill all required fields</div>"
        elif username in USER_DATA:
            error = "<div class=error>Username already taken. Choose another one</div>"
        elif cls.startswith("SS") and not dept:
            error = "<div class=error>Please select Department for SS classes</div>"
        else:
            USER_DATA[username] = {"name": f"{surname} {other}", "password": pwd, "class": cls, "dept": dept, "q_cycle": "free", "q_used": 0, "lesson_expiry": None, "friends": [], "correct":0, "wrong":0}
            save_db()
            success = f"<div class=success>✅ Registration Successful! You can now login</div>"
            resp = render_template_string(BASE, title="Success", header="", content=Markup(f"<div class='card'><h2>Registration Complete</h2>{success}<a class=btn href=/login>Login Now</a></div>"), timer_script="")
            resp.set_cookie("username", username)
            return resp
    js = """<script>function d(){let c=document.getElementById('class').value;let x=document.getElementById('dept');x.innerHTML='';if(['SS1','SS2','SS3'].includes(c)){x.innerHTML='<label>Department *</label><select name=dept required><option value="">Select</option><option>Science</option><option>Commercial</option><option>Art</option></select>'}}</script>"""
    form = f"<div class='card'><h2>Register</h2>{error}{success}<form method=POST><input name=username placeholder='Choose Username' required><input name=surname placeholder='Surname' required><input name=other placeholder='Other Name' required><input type=password name=password placeholder='Password/Passcode' required><select name=class id=class onchange=d() required><option value=''>Select Class *</option>{''.join([f'<option>{c}</option>' for c in CLASSES])}</select><div id=dept></div><button class=btn>Register</button></form></div>{js}"
    return render_template_string(BASE, title="Register", header="", content=Markup(form), timer_script="")

@app.route('/login', methods=["GET","POST"])
def login():
    if get_user()[1]: return redirect("/main")
    error = ""
    if request.method == "POST":
        username, pwd = request.form["username"].strip().lower(), request.form["password"]
        u = USER_DATA.get(username)
        if u and u["password"] == pwd: resp = redirect("/main"); resp.set_cookie("username", username); return resp
        else: error = "<div class=error>Invalid Username or Password</div>"
    return render_template_string(BASE, title="Login", header="", content=Markup(f"<div class='card'><h2>Login</h2>{error}<form method=POST><input name=username placeholder='Username' required><input type=password name=password placeholder=Password required><button class=btn>Login</button><a class=btn.blue href=/register>Register</a></form></div>"), timer_script="")

@app.route('/exam')
@login_required
def exam(username, user):
    cycle, used = user['q_cycle'], user['q_used']
    limit = FREE_Q if cycle=="free" else PAID_Q
    if cycle == "free" and used >= FREE_Q: return redirect("/request-payment/questions")
    key = f"{user['class']}_{user['dept']}" if user['dept'] else user['class']
    subs = SUBJECTS.get(key, [])
    if not subs: return render_template_string(BASE, title="Error", header=Markup(get_header(username,user)), content=Markup("<div class=error>No subjects found for your class</div>"), timer_script="")
    sub_btns = "".join([f"<a class=btn href=/start/{key}/{s}>{s}</a>" for s in subs])
    return render_template_string(BASE, title="CBT", header=Markup(get_header(username,user)), content=Markup(f"<div class='card'><h2>Select Subject</h2><p>Questions Used: {used}/{limit}</p>{sub_btns}</div>"), timer_script="")

@app.route('/start/<key>/<sub>', methods=["GET","POST"])
@login_required
def start(username, user, key, sub):
    limit = FREE_Q if user['q_cycle']=="free" else PAID_Q
    if user['q_used'] >= limit: return redirect("/result")
    q_list = QUESTIONS.get(key, [])
    if not q_list: return render_template_string(BASE, title="Error", header=Markup(get_header(username,user)), content=Markup("<div class=error>No questions for this subject yet. Contact Admin</div>"), timer_script="")
    q = q_list[user['q_used'] % len(q_list)]

    timer_js = """
    let timeLeft = 600;
    const timerEl = document.createElement('div');
    timerEl.className = 'timer';
    timerEl.id = 'countdown';
    document.querySelector('.container').prepend(timerEl);
    function updateTimer(){
        let m = Math.floor(timeLeft / 60);
        let s = timeLeft % 60;
        s = s < 10? '0' + s : s;
        timerEl.innerHTML = `⏰ TIME LEFT: ${m}:${s}`;
        if(timeLeft <= 60){timerEl.style.background = '#ffc107';timerEl.style.color = 'black';}
        if(timeLeft <= 0){document.querySelector('form').submit();}
        timeLeft--;
    }
    updateTimer(); setInterval(updateTimer, 1000);
    """

    if request.method == "POST":
        user['q_used'] += 1
        ans = request.form.get("answer")
        if ans == q['ans']: user['correct'] += 1; result_html = f"<div class='card correct'><h3>✅ Correct!</h3><p><b>Explanation:</b> {q['exp']}</p></div>"
        else: user['wrong'] += 1; result_html = f"<div class='card wrong'><h3>❌ Wrong!</h3><p><b>Answer:</b> {q['ans']}</p><p><b>Explanation:</b> {q['exp']}</p></div>"
        save_db()
        if user['q_used'] >= limit: return redirect("/result")
        return render_template_string(BASE, title="Result", header=Markup(get_header(username,user)), content=Markup(f"{result_html}<a class=btn href=/exam>Next Question</a>"), timer_script="")

    options_html = "".join([f"<label><input type=radio name=answer value='{opt}' required> {opt}</label><br>" for opt in q['options']])
    content = f"<div class='card'><h2>{sub}</h2><h3>Question {user['q_used']+1}</h3><p>{q['q']}</p><form method=POST id=examForm>{options_html}<button class=btn>Submit</button></form></div>"
    return render_template_string(BASE, title=sub, header=Markup(get_header(username,user)), content=Markup(content), timer_script=Markup(timer_js))

@app.route('/result')
@login_required
def result(username, user):
    total, correct = user['q_used'], user['correct']
    percent = round((correct/total)*100, 1) if total>0 else 0
    user['q_used']=0; user['correct']=0; user['wrong']=0; save_db()
    return render_template_string(BASE, title="Result", header=Markup(get_header(username,user)), content=Markup(f"<div class='card'><h2>🎉 Score: {correct}/{total}</h2><h3>{percent}%</h3><a class=btn href=/exam>Start New</a></div>"), timer_script="")

@app.route('/community', methods=["GET","POST"])
@login_required
def community(username, user):
    if request.method=="POST": POSTS.append({"user":user["name"],"text":request.form["post"],"emoji":request.form.get("emoji","")}); save_db()
    posts_html = "".join([f"<div class=post><b>{p['user']}</b>: {p['text']} {p['emoji']}</div>" for p in POSTS[::-1]])
    emoji_html = "".join([f"<button type=button class=emoji-btn onclick='document.getElementById(\"post\").value+={json.dumps(e)}'>{e}</button>" for e in EMOJIS])
    content = f"<div class=card><h2>Community</h2><form method=POST><textarea name=post id=post placeholder='Whats on your mind?' required></textarea><div>{emoji_html}</div><button class=btn>Post</button></form></div>{posts_html}"
    return render_template_string(BASE, title="Community", header=Markup(get_header(username,user)), content=Markup(content), timer_script="")

@app.route('/friends')
@login_required
def friends(username, user):
    friends_html = "".join([f"<div class=card>{f}</div>" for f in user['friends']]) or "<p>No friends yet</p>"
    return render_template_string(BASE, title="Friends", header=Markup(get_header(username,user)), content=Markup(f"<div class=card><h2>Friends</h2>{friends_html}</div>"), timer_script="")

@app.route('/lessons')
@login_required
def lessons(username, user):
    if not check_lesson_access(user): return redirect("/request-payment/lessons")
    lessons_html = "".join([f"<div class=card><h3>{l['subject']}: {l['topic']}</h3><p>{l['note']}</p></div>" for l in LESSONS]) or "<p>No lessons yet. Admin will add soon.</p>"
    return render_template_string(BASE, title="Lessons", header=Markup(get_header(username,user)), content=Markup(lessons_html), timer_script="")

@app.route('/request-payment/<t>')
@login_required
def req_pay(username, user, t):
    price = QUESTION_PRICE if t=="questions" else LESSON_PRICE
    pending = any(r['username']==username and r['type']==t and r['status']=='Pending' for r in PAYMENT_REQUESTS)
    if pending: return render_template_string(BASE, title="Payment", header=Markup(get_header(username,user)), content=Markup("<div class=locked><h2>⏳ Request Pending</h2><p>Wait for admin to verify</p></div>"), timer_script="")
    return render_template_string(BASE, title="Payment", header=Markup(get_header(username,user)), content=Markup(f"<div class=locked><h2>Unlock ₦{price}</h2><p><b>Account:</b> {PALMPAY_ACCOUNT}<br><b>Name:</b> {PALMPAY_NAME}</p><a class=btn href=/confirm/{t}>I Have Paid</a></div>"), timer_script="")

@app.route('/confirm/<t>')
@login_required
def confirm(username, user, t):
    PAYMENT_REQUESTS.append({"username": username, "name": user["name"], "type": t, "status": "Pending"}); save_db()
    return render_template_string(BASE, title="Sent", header=Markup(get_header(username,user)), content=Markup("<div class='card'><h2>✅ Request Sent</h2><p>Admin will verify soon</p><a class=btn href=/main>Home</a></div>"), timer_script="")

@app.route('/admin', methods=["GET","POST"])
def admin():
    global ADMIN_PASS
    error = ""
    logged_in = request.cookies.get("admin_logged_in") == "true"

    if request.method=="POST":
        if "login_pass" in request.form: # Admin login
            if request.form.get("login_pass")!= ADMIN_PASS: error = "<div class=error>Wrong Admin Password</div>"
            else: resp = redirect("/admin"); resp.set_cookie("admin_logged_in", "true"); return resp
        elif logged_in and "new_admin_pass" in request.form: # Change password
            old = request.form.get("old_pass")
            if old!= ADMIN_PASS: error = "<div class=error>Current Password Incorrect</div>"
            else: ADMIN_PASS = request.form.get("new_admin_pass"); save_db(); error = "<div class=success>Password Changed Successfully</div>"
        elif logged_in:
            if "add_q_sub" in request.form:
                key = f"{request.form['add_q_target']}_{request.form['add_q_sub']}"
                QUESTIONS.setdefault(key, []).append({"q":request.form["add_q"],"options":[request.form["opt1"],request.form["opt2"],request.form["opt3"],request.form["opt4"]],"ans":request.form["add_q_ans"],"exp":request.form["add_q_exp"]})
            if "lesson_sub" in request.form: LESSONS.append({"subject":request.form["lesson_sub"],"topic":request.form["topic"],"note":request.form["note"]})
            save_db(); error = "<div class=success>Data Saved</div>"

    if not logged_in:
        login_form = f"<div class='card'><h2>🔒 Admin Login</h2>{error}<form method=POST><input type=password name=login_pass placeholder='Enter Admin Password' required><button class=btn>Login</button></form></div>"
        return render_template_string(BASE, title="Admin Login", header="", content=Markup(login_form), timer_script="")

    reqs_html = "".join([f"<div class='card'><b>{r['name']}</b> for {r['type']} <a class=btn href=/verify-payment/{i}>Verify</a></div>" for i,r in enumerate(PAYMENT_REQUESTS) if r['status']=="Pending"])
    form = f"<div class='card'><h2>Admin Panel</h2>{error}</div><div class='card'><h2>Pending Payments</h2>{reqs_html or '<p>None</p>'}</div><div class='card'><h2>Change Admin Password</h2><form method=POST><input type=password name=old_pass placeholder='Current Password' required><input type=password name=new_admin_pass placeholder='New Password' required><button class=btn.orange>Change Password</button></form></div><div class='card'><h2>Add Question</h2><form method=POST><input name=add_q_target placeholder='Example: SS3_WAEC_Science' required><input name=add_q_sub placeholder='Example: Mathematics' required><textarea name=add_q placeholder=Question required></textarea><input name=opt1 placeholder='Option A' required><input name=opt2 placeholder='Option B' required><input name=opt3 placeholder='Option C' required><input name=opt4 placeholder='Option D' required><input name=add_q_ans placeholder='Correct Answer' required><input name=add_q_exp placeholder='Explanation' required><button class=btn>Post Question</button></form></div>"
    return render_template_string(BASE, title="Admin", header="", content=Markup(form), timer_script="")

@app.route('/verify-payment/<req_id>')
def verify_payment(req_id):
    if request.cookies.get("admin_logged_in")!= "true": return redirect("/admin")
    req = PAYMENT_REQUESTS[int(req_id)]
    if req["type"] == "questions": USER_DATA[req["username"]]['q_cycle'] = "paid"
    if req["type"] == "lessons": USER_DATA[req["username"]]['lesson_expiry'] = str(date.today() + timedelta(days=30))
    req["status"] = "Verified"; save_db()
    return redirect("/admin")

@app.route('/profile')
@login_required
def profile(username, user):
    return render_template_string(BASE, title="Profile", header=Markup(get_header(username,user)), content=Markup(f"<div class=card><h2>{user['name']}</h2><p><b>Username:</b> {username}</p><p><b>Class:</b> {user['class']} {user.get('dept','')}</p><p><b>Questions Used:</b> {user['q_used']}</p></div>"), timer_script="")

@app.route('/logout')
def logout(): resp = redirect("/login"); resp.set_cookie("username", "", expires=0); resp.set_cookie("admin_logged_in", "", expires=0); return resp

if __name__ == '__main__':
    print("===================================")
    print("Starting MOTIZ Server v4.2 RENDER...")
    print("LOGIN: Username + Password")
    print("ADMIN: Password = 24434")
    print("===================================")
    app.run(host='0.0.0.0', port=5000, debug=False)
