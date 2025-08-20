from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, session, flash, send_from_directory
import sqlite3
import calendar
from datetime import datetime, timedelta
import os
import json
from functools import wraps
import bcrypt
import secrets
import re
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available. Logo upload feature will be disabled.")
import io
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Clave secreta generada aleatoriamente

# Configuración de seguridad
SESSION_TIMEOUT = 3600  # 1 hora en segundos
PASSWORD_MIN_LENGTH = 8
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_LOGO_SIZE = (64, 64)  # Tamaño máximo del logo en píxeles

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_logo(file):
    """Process and optimize logo image"""
    if not PIL_AVAILABLE:
        print("PIL not available - cannot process logo")
        return None
        
    try:
        # Abrir imagen con PIL
        image = Image.open(file)
        
        # Convertir a RGBA si no lo está (para transparencias)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Redimensionar manteniendo aspecto ratio
        image.thumbnail(MAX_LOGO_SIZE, Image.Resampling.LANCZOS)
        
        # Crear imagen cuadrada con fondo transparente
        new_image = Image.new('RGBA', MAX_LOGO_SIZE, (0, 0, 0, 0))
        
        # Centrar la imagen
        x = (MAX_LOGO_SIZE[0] - image.size[0]) // 2
        y = (MAX_LOGO_SIZE[1] - image.size[1]) // 2
        new_image.paste(image, (x, y), image)
        
        # Convertir a base64 para almacenar en base de datos
        buffer = io.BytesIO()
        new_image.save(buffer, format='PNG', optimize=True)
        img_data = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_data}"
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def validate_password(password):
    """Validate password strength"""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"La contraseña debe tener al menos {PASSWORD_MIN_LENGTH} caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe contener al menos un caracter especial"
    
    return True, "Contraseña válida"

