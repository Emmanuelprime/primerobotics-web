from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Sample courses data
courses = [
    {
        'id': 1,
        'name': 'Robotics Development and Automation (RDA)',
        'description': 'Learn the fundamentals of robotics, automation, and control systems.',
        'requirements': [
            'Laptop with a minimum of 8Gb of RAM Running Windows 10 or 11',
            'High School Diploma or equivalent (WAEC, NECO, NABTEB)',
            'Basic understanding of Mathematics (algebra, geometry, and trigonometry)'
        ],
        'duration': '6 months',
        'cost': '₦230,000',
        'image': 'rob.png'
    },
    {
        'id': 2,
        'name': 'Artificial Intelligence and Machine Learning (AIML)',
        'description': 'Explore the basics of AI, machine learning, and their applications.',
        'requirements': [
            'Laptop with a minimum of 8Gb of RAM Running Windows 10 or 11',
            'High School Diploma or equivalent (WAEC, NECO, NABTEB)',
            'Basic understanding of Mathematics (algebra, geometry, and trigonometry)'
        ],
        'duration': '6 months',
        'cost': '₦200,000',
        'image': 'ai.jpg'
    },
    {
        'id': 3,
        'name': 'Data Science and Analytics (DSA)',
        'description': 'Master data science techniques and analytical skills for real-world data.',
        'requirements': [
            'Laptop with a minimum of 8Gb of RAM Running Windows 10 or 11',
            'High School Diploma or equivalent (WAEC, NECO, NABTEB)',
            'Basic understanding of Mathematics (algebra, geometry, and trigonometry)'
        ],
        'duration': '6 months',
        'cost': '₦200,000',
        'image': 'data.jpg'
    }
]

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create students table (for course registration)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            surname TEXT NOT NULL,
            other_names TEXT,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            guardian_phone TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            amount_paid REAL NOT NULL
        )
    ''')

    # Create users table (for admin login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL  -- Only admins
        )
    ''')

    conn.commit()
    conn.close()


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses')
def courses_list():
    return render_template('courses.html', courses=courses)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        flash('Thank you for your message! We will get back to you soon.')

        return redirect(url_for('contact')) 

    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = next((course for course in courses if course['id'] == course_id), None)
    return render_template('course_detail.html', course=course)

# Registration route for a specific course (no login required)
@app.route('/register/<int:course_id>', methods=['GET', 'POST'])
def register(course_id):
    course = next((course for course in courses if course['id'] == course_id), None)
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        surname = request.form['surname']
        other_names = request.form.get('other_names', '')  # Default to empty if not provided
        phone = request.form['phone']
        address = request.form['address']
        guardian_phone = request.form['guardian_phone']
        email = request.form['email']
        amount_paid = request.form['amount_paid']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO students (first_name, surname, other_names, phone, address, guardian_phone, email, course, amount_paid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                       (first_name, surname, other_names, phone, address, guardian_phone, email, course['name'], amount_paid))  # Use course name instead of ID
        conn.commit()
        conn.close()
        flash('Registration successful!')
        return render_template('register.html', course=course)

    return render_template('register.html', course=course)


# Admin Signup route
@app.route('/primeroboticsandai/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        # Get current user's session info to verify they are an admin
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('You must be logged in as an admin to create new admin accounts.')
            return redirect(url_for('admin_login'))
        
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = 'admin'  # Fixed role for admin
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)', 
                           (username, email, hashed_password, role))
            conn.commit()
            flash('Admin account created successfully! Please log in.')
            return redirect(url_for('admin_login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.')
            return redirect(url_for('admin_signup'))
        finally:
            conn.close()

    return render_template('admin_signup.html')



# Admin login route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND role = ?', (username, 'admin'))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            flash('Logged in successfully!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.')

    return render_template('admin_login.html')


# Admin dashboard route (can view registered students)
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access. You need to be an admin to access this page.')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        # Handle updating the amount paid
        student_id = request.form['student_id']
        amount_paid = request.form['amount_paid']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET amount_paid = ? WHERE id = ?', (amount_paid, student_id))
        conn.commit()
        conn.close()
        flash('Payment updated successfully.')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', students=students)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
