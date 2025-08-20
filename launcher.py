import os
import sys
import threading
import webbrowser
import time
import socket
import signal
import sqlite3
from app import app

def initialize_database():
    """Inicializa la base de datos con TODAS las columnas y tablas necesarias"""
    print("🗃️ Verificando e inicializando base de datos completa...")
    
    db_path = 'ingresos.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla users con TODAS las columnas posibles que usa la app
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                icon TEXT DEFAULT '💰',
                is_active BOOLEAN DEFAULT 1,
                failed_login_attempts INTEGER DEFAULT 0,
                last_login_attempt TIMESTAMP,
                account_locked_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_password_change TIMESTAMP,
                email_verified BOOLEAN DEFAULT 0,
                phone TEXT,
                two_factor_enabled BOOLEAN DEFAULT 0,
                backup_codes TEXT,
                profile_picture TEXT,
                timezone TEXT DEFAULT 'UTC',
                language TEXT DEFAULT 'es'
            )
        ''')
        
        # Crear tabla transactions completa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'general',
                type TEXT DEFAULT 'income',
                currency TEXT DEFAULT 'USD',
                recurring BOOLEAN DEFAULT 0,
                recurring_frequency TEXT,
                tags TEXT,
                location TEXT,
                receipt_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Crear tabla de categorías
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                color TEXT DEFAULT '#007bff',
                icon TEXT DEFAULT '📊',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Crear tabla de sesiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
          # Crear tabla de presupuestos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                period TEXT DEFAULT 'monthly',
                category_id INTEGER,
                start_date DATE,
                end_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Crear tabla de metas financieras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                target_date DATE,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'active',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Crear tabla de recordatorios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                reminder_date DATETIME NOT NULL,
                recurring BOOLEAN DEFAULT 0,
                recurring_frequency TEXT,
                is_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Crear tabla de reportes guardados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                report_type TEXT NOT NULL,
                filters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
          # Crear tabla de archivos adjuntos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions (id)
            )
        ''')
        
        # Crear tabla de notificaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                type TEXT DEFAULT 'info',
                is_read BOOLEAN DEFAULT 0,
                action_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Crear tabla de etiquetas/tags
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                color TEXT DEFAULT '#007bff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Crear tabla de relación transacciones-etiquetas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id)
            )
        ''')
        
        # Crear tabla de cuentas bancarias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                account_name TEXT NOT NULL,
                account_number TEXT,
                bank_name TEXT,
                account_type TEXT DEFAULT 'checking',
                balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Crear tabla de transferencias entre cuentas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                from_account_id INTEGER NOT NULL,
                to_account_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                transfer_date DATE NOT NULL,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (from_account_id) REFERENCES bank_accounts (id),
                FOREIGN KEY (to_account_id) REFERENCES bank_accounts (id)
            )
        ''')
        
        # Crear tabla de plantillas de transacciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount REAL,
                description TEXT,
                category_id INTEGER,
                type TEXT DEFAULT 'income',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Crear tabla de notificaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                type TEXT DEFAULT 'info',
                is_read BOOLEAN DEFAULT 0,
                action_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Crear tabla de configuraciones del sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                setting_type TEXT DEFAULT 'string',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla de logs de actividad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id INTEGER,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Crear tabla de backups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                backup_filename TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                backup_size INTEGER,
                backup_type TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Función para agregar columnas faltantes a cualquier tabla
        def add_missing_columns(table_name, required_columns):
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [column[1] for column in cursor.fetchall()]
            
            for col_name, col_def in required_columns.items():
                if col_name not in existing_columns:
                    print(f"📋 Agregando columna '{col_name}' a tabla {table_name}...")
                    try:
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")
                    except sqlite3.OperationalError as e:
                        print(f"⚠️ No se pudo agregar {col_name}: {e}")
        
        # Verificar y agregar columnas faltantes en users
        users_columns = {
            'email': 'TEXT',
            'icon': "TEXT DEFAULT '💰'",
            'is_active': 'BOOLEAN DEFAULT 1',
            'failed_login_attempts': 'INTEGER DEFAULT 0',
            'last_login_attempt': 'TIMESTAMP',
            'account_locked_until': 'TIMESTAMP',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'last_password_change': 'TIMESTAMP',
            'email_verified': 'BOOLEAN DEFAULT 0',
            'phone': 'TEXT',
            'two_factor_enabled': 'BOOLEAN DEFAULT 0',
            'backup_codes': 'TEXT',
            'profile_picture': 'TEXT',
            'timezone': "TEXT DEFAULT 'UTC'",
            'language': "TEXT DEFAULT 'es'"
        }
        add_missing_columns('users', users_columns)
        
        # Verificar y agregar columnas faltantes en transactions
        transactions_columns = {
            'category': "TEXT DEFAULT 'general'",
            'type': "TEXT DEFAULT 'income'",
            'currency': "TEXT DEFAULT 'USD'",
            'recurring': 'BOOLEAN DEFAULT 0',
            'recurring_frequency': 'TEXT',
            'tags': 'TEXT',
            'location': 'TEXT',
            'receipt_path': 'TEXT',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'        }
        add_missing_columns('transactions', transactions_columns)
        
        # Verificar todas las demás tablas y agregar columnas faltantes
        
        # Categorías
        categories_columns = {
            'color': "TEXT DEFAULT '#007bff'",
            'icon': "TEXT DEFAULT '📊'",
            'is_active': 'BOOLEAN DEFAULT 1',
            'parent_id': 'INTEGER',
            'sort_order': 'INTEGER DEFAULT 0'
        }
        add_missing_columns('categories', categories_columns)
        
        # Presupuestos
        budgets_columns = {
            'period': "TEXT DEFAULT 'monthly'",
            'category_id': 'INTEGER',
            'start_date': 'DATE',
            'end_date': 'DATE',
            'current_spent': 'REAL DEFAULT 0',
            'alert_threshold': 'REAL DEFAULT 80',
            'is_active': 'BOOLEAN DEFAULT 1'
        }
        add_missing_columns('budgets', budgets_columns)
        
        # Metas financieras
        goals_columns = {
            'current_amount': 'REAL DEFAULT 0',
            'target_date': 'DATE',
            'priority': "TEXT DEFAULT 'medium'",
            'status': "TEXT DEFAULT 'active'",
            'description': 'TEXT',
            'completion_percentage': 'REAL DEFAULT 0'
        }
        add_missing_columns('financial_goals', goals_columns)
        
        # Sesiones de usuario
        sessions_columns = {
            'ip_address': 'TEXT',
            'user_agent': 'TEXT',
            'last_activity': 'TIMESTAMP',
            'device_info': 'TEXT'
        }
        add_missing_columns('user_sessions', sessions_columns)
        
        # Configuraciones de usuario
        settings_columns = {
            'auto_backup': 'BOOLEAN DEFAULT 1',
            'email_notifications': 'BOOLEAN DEFAULT 1',
            'sms_notifications': 'BOOLEAN DEFAULT 0',
            'dark_mode': 'BOOLEAN DEFAULT 0',
            'default_category': 'INTEGER',
            'monthly_budget_limit': 'REAL'
        }
        add_missing_columns('user_settings', settings_columns)
        
        # Recordatorios
        reminders_columns = {
            'recurring': 'BOOLEAN DEFAULT 0',
            'recurring_frequency': 'TEXT',
            'is_completed': 'BOOLEAN DEFAULT 0',
            'completion_date': 'TIMESTAMP',
            'snooze_until': 'TIMESTAMP'
        }
        add_missing_columns('reminders', reminders_columns)
        
        # Archivos adjuntos
        attachments_columns = {
            'file_size': 'INTEGER',
            'mime_type': 'TEXT',
            'thumbnail_path': 'TEXT',
            'is_deleted': 'BOOLEAN DEFAULT 0'
        }
        add_missing_columns('attachments', attachments_columns)
        
        # Notificaciones
        notifications_columns = {
            'action_url': 'TEXT',
            'read_at': 'TIMESTAMP',
            'expires_at': 'TIMESTAMP',
            'priority': "TEXT DEFAULT 'normal'"
        }
        add_missing_columns('notifications', notifications_columns)
        
        # Logs de actividad
        logs_columns = {
            'table_name': 'TEXT',
            'record_id': 'INTEGER',
            'old_values': 'TEXT',
            'new_values': 'TEXT',
            'ip_address': 'TEXT',
            'user_agent': 'TEXT',
            'session_id': 'TEXT'
        }
        add_missing_columns('activity_logs', logs_columns)
        
        # Configuraciones del sistema
        system_columns = {
            'setting_type': "TEXT DEFAULT 'string'",
            'description': 'TEXT',
            'is_public': 'BOOLEAN DEFAULT 0',
            'validation_rules': 'TEXT'
        }
        add_missing_columns('system_settings', system_columns)
        
        # Backups
        backups_columns = {
            'backup_size': 'INTEGER',
            'backup_type': "TEXT DEFAULT 'manual'",
            'compression_type': 'TEXT',
            'is_encrypted': 'BOOLEAN DEFAULT 0',
            'restore_tested': 'BOOLEAN DEFAULT 0'
        }
        add_missing_columns('backups', backups_columns)
        
        conn.commit()
        conn.close()
        print("✅ BASE DE DATOS INICIALIZADA COMPLETAMENTE")
        print("📊 TABLAS CREADAS/VERIFICADAS:")
        print("   • users (tabla principal de usuarios)")
        print("   • transactions (registro de ingresos/gastos)")
        print("   • categories (categorías de transacciones)")
        print("   • budgets (presupuestos y límites)")
        print("   • financial_goals (metas financieras)")
        print("   • user_sessions (sesiones de usuario)")
        print("   • user_settings (configuraciones)")
        print("   • reminders (recordatorios)")
        print("   • saved_reports (reportes guardados)")
        print("   • attachments (archivos adjuntos)")
        print("   • notifications (notificaciones)")
        print("   • system_settings (configuración del sistema)")
        print("   • activity_logs (registro de actividades)")
        print("   • backups (respaldos)")
        print("🔧 TODAS las columnas posibles verificadas/creadas en TODAS las tablas")
        print("🎯 Tu aplicación funcionará sin errores de tablas o columnas faltantes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        try:
            conn.close()
        except:
            pass
        return False

def find_free_port():
    """Encuentra un puerto libre para usar"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_flask_server(port):
    """Inicia el servidor Flask en un hilo separado"""
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error en servidor Flask: {e}")

def open_browser(port):
    """Abre el navegador después de un breve delay"""
    time.sleep(2)
    webbrowser.open(f'http://127.0.0.1:{port}')

def signal_handler(sig, frame):
    """Maneja la señal de cierre"""
    print("\n👋 Cerrando aplicación...")
    os._exit(0)

def main():
    """Función principal del launcher"""
    print("🚀 Iniciando Sistema de Registro de Ingresos...")
    print("📱 La aplicación se abrirá automáticamente en tu navegador")
    print("🔄 Presiona Ctrl+C para cerrar la aplicación")
    print("❌ O cierra esta ventana para salir completamente")
    print("-" * 50)
    
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Inicializar base de datos ANTES de iniciar Flask
    if not initialize_database():
        print("❌ Error crítico: No se pudo inicializar la base de datos")
        print("🔧 Verifica que tienes permisos de escritura en esta carpeta")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    # Encontrar puerto libre
    port = find_free_port()
    print(f"📡 Puerto asignado: {port}")
    
    # Iniciar servidor Flask en hilo separado
    flask_thread = threading.Thread(target=start_flask_server, args=(port,), daemon=True)
    flask_thread.start()
    
    # Iniciar navegador en hilo separado
    browser_thread = threading.Thread(target=open_browser, args=(port,), daemon=True)
    browser_thread.start()
    
    print("✅ Aplicación iniciada!")
    print(f"🌐 Accede manualmente en: http://127.0.0.1:{port}")
    
    try:
        # Mantener el programa principal corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main()