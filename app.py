import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Absolute Base Directory Path Logic
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ensure static/uploads exists automatically on boot
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    image_file = db.Column(db.String(100), nullable=True)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    tickets = Ticket.query.order_by(Ticket.id.desc()).all()
    return render_template('admin.html', tickets=tickets)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        file = request.files.get('image')

        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

        new_ticket = Ticket(
            title=request.form['title'],
            location=request.form['location'],
            category=request.form['category'],
            description=request.form['description'],
            image_file=filename
        )
        db.session.add(new_ticket)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('submit.html')

@app.route('/update/<int:ticket_id>/<string:status>')
def update_status(ticket_id, status):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = status
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete/<int:ticket_id>')
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.image_file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], ticket.image_file)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(ticket)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)