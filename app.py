import os
import time
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload path and allowed extensions
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ensure uploads folder exists on server start
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    image_file = db.Column(db.String(100), nullable=True)  # Store image filename

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
        filename = None
        
        # Check if an image file was submitted
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Sanitize filename and prepend timestamp to prevent duplicate name overwrites
                clean_name = secure_filename(file.filename)
                filename = f"{int(time.time())}_{clean_name}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

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

@app.route('/update/<int:id>/<string:status>')
def update_status(id, status):
    ticket = Ticket.query.get_or_404(id)
    ticket.status = status
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)