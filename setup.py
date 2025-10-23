#!/usr/bin/env python
"""
Script de inicialización para el proyecto MP3 Player
Ejecuta todas las configuraciones necesarias
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    
    try:
        if sys.platform == 'win32':
            result = subprocess.run(command, shell=True, check=True)
        else:
            result = subprocess.run(command.split(), check=True)
        print(f"✅ {description} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        return False


def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")


def check_ffmpeg():
    """Verifica si FFmpeg está instalado"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        print("✅ FFmpeg está instalado")
        return True
    except FileNotFoundError:
        print("⚠️  FFmpeg no está instalado")
        print("   Por favor instálalo desde: https://ffmpeg.org/download.html")
        return False


def main():
    """Función principal de configuración"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          🎵 MP3 PLAYER - SETUP INICIAL 🎵                 ║
    ║                                                           ║
    ║              Mejor que Spotify                            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Verificar Python
    print("\n1️⃣  Verificando Python...")
    check_python_version()
    
    # Verificar FFmpeg
    print("\n2️⃣  Verificando FFmpeg...")
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        print("\n   Continúa con la instalación, pero necesitarás FFmpeg para descargar canciones.")
    
    # Instalar dependencias
    print("\n3️⃣  Instalando dependencias...")
    python_cmd = 'py' if sys.platform == 'win32' else 'python3'
    if not run_command(f"{python_cmd} -m pip install -r requirements.txt", 
                      "Instalación de dependencias"):
        print("❌ Error al instalar dependencias. Intenta manualmente:")
        print(f"   {python_cmd} -m pip install -r requirements.txt")
        sys.exit(1)
    
    # Crear directorios necesarios
    print("\n4️⃣  Creando directorios...")
    directories = ['media/songs', 'staticfiles']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}")
    
    # Migraciones
    print("\n5️⃣  Configurando base de datos...")
    run_command(f"{python_cmd} manage.py makemigrations", 
                "Creando migraciones")
    run_command(f"{python_cmd} manage.py migrate", 
                "Aplicando migraciones")
    
    # Recolectar archivos estáticos
    print("\n6️⃣  Recolectando archivos estáticos...")
    run_command(f"{python_cmd} manage.py collectstatic --noinput", 
                "Archivos estáticos")
    
    # Migrar canciones antiguas
    print("\n7️⃣  Verificando canciones existentes...")
    if os.path.exists('songs') and os.listdir('songs'):
        print("   📁 Se encontraron canciones en la carpeta 'songs'")
        print("   Puedes moverlas manualmente a 'media/songs/' si lo deseas")
    
    # Resumen final
    print(f"""
    
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          ✨ CONFIGURACIÓN COMPLETADA ✨                    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    📋 PRÓXIMOS PASOS:
    
    1. (Opcional) Crear un superusuario para el admin:
       {python_cmd} manage.py createsuperuser
    
    2. Iniciar el servidor de desarrollo:
       {python_cmd} manage.py runserver
    
    3. Abrir en el navegador:
       http://localhost:8000
    
    4. Para acceder al panel de administración:
       http://localhost:8000/admin
    
    ╔═══════════════════════════════════════════════════════════╗
    ║  🎵 ¡Disfruta de tu reproductor de música! 🎵             ║
    ╚═══════════════════════════════════════════════════════════╝
    
    """)
    
    # Preguntar si desea crear superusuario
    response = input("¿Deseas crear un superusuario ahora? (s/n): ")
    if response.lower() in ['s', 'si', 'yes', 'y']:
        run_command(f"{python_cmd} manage.py createsuperuser", 
                   "Creación de superusuario")
    
    print("\n✅ ¡Listo! Ahora ejecuta: python manage.py runserver")


if __name__ == '__main__':
    main()

