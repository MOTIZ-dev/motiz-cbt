from flask import Flask, render_template_string, request, session
from markupsafe import Markup
import random

app = Flask(__name__)
app.secret_key = "motiz_cbt_secret_4637"

CBT_QUESTIONS = {
    "Math": [
        {"q": "What is 25 x 4?", "options": ["80", "100", "120", "90"], "ans": "100"},
        {"q": "Solve: 2x + 5 = 15", "options": ["3", "4", "5", "6"], "ans": "5"},
        {"q": "What is 15% of 200?", "options": ["20", "25", "30", "35"], "ans": "30"},
        {"q": "Factorize: x^2 - 9", "options": ["(x-3)(x+3)", "(x-9)(x+1)", "(x-3)^2", "(x+9)(x-1)"], "ans": "(x-3)(x+3)"},
        {"q": "What is the LCM of 4 and 6?", "options": ["8", "10", "12", "24"], "ans": "12"},
        {"q": "Convert 0.75 to fraction", "options": ["1/2", "2/3", "3/4", "4/5"], "ans": "3/4"},
        {"q": "Area of rectangle 5cm by 8cm?", "options": ["13cm2", "40cm2", "26cm2", "45cm2"], "ans": "40cm2"},
        {"q": "What is 2^3?", "options": ["6", "8", "9", "4"], "ans": "8"},
        {"q": "Mean of 2,4,6,8?", "options": ["4", "5", "6", "7"], "ans": "5"},
        {"q": "Solve: 3y - 7 = 8", "options": ["3", "4", "5", "6"], "ans": "5"}
    ],
    "English": [
        {"q": "Choose correct spelling", "options": ["Accomodate", "Accommodation", "Acommodation", "Acomodation"], "ans": "Accommodation"},
        {"q": "Opposite of Brave", "options": ["Strong", "Coward", "Weak", "Foolish"], "ans": "Coward"},
        {"q": "Which is a noun? The boy ran", "options": ["ran", "quickly", "boy", "the"], "ans": "boy"},
        {"q": "Past tense of Go", "options": ["Goed", "Went", "Gone", "Going"], "ans": "Went"},
        {"q": "Synonym of Happy", "options": ["Sad", "Joyful", "Angry", "Tired"], "ans": "Joyful"},
        {"q": "She ___ to school yesterday", "options": ["go", "goes", "went", "gone"], "ans": "went"},
        {"q": "Figure of speech in The sun smiled", "options": ["Simile", "Metaphor", "Personification", "Alliteration"], "ans": "Personification"},
        {"q": "Plural of Child", "options": ["Childs", "Children", "Childes", "Childrens"], "ans": "Children"},
        {"q": "Which is an adjective?", "options": ["Run", "Beautiful", "Quickly", "And"], "ans": "Beautiful"},
        {"q": "Correct sentence?", "options": ["Me and him went", "Him and I went", "He and I went", "I and he went"], "ans": "He and I went"}
    ],
    "Physics": [
        {"q": "SI unit of Force", "options": ["Joule", "Watt", "Newton", "Pascal"], "ans": "Newton"},
        {"q": "Speed equals", "options": ["Distance/Time", "Time/Distance", "Distance x Time", "Mass x Velocity"], "ans": "Distance/Time"},
        {"q": "Which is NOT vector?", "options": ["Velocity", "Force", "Mass", "Displacement"], "ans": "Mass"},
        {"q": "Unit of Power", "options": ["Newton", "Joule", "Watt", "Volt"], "ans": "Watt"},
        {"q": "Acceleration unit", "options": ["m/s", "m/s2", "kg", "N"], "ans": "m/s2"},
        {"q": "Light travels fastest in?", "options": ["Water", "Glass", "Air", "Vacuum"], "ans": "Vacuum"},
        {"q": "Instrument for current", "options": ["Voltmeter", "Ammeter", "Barometer", "Thermometer"], "ans": "Ammeter"},
        {"q": "Energy in moving object", "options": ["Potential", "Kinetic", "Chemical", "Heat"], "ans": "Kinetic"},
        {"q": "1 Horse Power equals how many Watts", "options": ["746", "640", "1000", "500"], "ans": "746"},
        {"q": "Sound cannot travel through", "options": ["Air", "Water", "Steel", "Vacuum"], "ans": "Vacuum"}
    ],
    "Chemistry": [
        {"q": "Symbol for Sodium", "options": ["Na", "So", "S", "Sn"], "ans": "Na"},
        {"q": "H2O is", "options": ["Salt", "Water", "Oxygen", "CO2"], "ans": "Water"},
        {"q": "Acids turn blue litmus", "options": ["Red", "Green", "Yellow", "No change"], "ans": "Red"},
        {"q": "Atomic number of Oxygen", "options": ["6", "7", "8", "9"], "ans": "8"},
        {"q": "Gas used in fire extinguisher", "options": ["O2", "N2", "CO2", "H2"], "ans": "CO2"},
        {"q": "pH of pure water", "options": ["5", "6", "7", "8"], "ans": "7"},
        {"q": "Example of noble gas", "options": ["O2", "N2", "He", "H2"], "ans": "He"},
        {"q": "Rust is", "options": ["FeO", "Fe2O3", "Fe3O4", "FeS"], "ans": "Fe2O3"},
        {"q": "Valency of Carbon", "options": ["2", "3", "4", "5"], "ans": "4"},
        {"q": "Acid in lemon", "options": ["HCl", "H2SO4", "Citric acid", "Nitric acid"], "ans": "Citric acid"}
    ],
    "Biology": [
        {"q": "Powerhouse of cell", "options": ["Nucleus", "Mitochondria", "Ribosome", "Chloroplast"], "ans": "Mitochondria"},
        {"q": "Human heart chambers", "options": ["2", "3", "4", "5"], "ans": "4"},
        {"q": "Plants make food by", "options": ["Respiration", "Photosynthesis", "Transpiration", "Digestion"], "ans": "Photosynthesis"},
        {"q": "Largest organ in body", "options": ["Liver", "Brain", "Skin", "Heart"], "ans": "Skin"},
        {"q": "Blood cells that fight infection", "options": ["RBC", "WBC", "Platelets", "Plasma"], "ans": "WBC"},
        {"q": "Process of cell division", "options": ["Mitosis", "Osmosis", "Diffusion", "Respiration"], "ans": "Mitosis"},
        {"q": "Green pigment in plants", "options": ["Carotene", "Chlorophyll", "Xanthophyll", "Anthocyanin"], "ans": "Chlorophyll"},
        {"q": "Kidney function", "options": ["Digestion", "Excretion", "Respiration", "Circulation"], "ans": "Excretion"},
        {"q": "DNA stands for", "options": ["Deoxyribonucleic Acid", "Dinitric Acid", "Diethyl Acid", "Deoxy Acid"], "ans": "Deoxyribonucleic Acid"},
        {"q": "Vitamin for healthy bones", "options": ["A", "B", "C", "D"], "ans": "D"}
    ],
    "Geography": [
        {"q": "Capital of Nigeria", "options": ["Lagos", "Abuja", "Kano", "PH"], "ans": "Abuja"},
        {"q": "Largest ocean", "options": ["Atlantic", "Indian", "Arctic", "Pacific"], "ans": "Pacific"},
        {"q": "Instrument for rainfall", "options": ["Thermometer", "Barometer", "Rain gauge", "Hygrometer"], "ans": "Rain gauge"},
        {"q": "Longest river in Africa", "options": ["Niger", "Congo", "Nile", "Zambezi"], "ans": "Nile"},
        {"q": "Desert in Northern Nigeria", "options": ["Kalahari", "Sahara", "Namib", "Gobi"], "ans": "Sahara"},
        {"q": "Earth rotation causes", "options": ["Seasons", "Day and Night", "Tides", "Wind"], "ans": "Day and Night"},
        {"q": "Plateau State is known for", "options": ["Oil", "Tin mining", "Cocoa", "Cotton"], "ans": "Tin mining"},
        {"q": "Equator passes through", "options": ["Asia", "Africa", "Europe", "Antarctica"], "ans": "Africa"},
        {"q": "Map scale 1 to 100000 means", "options": ["1cm=1km", "1cm=10km", "1cm=100km", "1cm=1000km"], "ans": "1cm=1km"},
        {"q": "Harmattan wind comes from", "options": ["Atlantic", "Sahara", "Indian Ocean", "Arctic"], "ans": "Sahara"}
    ],
    "Live stock farming": [
        {"q": "Animal that gives wool", "options": ["Cow", "Sheep", "Goat", "Pig"], "ans": "Sheep"},
        {"q": "Housing for poultry", "options": ["Pen", "Stable", "Piggery", "Poultry house"], "ans": "Poultry house"},
        {"q": "Young cow", "options": ["Calf", "Kid", "Lamb", "Foal"], "ans": "Calf"},
        {"q": "Male pig", "options": ["Boar", "Bull", "Ram", "Stallion"], "ans": "Boar"},
        {"q": "Disease in poultry", "options": ["Foot and mouth", "Newcastle", "Anthrax", "Rabies"], "ans": "Newcastle"},
        {"q": "Feed for cattle", "options": ["Grains", "Fodder", "Pellets", "Mash"], "ans": "Fodder"},
        {"q": "Rabbit meat is called", "options": ["Beef", "Mutton", "Chevon", "Rabbit"], "ans": "Rabbit"},
        {"q": "Best breed for milk", "options": ["Sokoto Gudali", "Friesian", "WAD", "Yankasa"], "ans": "Friesian"},
        {"q": "Incubation period for chicken", "options": ["18 days", "21 days", "28 days", "30 days"], "ans": "21 days"},
        {"q": "Parasite in goats", "options": ["Tick", "Tsetse", "Mosquito", "Fly"], "ans": "Tick"}
    ],
    "Agriculture science": [
        {"q": "Example of legume", "options": ["Maize", "Beans", "Rice", "Yam"], "ans": "Beans"},
        {"q": "Tool for weeding", "options": ["Cutlass", "Hoe", "Spade", "Rake"], "ans": "Hoe"},
        {"q": "Main nutrient in NPK", "options": ["Nitrogen", "Calcium", "Magnesium", "Sulphur"], "ans": "Nitrogen"},
        {"q": "Soil with best drainage", "options": ["Clay", "Loam", "Sandy", "Peat"], "ans": "Sandy"},
        {"q": "Crop pest", "options": ["Earthworm", "Termite", "Bee", "Butterfly"], "ans": "Termite"},
        {"q": "Method of soil conservation", "options": ["Bush burning", "Crop rotation", "Overgrazing", "Deforestation"], "ans": "Crop rotation"},
        {"q": "Cash crop in Nigeria", "options": ["Yam", "Cocoa", "Cassava", "Beans"], "ans": "Cocoa"},
        {"q": "Farm implement for ploughing", "options": ["Sickle", "Plough", "Mattock", "Sprayer"], "ans": "Plough"},
        {"q": "Organic fertilizer", "options": ["NPK", "Urea", "Manure", "SSP"], "ans": "Manure"},
        {"q": "Planting season in Nigeria", "options": ["Dry season", "Rainy season", "Harmattan", "Winter"], "ans": "Rainy season"}
    ],
    "Further math": [
        {"q": "Derivative of x^2", "options": ["x", "2x", "x^2", "2"], "ans": "2x"},
        {"q": "Log10 100", "options": ["1", "2", "10", "100"], "ans": "2"},
        {"q": "Sin 90 degrees", "options": ["0", "0.5", "1", "-1"], "ans": "1"},
        {"q": "Integral of 2x dx", "options": ["x", "x^2", "2x^2", "2"], "ans": "x^2"},
        {"q": "Matrix 1 2 3 4 determinant", "options": ["-2", "2", "10", "0"], "ans": "-2"},
        {"q": "Complex number i squared", "options": ["1", "-1", "0", "i"], "ans": "-1"},
        {"q": "Sum of AP 2,4,6", "options": ["10", "12", "14", "16"], "ans": "12"},
        {"q": "Probability of head in coin", "options": ["0", "0.25", "0.5", "1"], "ans": "0.5"},
        {"q": "nCr formula", "options": ["n!/r!", "n!/r!(n-r)!", "n!/(n-r)!", "n!r!"], "ans": "n!/r!(n-r)!"},
        {"q": "Cos 0 degrees", "options": ["0", "0.5", "1", "-1"], "ans": "1"}
    ],
    "Electrical engineering": [
        {"q": "SI unit of current", "options": ["Volt", "Ohm", "Ampere", "Watt"], "ans": "Ampere"},
        {"q": "Device that stores charge", "options": ["Resistor", "Capacitor", "Inductor", "Diode"], "ans": "Capacitor"},
        {"q": "Ohm's Law: V equals", "options": ["I/R", "IR", "I^2R", "R/I"], "ans": "IR"},
        {"q": "Unit of resistance", "options": ["Volt", "Ampere", "Ohm", "Watt"], "ans": "Ohm"},
        {"q": "AC stands for", "options": ["Alternating Current", "Armature Coil", "Applied Charge", "Ampere Current"], "ans": "Alternating Current"},
        {"q": "Transformer changes", "options": ["Current to Voltage", "Voltage level", "AC to DC", "DC to AC"], "ans": "Voltage level"},
        {"q": "Fuse is for", "options": ["Increase current", "Protection", "Store charge", "Measure voltage"], "ans": "Protection"},
        {"q": "Color code for ground wire", "options": ["Red", "Black", "Green", "Blue"], "ans": "Green"},
        {"q": "Semiconductor material", "options": ["Copper", "Silicon", "Aluminum", "Gold"], "ans": "Silicon"},
        {"q": "Power formula", "options": ["VI", "V/I", "I/V", "V^2/I"], "ans": "VI"}
    ]
}

