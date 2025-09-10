# Registro de Ingresos Digitales - Aplicación Web

Una aplicación web completa y moderna para llevar el registro detallado de tus ingresos digitales con soporte para múltiples transacciones por día. **Solo versión web** - sin dependencias de escritorio.

## 🚀 Características Principales

- **Dashboard intuitivo** con métricas clave y análisis de ingresos
- **Múltiples transacciones por día** - Registra tantas transacciones como necesites
- **Gestión avanzada de reportes mensuales** con edición individual de transacciones
- **Sistema de impresión optimizado** para reportes mensuales profesionales
- **Base de datos SQLite** con migración automática de datos existentes
- **Interfaz moderna y responsiva** con TailwindCSS y gradientes
- **Navegación intuitiva** entre todas las secciones
- **Análisis estadístico** con promedios diarios, mejores días y tendencias

## 💡 Nuevas Funcionalidades

### Transacciones Múltiples

- Agrega múltiples transacciones en un mismo día
- Cada transacción incluye monto, descripción y timestamp
- Edición y eliminación individual de transacciones
- Cálculos automáticos de totales diarios y mensuales

### Reportes Mejorados

- Vista de tarjetas por día del mes
- Gestión AJAX para operaciones sin recarga de página
- Modal de edición para transacciones existentes
- Totales en tiempo real

### Sistema de Impresión

- Diseño optimizado para impresión en papel
- Reportes profesionales con análisis detallado
- Preservación de colores importantes en la impresión
- Ocultación automática de elementos no necesarios

### Interfaz Moderna

- Diseño con gradientes y efectos hover
- Cards responsivas con mejor jerarquía visual
- Iconos y emojis para mejor UX
- Transiciones suaves y efectos de profundidad

## Instalación

1. **Clona o descarga el proyecto**

2. **Crea un entorno virtual (recomendado):**
```bash
python -m venv venv
```

3. **Activa el entorno virtual:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

5. **Ejecuta la aplicación:**
```bash
python app.py
```

6. **Abre tu navegador en:** http://localhost:5000

## Uso

1. **Dashboard**: Visualiza tus métricas principales y accede a las funciones
2. **Nuevo Reporte**: Selecciona año y mes para crear un nuevo reporte
3. **Ingreso de datos**: Completa los ingresos día por día del mes seleccionado
4. **Ver Reportes**: Consulta el historial completo de todos tus reportes

## Estructura

```
xpp/
├── app.py                    # Aplicación Flask principal
├── advanced_fake_data.py     # Generador de datos de prueba
├── requirements.txt          # Dependencias Python
├── ingresos.db              # Base de datos SQLite (se crea automáticamente)
├── templates/               # Templates HTML
│   ├── base.html
│   ├── dashboard.html
│   ├── nuevo_reporte.html
│   ├── reporte_mensual.html
│   ├── reportes.html
│   ├── imprimir_reporte.html
│   ├── configuraciones.html
│   ├── login.html
│   ├── register.html
│   └── 404.html
└── static/                  # Archivos estáticos
    ├── images/
    │   └── icon.webp
    └── uploads/
```

## Funcionalidades

- ✅ Dashboard con métricas principales
- ✅ Crear reportes mensuales
- ✅ Campos dinámicos según días del mes (28/30/31)
- ✅ Editar reportes existentes
- ✅ Historial completo de reportes
- ✅ Cálculo automático de totales
- ✅ Navegación con teclado
- ✅ Diseño responsivo
