#!/usr/bin/env python3
"""
Script de build para Vercel
Compila Tailwind CSS antes del deploy
"""

import subprocess
import sys
import os

def build_css():
    """Compila Tailwind CSS"""
    print("🎨 Compilando Tailwind CSS...")
    
    # Verificar si Node.js está disponible
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js no encontrado. Instalando dependencias...")
        try:
            subprocess.run(['npm', 'install'], check=True)
        except subprocess.CalledProcessError:
            print("❌ Error instalando dependencias de Node.js")
            return False
    
    try:
        # Compilar CSS
        result = subprocess.run([
            'npx', '@tailwindcss/cli', 
            '-i', './static/css/src/input.css', 
            '-o', './static/css/dist/output.css'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Tailwind CSS compilado exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error compilando CSS: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Comando no encontrado: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando build para Vercel...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ No se encontró app.py. Asegúrate de estar en el directorio correcto.")
        sys.exit(1)
    
    # Compilar CSS
    if not build_css():
        print("❌ Build falló")
        sys.exit(1)
    
    print("✅ Build completado exitosamente")

if __name__ == '__main__':
    main()
