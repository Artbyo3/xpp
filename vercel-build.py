#!/usr/bin/env python3
"""
Script de build completo para Vercel
Compila CSS y prepara la aplicación para producción
"""

import subprocess
import sys
import os
import shutil

def install_dependencies():
    """Instala dependencias de Python y Node.js"""
    print("📦 Instalando dependencias...")
    
    # Instalar dependencias de Python
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencias de Python instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias de Python: {e}")
        return False
    
    # Instalar dependencias de Node.js
    try:
        subprocess.run(['npm', 'install'], check=True)
        print("✅ Dependencias de Node.js instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias de Node.js: {e}")
        return False
    
    return True

def build_css():
    """Compila Tailwind CSS"""
    print("🎨 Compilando Tailwind CSS...")
    
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

def create_directories():
    """Crea directorios necesarios"""
    print("📁 Creando directorios necesarios...")
    
    directories = ['templates', 'static', 'static/uploads', 'static/css/dist']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directorio {directory} creado/verificado")

def main():
    """Función principal"""
    print("🚀 Iniciando build completo para Vercel...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ No se encontró app.py. Asegúrate de estar en el directorio correcto.")
        sys.exit(1)
    
    # Crear directorios
    create_directories()
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ Error instalando dependencias")
        sys.exit(1)
    
    # Compilar CSS
    if not build_css():
        print("❌ Error compilando CSS")
        sys.exit(1)
    
    print("✅ Build completado exitosamente")
    print("🎉 Aplicación lista para Vercel")

if __name__ == '__main__':
    main()