def get_user_logo():
    """Get current user's logo data"""
    if 'user_id' not in session:
        return None
    
    conn = get_db_connection()
    try:
        user = conn.execute(
            'SELECT logo_data FROM users WHERE id = ?',
            (session['user_id'],)
        ).fetchone()
        return user['logo_data'] if user and user['logo_data'] else None
    except:
        return None
    finally:
        conn.close()

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        
        # Verificar timeout de sesión
        if 'login_time' in session:
            login_time = datetime.fromisoformat(session['login_time'])
            if datetime.now() - login_time > timedelta(seconds=SESSION_TIMEOUT):
                session.clear()
                flash('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'warning')
                return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

# Make the function available in templates
@app.context_processor
def inject_user_logo():
    return dict(get_user_logo=get_user_logo)

# Database configuration
DATABASE = 'ingresos.db'

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with new structure for multiple transactions and users"""
    conn = get_db_connection()
      # Crear tabla de usuarios
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            logo_filename TEXT,
            logo_data TEXT
        )
    ''')
    
    # New table for individual transactions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
      # Tabla de sesiones activas (opcional, para mayor seguridad)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
      # Check if old table exists and migrate data if necessary
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ingresos'")
    if cursor.fetchone():
        # Skip migration if no users exist - data will be preserved in old table
        user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        if user_count > 0:
            # Get first user for migration (if any users exist)
            first_user = conn.execute('SELECT id FROM users ORDER BY created_at ASC LIMIT 1').fetchone()
            if first_user:
                user_id = first_user[0]
                try:
                    conn.execute('''
                        INSERT INTO transactions (user_id, year, month, day, amount, description, created_at)
                        SELECT ?, año, mes, dia, monto, 'Migrated automatically', fecha_registro
                        FROM ingresos
                        WHERE monto > 0
                    ''', (user_id,))
                    print("Data migrated successfully from 'ingresos' to 'transactions'")
                except sqlite3.Error as e:
                    print(f"Migration error: {e}")
    
    # Check if old 'transacciones' table exists and migrate
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transacciones'")
    if cursor.fetchone():
        user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        if user_count > 0:
            first_user = conn.execute('SELECT id FROM users ORDER BY created_at ASC LIMIT 1').fetchone()
            if first_user:
                user_id = first_user[0]
                try:
                    conn.execute('''
                        INSERT INTO transactions (user_id, year, month, day, amount, description, created_at)
                        SELECT ?, año, mes, dia, monto, descripcion, fecha_registro
                        FROM transacciones
                        WHERE monto > 0
                    ''', (user_id,))
                    print("Data migrated successfully from 'transacciones' to 'transactions'")
                except sqlite3.Error as e:
                    print(f"Migration error: {e}")
    
    conn.commit()
    conn.close()

@app.route('/')
@login_required
def dashboard():
    """Main dashboard with metrics"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get general statistics for this user
    total_income = conn.execute('SELECT SUM(amount) as total FROM transactions WHERE user_id = ?', (user_id,)).fetchone()['total'] or 0
    
    # Current month income
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_month_income = conn.execute(
        'SELECT SUM(amount) as total FROM transactions WHERE user_id = ? AND year = ? AND month = ?',
        (user_id, current_year, current_month)
    ).fetchone()['total'] or 0
    
    # Last 6 months of income for chart
    recent_months = conn.execute('''
        SELECT year, month, SUM(amount) as total
        FROM transactions
        WHERE user_id = ?
        GROUP BY year, month
        ORDER BY year DESC, month DESC
        LIMIT 6
    ''', (user_id,)).fetchall()
    
    # Daily average for current month
    days_elapsed = datetime.now().day
    daily_average = current_month_income / days_elapsed if days_elapsed > 0 else 0
    # Total number of transactions
    total_transactions = conn.execute('SELECT COUNT(*) as total FROM transactions WHERE user_id = ?', (user_id,)).fetchone()['total']
    conn.close()
    
    return render_template('dashboard.html', 
                         total_income=total_income,
                         current_month_income=current_month_income,
                         daily_average=daily_average,
                         recent_months=recent_months,
                         total_transactions=total_transactions,
                         current_year=current_year,
                         current_month=current_month,
                         current_date=datetime.now())

@app.route('/nuevo')
@app.route('/nuevo_reporte')
@app.route('/new-report')
@login_required
def new_report():
    """Page to select year and month for new report"""
    return render_template('nuevo_reporte.html')

@app.route('/reporte/<int:year>/<int:month>')
@app.route('/report/<int:year>/<int:month>')
@login_required
def monthly_report(year, month):
    """Show form to enter data for a specific month"""
    # Validate month
    if month < 1 or month > 12:
        return redirect(url_for('new_report'))
    
    # Get number of days in month
    days_in_month = calendar.monthrange(year, month)[1]
    month_name = calendar.month_name[month]
    
    # Get existing transactions grouped by day for this user
    user_id = session['user_id']
    conn = get_db_connection()
    transactions_by_day = {}
    
    transactions = conn.execute('''
        SELECT day, amount, description, id 
        FROM transactions 
        WHERE user_id = ? AND year = ? AND month = ? 
        ORDER BY day, id
    ''', (user_id, year, month)).fetchall()
    
    for trans in transactions:
        day = trans['day']
        if day not in transactions_by_day:
            transactions_by_day[day] = []
        transactions_by_day[day].append({
            'id': trans['id'],
            'amount': trans['amount'],
            'description': trans['description'] or ''
        })
    
    # Calculate totals by day
    totals_by_day = {}
    total_month = 0
    for day in range(1, days_in_month + 1):
        if day in transactions_by_day:
            totals_by_day[day] = sum(t['amount'] for t in transactions_by_day[day])
            total_month += totals_by_day[day]
        else:
            totals_by_day[day] = 0
    
    # Calculate statistics
    active_days = len([day for day in totals_by_day.values() if day > 0])
    daily_average = total_month / active_days if active_days > 0 else 0
    
    conn.close()
    
    return render_template('reporte_mensual.html',
                         year=year,
                         month=month,
                         month_name=month_name,
                         days_in_month=days_in_month,
                         transactions_by_day=transactions_by_day,
                         totals_by_day=totals_by_day,
                         total_month=total_month,
                         active_days=active_days,
                         daily_average=daily_average,
                         current_time=datetime.now().strftime('%H:%M'))

@app.route('/add-transaction', methods=['POST'])
@login_required
def add_transaction():
    """Add a new transaction"""
    user_id = session['user_id']
    
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    try:
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        amount = float(data.get('amount', 0))
        description = data.get('description', '').strip()
        
        if amount <= 0:
            if request.is_json:
                return jsonify({'success': False, 'message': 'El monto debe ser mayor a 0'})
            else:
                flash('El monto debe ser mayor a 0', 'error')
                return redirect(url_for('monthly_report', year=year, month=month))
        
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO transactions (user_id, year, month, day, amount, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, year, month, day, amount, description))
        
        conn.commit()
        conn.close()
        
        if request.is_json:
            # Return new transaction with its ID for AJAX requests
            new_transaction = {
                'id': cursor.lastrowid,
                'amount': amount,
                'description': description
            }
            return jsonify({'success': True, 'transaction': new_transaction})
        else:
            # Redirect for form submissions
            flash('💰 Ingreso agregado exitosamente', 'success')
            return redirect(url_for('monthly_report', year=year, month=month))
            
    except ValueError as e:
        error_msg = 'Datos inválidos. Verifica los valores ingresados.'
        if request.is_json:
            return jsonify({'success': False, 'message': error_msg})
        else:
            flash(error_msg, 'error')
            return redirect(url_for('new_report'))
    except Exception as e:
        error_msg = f'Error al guardar: {str(e)}'
        if request.is_json:
            return jsonify({'success': False, 'message': error_msg})
        else:
            flash(error_msg, 'error')
            return redirect(url_for('new_report'))