BASE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{title}}</title><style>
*{box-sizing:border-box}
body{font-family:Segoe UI;background:#0f3460;margin:0;padding:10px;color:white}
.container{max-width:600px;margin:0 auto}
.card{background:white;color:black;padding:15px;margin:10px 0;border-radius:10px}
.btn{background:#28a745;color:white;padding:15px 10px;text-decoration:none;border-radius:10px;display:flex;align-items:center;justify-content:center;margin:8px 0;text-align:center;font-weight:bold;border:none;width:100%;font-size:1rem;min-height:55px;word-break:break-word}
.btn:hover{background:#218838}
.option{background:#f0f2f5;padding:14px;margin:10px 0;border-radius:8px;border:1px solid #ddd;color:black;display:flex;align-items:flex-start;gap:10px}
.option input{margin-top:4px;flex-shrink:0;width:18px;height:18px}
.option span{flex:1;line-height:1.4}
.q-nav{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0;justify-content:center}
.q-nav a{background:#2196f3;color:white;padding:8px 12px;border-radius:5px;text-decoration:none;font-weight:bold}
.timer{background:#e94560;color:white;padding:12px;text-align:center;border-radius:8px;font-weight:bold;font-size:1.1rem}
h2{font-size:1.3rem;text-align:center}
</style></head><body><div class="container">{{content}}</div></body></html>"""

@app.route('/')
def home():
    session.clear() # clear old exam data
    subjects_html = "".join([f"<a class='btn' href=/exam/{s}>📚 {s} - 10 Questions</a>" for s in CBT_QUESTIONS.keys()])
    content = f"<h2>✍️ MOTIZ CBT</h2><div class='card'><p><b>Total: 100 FREE Questions</b></p>{subjects_html}</div>"
    return render_template_string(BASE, title="CBT Home", content=Markup(content))

@app.route('/exam/<subject>', methods=["GET","POST"])
def take_exam(subject):
    if subject not in CBT_QUESTIONS: return redirect("/")

    session_key = f"exam_{subject}"

    if request.method == "GET":
        questions = CBT_QUESTIONS[subject][:]
        random.shuffle(questions)
        session[session_key] = questions # SAVE SHUFFLED ORDER
    else:
        questions = session.get(session_key, CBT_QUESTIONS[subject]) # LOAD SAME ORDER

    if request.method == "POST":
        score = 0
        for i,q in enumerate(questions):
            user_ans = request.form.get(f"q{i}")
            if user_ans and user_ans == q["ans"]: score += 1
        percent = round((score/len(questions))*100,1)
        grade = "A" if percent>=70 else "B" if percent>=60 else "C" if percent>=50 else "F"
        session.pop(session_key, None) # clear after marking
        content = f"<h2>📊 RESULT</h2><div class='card'><h3>{subject}</h3><p><b>Score: {score}/{len(questions)}</b></p><p><b>Percentage: {percent}%</b></p><p><b>Grade: {grade}</b></p><a class='btn' href=/>Back to Subjects</a></div>"
        return render_template_string(BASE, title="Result", content=Markup(content))

    q_html = ""
    q_nav = ""
    for i,q in enumerate(questions):
        options = "".join([f"<label class=option><input type=radio name=q{i} value=\"{opt}\"><span>{opt}</span></label>" for opt in q["options"]])
        q_html += f"<div class=card id=q{i}><p><b>Question {i+1} of {len(questions)}</b></p><p>{q['q']}</p>{options}</div>"
        q_nav += f"<a href=#q{i}>{i+1}</a>"

    content = f"<div class='timer'>⏰ TIME: 10 Minutes</div><div class='q-nav'>{q_nav}</div><form method=POST><h2 style=color:white>{subject}</h2>{q_html}<button class='btn'>Submit Exam</button></form>"
    return render_template_string(BASE, title=subject, content=Markup(content))

if __name__ == '__main__':
    print("===================================")
    print("MOTIZ CBT SERVER STARTED v2.2")
    print("100 FREE QUESTIONS READY")
    print("Open IP:5000 in Chrome")
    print("===================================")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
