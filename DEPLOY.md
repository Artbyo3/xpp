# 🚀 Deploy en Vercel

Esta guía te ayudará a hacer deploy de tu aplicación Flask en Vercel.

## 📋 Requisitos Previos

1. **Cuenta de Vercel** - Regístrate en [vercel.com](https://vercel.com)
2. **Vercel CLI** - Instala con `npm i -g vercel`
3. **Git** - Para versionado del código

## 🛠️ Pasos para Deploy

### 1. Preparar el Proyecto

```bash
# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias de Node.js
npm install

# Compilar CSS
npm run build-css
```

### 2. Deploy con Vercel CLI

```bash
# Inicializar proyecto en Vercel
vercel

# Seguir las instrucciones:
# - ¿Cuál es el nombre de tu proyecto? (presiona Enter para usar el nombre actual)
# - ¿En qué directorio está tu código? (presiona Enter para usar el directorio actual)
# - ¿Quieres sobrescribir la configuración? (presiona Enter para No)
```

### 3. Deploy Automático

Una vez configurado, cada push a tu repositorio de Git hará deploy automáticamente.

## 📁 Estructura para Vercel

```
xpp/
├── api/
│   └── index.py          # Punto de entrada para Vercel
├── static/
│   └── css/
│       └── dist/
│           └── output.css # CSS compilado
├── templates/            # Templates HTML
├── app.py               # Aplicación Flask principal
├── vercel.json          # Configuración de Vercel
├── requirements.txt     # Dependencias Python
├── package.json         # Dependencias Node.js
└── build.py            # Script de build
```

## ⚙️ Configuración

### Variables de Entorno

En el dashboard de Vercel, puedes configurar:

- `FLASK_ENV=production`
- `SECRET_KEY=tu_clave_secreta_aqui` (opcional)

### Base de Datos

La aplicación usa SQLite que se crea automáticamente. Para producción, considera usar:

- **Vercel Postgres** - Base de datos PostgreSQL
- **PlanetScale** - MySQL serverless
- **Supabase** - PostgreSQL con funciones adicionales

## 🔧 Comandos Útiles

```bash
# Deploy manual
vercel --prod

# Ver logs
vercel logs

# Abrir en el navegador
vercel open

# Verificar configuración
vercel inspect
```

## 🐛 Solución de Problemas

### Error: "Module not found"
- Verifica que `requirements.txt` tenga todas las dependencias
- Asegúrate de que `api/index.py` importe correctamente `app.py`

### Error: "CSS not loading"
- Ejecuta `npm run build-css` antes del deploy
- Verifica que `static/css/dist/output.css` existe

### Error: "Database not found"
- La base de datos SQLite se crea automáticamente
- Verifica que la aplicación tenga permisos de escritura

## 📊 Monitoreo

- **Logs**: Disponibles en el dashboard de Vercel
- **Métricas**: CPU, memoria, y requests en tiempo real
- **Alertas**: Configura notificaciones por email

## 🔄 Actualizaciones

Para actualizar la aplicación:

1. Haz cambios en tu código local
2. Compila CSS: `npm run build-css`
3. Commit y push: `git add . && git commit -m "Update" && git push`
4. Vercel hará deploy automáticamente

## 🎉 ¡Listo!

Tu aplicación estará disponible en `https://tu-proyecto.vercel.app`

Para más información, visita la [documentación de Vercel](https://vercel.com/docs).
