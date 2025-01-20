from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename 
import os
from dotenv import load_dotenv 

load_dotenv()

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Initialize the Flask app
app =Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# Configure the upload folder and allowed file types
app.config['UPLOAD_FOLDER'] = 'static/uploads' 
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

db = SQLAlchemy(app)

class Exercise(db.Model):
    __tablename__ = 'exercise'
    exercise_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    target = db.Column(db.String(50), nullable=False)
    etype = db.Column(db.String(50), nullable=False)
    needs = db.Column(db.String(200), nullable=False)
    reps = db.Column(db.String(100), nullable=False)
    technique = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200), nullable=False)

    def __init__(self, name, target, etype, needs, reps, technique,image_path):
        self.name = name
        self.target = target
        self.etype = etype
        self.needs = needs
        self.reps = reps
        self.technique = technique
        self.image_path = image_path



@app.route('/')
def admin_dashboard():
    # Retrieve all exercises from the database
    exercises = Exercise.query.all()
    return render_template('admin_dashboard.html', exercises=exercises)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()  # Get the search query
    if query:
        # Filter exercises where the name contains the query (case-insensitive)
        filtered_exercises = Exercise.query.filter(Exercise.name.ilike(f"%{query}%")).all()
    else:
        # If no query, return all exercises
        filtered_exercises = Exercise.query.all()
    return render_template('admin_dashboard.html', exercises=filtered_exercises, query=query)

@app.route('/admin_view/<int:id>')
def admin_view(id):
    # Retrieve the exercise details from the database using the provided id
    exercise = Exercise.query.get_or_404(id) 
    return render_template('admin_view.html', exercise=exercise)

@app.route('/add', methods=['GET', 'POST'])
def add_workout():
    if request.method == 'POST':
        
        name = request.form['name']
        etype = request.form['etype']
        target = request.form['target']
        needs = ', '.join(request.form.getlist('equipment_needed[]')) 
        reps = request.form['reps']
        technique = request.form['technique']

        # Handle image file upload.
        file = request.files.get('image')
        if not file or not allowed_file(file.filename):
            return render_template('add.html', message='Image is required and must be of type png, jpg, jpeg.')

        # Save the image
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Check if exercise already exists
        existing_exercise = db.session.query(Exercise).filter(Exercise.name == name).first()
        if existing_exercise:
            existing_data = {
                'name': existing_exercise.name,
                'target': existing_exercise.target,
                'etype': existing_exercise.etype,
                'needs': existing_exercise.needs,
                'reps': existing_exercise.reps,
                'technique': existing_exercise.technique,
                'image_path': existing_exercise.image_path,
            }
            return render_template(
                'success.html',
                status='failed',
                message='Failed to add exercise. Exercise name already exists.',
                details=existing_data
            )

        # Add new exercise to the database with the image path
        data = Exercise(name, target, etype, needs, reps, technique, filepath)
        db.session.add(data)
        db.session.commit()

        new_data = {
            'name': name,
            'target': target,
            'etype': etype,
            'needs': needs,
            'reps': reps,
            'technique': technique,
            'image_path': filepath
        }
        return render_template(
            'success.html',
            status='success',
            message='Exercise has been successfully added.',
            details=new_data
        )
    return render_template('add.html')

@app.route('/success')
def success():
    # Retrieve query parameters
    details = {
        'name': request.args.get('name'),
        'target': request.args.get('target'),
        'etype': request.args.get('etype'),
        'needs': request.args.get('needs'),
        'reps': request.args.get('reps'),
        'technique': request.args.get('technique'),
        'image_path': request.args.get('image_path'),
    }
    return render_template('success.html', details=details)

@app.route('/update_exercise/<int:exercise_id>', methods=['GET', 'POST'])
def update_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)

    if request.method == 'POST':
        name = request.form.get('name')
        etype = request.form.get('etype')
        target = request.form.get('target')
        needs = ', '.join(request.form.getlist('equipment_needed[]')) 
        reps = request.form.get('reps')
        technique = request.form.get('technique')

        file = request.files.get('image')
        filepath = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        # Check if exercise with the new name already exists
        existing_exercise = db.session.query(Exercise).filter(Exercise.name == name).first()
        if existing_exercise and existing_exercise.exercise_id != exercise_id:
            previous_exercise =db.session.query(Exercise).filter(Exercise.exercise_id == exercise_id).first()
            previous_data = {
                'name': previous_exercise.name,
                'target': previous_exercise.target,
                'etype': previous_exercise.etype,
                'needs': previous_exercise.needs,
                'reps': previous_exercise.reps,
                'technique': previous_exercise.technique,
                'image_path': previous_exercise.image_path,
            }
            return render_template(
                'success.html',
                status='failed',
                message='Failed to update exercise. Exercise name already exists with following previous records.',
                details=previous_data
            )

        # Update exercise details
        exercise.name = name
        exercise.etype = etype
        exercise.target = target
        exercise.needs = needs
        exercise.reps = reps
        exercise.technique = technique
        if filepath:
            exercise.image_path = filepath

        db.session.commit()

        new_data = {
            'name': exercise.name,
            'target': exercise.target,
            'etype': exercise.etype,
            'needs': exercise.needs,
            'reps': exercise.reps,
            'technique': exercise.technique,
            'image_path': exercise.image_path
        }
        return render_template(
            'success.html',
            status='success',
            message='Exercise has been successfully updated.',
            details=new_data
        )

    return render_template('update_exercise.html', exercise=exercise)



@app.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    return redirect(url_for('admin_dashboard')) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)






    