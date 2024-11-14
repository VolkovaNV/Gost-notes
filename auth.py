from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from gost_cipher import encrypt_message, decrypt_message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gost_notes_user:new_password@localhost:5432/gostNotes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
KEY = "secretkey"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = encrypt_message(data['password'], KEY)
    hashed_username = encrypt_message(data['username'], KEY)
    # print(hashed_password, '\n', hashed_username)
    new_user = User(username=hashed_username, password=hashed_password)
    # print(hashed_password, '\n', hashed_username)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully', 'user_id': new_user.id, 'user_name': decrypt_message(new_user.username, KEY)})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    encrypted_input_username = encrypt_message(data['username'], KEY)
    
    user = User.query.filter_by(username=encrypted_input_username).first()

    if not user:
        return jsonify({'message': 'Login failed'})

    encrypted_input_password = encrypt_message(data['password'], KEY)
    if user.password != encrypted_input_password:
        return jsonify({'message': 'Login failed'})
    else:
        return jsonify({'message': 'Logged in successfully', 'user_id': user.id, 'user_name': decrypt_message(user.username, KEY)})



@app.route('/note', methods=['GET'])
def get_notes():
    user_id = request.args.get('id')
    notes = Note.query.filter_by(author=user_id).all()
    return jsonify([{'id': note.id, 'text': decrypt_message(note.text, KEY)} for note in notes])

@app.route('/note', methods=['POST'])
def add_note():
    data = request.get_json()
    user_id = data['user_id']
    note_text = encrypt_message(data['text'], KEY)
    
    new_note = Note(author=user_id, text=note_text)
    db.session.add(new_note)
    db.session.commit()
    
    return jsonify({'message': 'Note added successfully'})


@app.route('/')
def index():
    return render_template('auth.html')

@app.route('/notes')
def login_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

