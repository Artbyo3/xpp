import sqlite3
import random
from datetime import datetime, timedelta
import calendar
import argparse

def clear_all_data():
    """Clear all existing transaction data"""
    import os
    db_path = os.path.join(os.path.dirname(__file__), 'ingresos.db')
    print(f"🔍 Conectando a base de datos: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
    if cursor.fetchone():
        cursor.execute('DELETE FROM transactions')
        print("🗑️ Todos los datos existentes han sido eliminados.")
    else:
        print("ℹ️ La tabla 'transactions' no existe aún, se creará.")
    
    conn.commit()
    conn.close()

def generate_smart_fake_data(months=6, min_daily_income=50, max_daily_income=800, clear_existing=False):
    """Generate smart fake data with realistic patterns"""
    
    if clear_existing:
        clear_all_data()
    
    import os
    db_path = os.path.join(os.path.dirname(__file__), 'ingresos.db')
    print(f"🔍 Conectando a base de datos: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ Tabla creada/verificada correctamente")
    
    # Realistic job descriptions by category
    freelance_work = [
        "Desarrollo web freelance", "Diseño de logo", "Programación Python", 
        "Consultoría IT", "Desarrollo app móvil", "Mantenimiento web",
        "Optimización SEO", "Diseño UX/UI", "Integración API", "Bug fixing"
    ]
    
    sales_work = [
        "Venta producto digital", "Comisión por referido", "Venta curso online",
        "E-commerce dropshipping", "Afiliado Amazon", "Venta template",
        "Licencia software", "Servicio premium", "Consulta paga", "Membresía"
    ]
    
    content_work = [
        "Artículo blog", "Video YouTube", "Podcast sponsorship", 
        "Curso online", "Webinar", "Tutorial premium", "Newsletter",
        "Social media content", "Traducción", "Copywriting"
    ]
    
    tech_services = [
        "Soporte técnico", "Instalación software", "Reparación PC",
        "Backup y recuperación", "Migración datos", "Configuración red",
        "Auditoría seguridad", "Capacitación", "Automatización", "Script custom"
    ]
    all_descriptions = freelance_work + sales_work + content_work + tech_services
    print(f"🚀 Generando {months} meses de datos inteligentes...")
    print(f"💰 Rango diario: ${min_daily_income} - ${max_daily_income}")
    
    # Start from 2025 and go backwards
    current_date = datetime(2025, 12, 31)  # Start from end of 2025
    total_transactions = 0
    total_amount = 0
    
    for month_offset in range(months):
        # Calculate target date by going backwards month by month
        year = 2025
        month = 12 - month_offset
        
        # Handle year rollover
        while month <= 0:
            month += 12
            year -= 1
        
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Realistic working pattern: 20-25 working days per month
        working_days = random.randint(20, min(25, days_in_month - 2))
        
        # Select random working days within the valid range for this month
        available_days = list(range(1, days_in_month + 1))
        work_days = random.sample(available_days, min(working_days, len(available_days)))
        
        month_total = 0
        month_transactions = 0
        
        for day in sorted(work_days):
            # Target daily income
            target_daily = random.uniform(min_daily_income, max_daily_income)
            
            # Number of transactions per day (1-5, weighted towards 1-3)
            num_transactions = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 20, 7, 3])[0]
            
            # Distribute daily income across transactions
            daily_amounts = []
            remaining = target_daily
            
            for i in range(num_transactions):
                if i == num_transactions - 1:
                    # Last transaction gets remaining amount
                    amount = remaining
                else:
                    # Random portion of remaining
                    portion = random.uniform(0.2, 0.7)
                    amount = remaining * portion
                    remaining -= amount
                
                # Round to realistic values
                amount = round(max(10, amount), 2)
                daily_amounts.append(amount)
            
            # Create transactions for this day
            for amount in daily_amounts:
                # Choose description based on amount
                if amount >= 300:
                    description = random.choice(freelance_work + tech_services)
                elif amount >= 100:
                    description = random.choice(sales_work + content_work)
                else:
                    description = random.choice(all_descriptions)
                
                # 15% chance of no description
                if random.random() < 0.15:
                    description = ""
                
                cursor.execute('''
                    INSERT INTO transactions (year, month, day, amount, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (year, month, day, amount, description))
                
                month_total += amount
                month_transactions += 1
                total_transactions += 1
                total_amount += amount
        
        print(f"📅 {calendar.month_name[month]} {year}: {month_transactions} transacciones, ${month_total:.2f}")
    
    # Force commit all changes
    conn.commit()
    print("💾 Guardando datos en la base de datos...")
    
    # Verify data was saved
    cursor.execute('SELECT COUNT(*) FROM transactions')
    saved_count = cursor.fetchone()[0]
    print(f"✅ Verificado: {saved_count} transacciones guardadas en la DB")
    
    conn.close()
    
    print(f"\n✅ ¡Datos inteligentes generados!")
    print(f"📊 Resumen final:")
    print(f"   • Total transacciones: {total_transactions}")
    print(f"   • Ingreso total: ${total_amount:.2f}")
    print(f"   • Promedio mensual: ${total_amount/months:.2f}")
    print(f"   • Promedio por transacción: ${total_amount/total_transactions:.2f}")
    print(f"   • Período: {months} meses")

def quick_test_data():
    """Generate quick test data for immediate testing"""
    print("⚡ Generando datos de prueba rápidos...")
    
    import os
    db_path = os.path.join(os.path.dirname(__file__), 'ingresos.db')
    print(f"🔍 Conectando a base de datos: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    print(f"📅 Agregando datos para {calendar.month_name[month]} {year}")
    
    transactions_added = 0
    
    # Add transactions for current month - last 15 days
    for day_offset in range(15):
        day = max(1, current_date.day - day_offset)
        
        # 1-3 transactions per day
        daily_transactions = random.randint(1, 3)
        for _ in range(daily_transactions):
            amount = round(random.uniform(25, 250), 2)
            descriptions = ["Test work", "Quick job", "Small project", "Consulting", ""]
            description = random.choice(descriptions)
            
            cursor.execute('''
                INSERT INTO transactions (year, month, day, amount, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (year, month, day, amount, description))
            
            transactions_added += 1
    
    conn.commit()
    
    # Verify data was saved
    cursor.execute('SELECT COUNT(*) FROM transactions')
    total_count = cursor.fetchone()[0]
    print(f"✅ {transactions_added} nuevas transacciones agregadas")
    print(f"📊 Total en DB: {total_count} transacciones")
    
    conn.close()
    
    print("✅ Datos de prueba agregados para este mes!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generar datos falsos para Income Tracker')
    parser.add_argument('--months', type=int, default=12, help='Número de meses de datos (default: 12)')
    parser.add_argument('--years', type=int, default=2, help='Número de años hacia atrás desde 2025 (default: 2)')
    parser.add_argument('--min-daily', type=float, default=50, help='Ingreso mínimo diario (default: 50)')
    parser.add_argument('--max-daily', type=float, default=800, help='Ingreso máximo diario (default: 800)')
    parser.add_argument('--clear', action='store_true', help='Limpiar datos existentes primero')
    parser.add_argument('--quick', action='store_true', help='Generar solo datos de prueba rápidos')
    
    args = parser.parse_args()
    
    try:
        if args.quick:
            quick_test_data()
        else:
            # Calculate total months from years
            total_months = args.years * 12 if args.years else args.months
            generate_smart_fake_data(
                months=total_months,
                min_daily_income=args.min_daily,
                max_daily_income=args.max_daily,
                clear_existing=args.clear
            )
        
        print(f"\n🎉 ¡Listo! Reinicia tu aplicación Flask para ver los nuevos datos.")
        print(f"💡 Comandos útiles:")
        print(f"   python advanced_fake_data.py --quick  (datos rápidos)")
        print(f"   python advanced_fake_data.py --years 3 --clear  (3 años nuevos)")
        print(f"   python advanced_fake_data.py --months 18  (18 meses)")
        print(f"   python advanced_fake_data.py --years 2 --min-daily 100 --max-daily 1000  (más dinero)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Asegúrate de que la aplicación Flask no esté ejecutándose.")