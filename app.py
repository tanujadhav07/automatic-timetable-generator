from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
import json
import os
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from algorithm import validate_inputs_and_build_maps, generate_timetable

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app, supports_credentials=True)

DATA_FILE = "user_data.json"
USERS_FILE = "users.json"
CONTACT_FILE = "contact_messages.json"

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"classes": [], "teachers": [], "electives": [], "timetables": [], "collegeName": "College Timetable Generator"}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

TIMESLOTS = [
    ("10:00 - 11:00", "lecture"),
    ("11:00 - 12:00", "lecture"),
    ("12:00 - 13:00", "lunch"),
    ("13:00 - 14:00", "lecture"),
    ("14:00 - 15:00", "lecture"),
    ("15:00 - 16:00", "lecture"),
    ("16:00 - 17:00", "lecture"),
]

classes = []
teachers = []
subjects = {}
batches = {}
labs = ["Lab(A)", "Lab(B)", "Lab(C)", "Lab(D)"]
elective_subjects = []

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    users = load_users()
    if username in users:
        return jsonify({"error": "Username already exists"}), 400
    
    users[username] = hash_password(password)
    save_users(users)
    return jsonify({"message": "Registration successful! You can now log in."})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    users = load_users()
    if username not in users or users[username] != hash_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
    
    session["user"] = username
    return jsonify({"message": f"Welcome back, {username}!", "username": username})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"})

@app.route("/api/me")
def get_me():
    if "user" in session:
        return jsonify({"username": session["user"]})
    return jsonify({"username": None})

# API routes MUST come before catch-all static route
@app.route("/api/bulk-add", methods=["POST"])
def bulk_add():
    data = request.get_json()
    bulk_classes = json.loads(data.get("bulkClasses", "[]"))
    bulk_teachers = json.loads(data.get("bulkTeachers", "[]"))
    
    classes = []
    for c in bulk_classes:
        classes.append({
            "name": c["name"],
            "batches": c.get("batches", []),
            "lectures": c.get("lectures", []),
            "practicals": c.get("practicals", [])
        })
    
    teachers = []
    for t in bulk_teachers:
        teachers.append({
            "name": t["name"],
            "fullName": t.get("fullName", t["name"]),
            "subjects": t.get("subjects", [])
        })
    
    current_data = load_data()
    current_data["classes" ] = classes
    current_data["teachers"] = teachers
    save_data(current_data)
    
    return jsonify({"message": f"Successfully imported {len(classes)} classes and {len(teachers)} teachers"})

@app.route("/api/timetable")
def api_timetable():
    include_project = request.args.get("project") == "true"
    data = load_data()
    classes = [c["name"] for c in data["classes"]]
    teachers = data["teachers"]
    
    # subjects mapping: class → {lectures: [], practicals: []}
    subjects = {}
    for cls_obj in data["classes"]:
        name = cls_obj["name"]
        subjects[name] = {
            "lectures": cls_obj.get("lectures", []),
            "practicals": cls_obj.get("practicals", [])
        }
    
    # batches mapping: class → [B1, B2, ...]
    batches = {}
    for cls_obj in data["classes"]:
        batches[cls_obj["name"]] = cls_obj.get("batches", [])
    
    # labs list
    labs = []
    for t in teachers:
        for s in t.get("subjects", []):
            if "lab" in s.lower() or "practical" in s.lower():
                labs.append(f"{s} Lab")
    labs = list(set(labs))
    if not labs: labs = ["Lab A", "Lab B", "Lab C"]
    
    # Map building
    maps, err = validate_inputs_and_build_maps(classes, teachers, data.get("electives", []))
    if err:
        return jsonify({"error": err}), 400
    
    timetable = generate_timetable(classes, teachers, subjects, TIMESLOTS, batches, labs, maps, include_project=include_project)
    
    return jsonify({
        "timetable": timetable,
        "teachers": teachers,
        "collegeName": data.get("collegeName", "College Timetable Generator")
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()
    name = data.get("name", "")
    email = data.get("email", "")
    subject = data.get("subject", "")
    message = data.get("message", "")
    
    if not name or not email or not message:
        return jsonify({"error": "Name, email and message are required"}), 400
    
    # Save to file
    contacts = []
    if os.path.exists(CONTACT_FILE):
        with open(CONTACT_FILE, 'r') as f:
            contacts = json.load(f)
    
    contacts.append({
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    
    with open(CONTACT_FILE, 'w') as f:
        json.dump(contacts, f, indent=2)
    
    # Try to send email if configured
    if EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECEIVER:
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECEIVER
            msg['Subject'] = f"Contact Form: {subject}"
            
            body = f"""
Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            return jsonify({"message": "Message sent successfully!"})
        except Exception as e:
            return jsonify({"message": "Message saved but email failed", "error": str(e)})
    
    return jsonify({"message": "Message received! We'll get back to you soon."})

# Email config - set via environment variables or change here
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', '')  # your Gmail
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')  # Gmail App Password
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', '')  # where to receive messages

# Serve static files from frontend folder
@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # API routes should be handled before this
    if path.startswith('api/'):
        return jsonify({"error": "Not found"}), 404
    try:
        return send_from_directory('frontend', path)
    except:
        # For SPA routing, return index.html for non-file routes
        return send_from_directory('frontend', 'index.html')

if __name__ == "__main__":
    app.run(debug=False, port=5000)