@app.route('/delete-transaction/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Transacción eliminada exitosamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/edit-transaction/<int:transaction_id>', methods=['PUT'])
@login_required
def edit_transaction(transaction_id):
    try:
        data = request.get_json()
        amount = data.get('amount')
        description = data.get('description', '')
        
        if not amount or amount <= 0:
            return jsonify({'success': False, 'message': 'El monto debe ser mayor a 0'})
        
        conn = get_db_connection()
        conn.execute('''
            UPDATE transactions 
            SET amount = ?, description = ?
            WHERE id = ?
        ''', (amount, description, transaction_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Transacción editada exitosamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/reportes')
@app.route('/ver_reportes')
@app.route('/reports')
@login_required
def view_reports():
    """Show all saved reports with pagination"""
    user_id = session['user_id']
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate per_page value
    if per_page not in [10, 25, 50, 100]:
        per_page = 10
    
    conn = get_db_connection()
    
    # Get total count for pagination for this user
    total_count = conn.execute('''
        SELECT COUNT(*) as count
        FROM (
            SELECT year, month
            FROM transactions
            WHERE user_id = ? AND amount > 0
            GROUP BY year, month
        )
    ''', (user_id,)).fetchone()['count']
    
    # Calculate pagination values
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
    offset = (page - 1) * per_page
    
    # Get paginated reports for this user
    reports = conn.execute('''
        SELECT year, month, SUM(amount) as total, COUNT(*) as total_transactions,
               COUNT(DISTINCT day) as dias_registrados
        FROM transactions
        WHERE user_id = ? AND amount > 0
        GROUP BY year, month
        ORDER BY year DESC, month DESC
        LIMIT ? OFFSET ?
    ''', (user_id, per_page, offset)).fetchall()
    conn.close()
    
    # Add month names
    reports_with_names = []
    for report in reports:
        reports_with_names.append({
            'year': report['year'],
            'month': report['month'],
            'month_name': calendar.month_name[report['month']],
            'total': report['total'],
            'total_transactions': report['total_transactions'],
            'dias_registrados': report['dias_registrados']
        })
    
    # Create pagination object
    class Pagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = total_pages
            self.has_prev = page > 1
            self.has_next = page < total_pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
        
        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            """Generate page numbers for pagination display"""
            last = self.pages
            for num in range(1, last + 1):
                if num <= left_edge or \
                   (self.page - left_current - 1 < num < self.page + right_current) or \
                   num > last - right_edge:
                    yield num
    
    pagination = Pagination(page, per_page, total_count, reports_with_names)
    
    return render_template('reportes.html', reports=pagination)

@app.route('/imprimir/<int:year>/<int:month>')
@app.route('/print-report/<int:year>/<int:month>')
@login_required
def print_report(year, month):
    """Generate a print view of the monthly report"""
    user_id = session['user_id']
    
    # Validate month
    if month < 1 or month > 12:
        return redirect(url_for('view_reports'))
    
    days_in_month = calendar.monthrange(year, month)[1]
    month_name = calendar.month_name[month]
    
    conn = get_db_connection()
    
    # Get all transactions with created_at for this user only
    transactions_complete = conn.execute('''
        SELECT day, amount, description, created_at
        FROM transactions 
        WHERE user_id = ? AND year = ? AND month = ? 
        ORDER BY day, id
    ''', (user_id, year, month)).fetchall()
    
    # Organize transactions by day with created_at
    transactions_by_day = {}
    total_month = 0
    total_transactions = 0
    days_with_transactions = 0
    
    for trans in transactions_complete:
        day = trans['day']
        if day not in transactions_by_day:
            transactions_by_day[day] = []
        transactions_by_day[day].append({
            'amount': trans['amount'],
            'description': trans['description'] or 'No description',
            'created_at': datetime.strptime(trans['created_at'], '%Y-%m-%d %H:%M:%S') if trans['created_at'] else datetime.now()
        })
        total_month += trans['amount']
        total_transactions += 1
    
    # Count days with transactions
    days_with_transactions = len(transactions_by_day)
    
    # Calculate daily average
    daily_average = total_month / days_with_transactions if days_with_transactions > 0 else 0
    
    conn.close()
    
    return render_template('imprimir_reporte.html',
                         year=year,
                         month=month,
                         month_name=month_name,
                         days_in_month=days_in_month,
                         transactions_by_day=transactions_by_day,
                         total_month=total_month,
                         total_transactions=total_transactions,
                         days_with_transactions=days_with_transactions,                         daily_average=daily_average,
                         current_date=datetime.now())

@app.route('/configuraciones', methods=['GET', 'POST'])
@login_required
def configuraciones():
    """Handle user configurations including logo upload"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                if not PIL_AVAILABLE:
                    flash('Error: La función de subida de logos no está disponible. Instala la librería Pillow.', 'error')
                elif allowed_file(file.filename):
                    # Process the logo
                    logo_data = process_logo(file)
                    if logo_data:
                        # Save to database
                        conn = get_db_connection()
                        try:
                            filename = secure_filename(file.filename)
                            conn.execute(
                                'UPDATE users SET logo_filename = ?, logo_data = ? WHERE id = ?',
                                (filename, logo_data, user_id)
                            )
                            conn.commit()
                            flash('Logo actualizado exitosamente', 'success')
                        except Exception as e:
                            flash('Error al guardar el logo', 'error')
                        finally:
                            conn.close()
                    else:
                        flash('Error al procesar la imagen', 'error')
                else:
                    flash('Formato de archivo no permitido. Use PNG, JPG, JPEG, GIF o WEBP', 'error')
        
        # Handle logo removal
        if request.form.get('remove_logo'):
            conn = get_db_connection()
            try:
                conn.execute(
                    'UPDATE users SET logo_filename = NULL, logo_data = NULL WHERE id = ?',
                    (user_id,)
                )
                conn.commit()
                flash('Logo eliminado exitosamente', 'success')
            except Exception as e:
                flash('Error al eliminar el logo', 'error')
            finally:
                conn.close()
    
    # Get current user data including logo
    conn = get_db_connection()
    user = conn.execute(
        'SELECT username, email, logo_filename, logo_data FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()
    conn.close()
    
    return render_template('configuraciones.html', user=user, pil_available=PIL_AVAILABLE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with database authentication"""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username, email, password_hash, is_active, failed_login_attempts, locked_until FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        
        if user:
            # Check if user is locked
            if user['locked_until'] and datetime.now() < datetime.fromisoformat(user['locked_until']):
                flash('Cuenta bloqueada por intentos fallidos. Intenta más tarde.', 'error')
                conn.close()
                return render_template('login.html')
            
            # Check if user is active
            if not user['is_active']:
                flash('Cuenta desactivada. Contacta al administrador.', 'error')
                conn.close()
                return render_template('login.html')
            
            # Verify password
            if verify_password(password, user['password_hash']):
                # Successful login
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['login_time'] = datetime.now().isoformat()
                
                # Reset failed attempts and update last login
                conn.execute(
                    'UPDATE users SET failed_login_attempts = 0, locked_until = NULL, last_login = ? WHERE id = ?',
                    (datetime.now(), user['id'])
                )
                conn.commit()
                conn.close()
                
                flash(f'¡Welcome, {user["username"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                # Failed login
                failed_attempts = user['failed_login_attempts'] + 1
                locked_until = None
                
                # Lock account after 5 failed attempts for 15 minutes
                if failed_attempts >= 5:
                    locked_until = (datetime.now() + timedelta(minutes=15)).isoformat()
                    flash('Demasiados intentos fallidos. Cuenta bloqueada por 15 minutos.', 'error')
                else:
                    flash(f'Contraseña incorrecta. Intentos restantes: {5 - failed_attempts}', 'error')
                
                conn.execute(
                    'UPDATE users SET failed_login_attempts = ?, locked_until = ? WHERE id = ?',
                    (failed_attempts, locked_until, user['id'])
                )
                conn.commit()
                conn.close()
        else:
            flash('Usuario no encontrado', 'error')
            conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validations
        if not username or not email or not password:
            flash('Todos los campos son obligatorios', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('register.html')
        
        # Check if user exists
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('El usuario o email ya existe', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        try:
            password_hash = hash_password(password)
            conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            flash('Cuenta creada exitosamente. Ahora puedes iniciar sesión.', 'success')
            conn.close()
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error al crear la cuenta. Intenta nuevamente.', 'error')
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    username = session.get('username', 'Usuario')
    session.clear()
    flash(f'Hasta luego, {username}. Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('404.html'), 500

if __name__ == '__main__':
    # Create directories for templates and static if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Run application
    app.run(debug=True)
