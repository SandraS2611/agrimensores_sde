# Estudio Agrimensor - Sistema de Gestión de Memorias

Proyecto desarrollado en **Django** para la gestión de planos, procesamiento automático de PDFs y generación de memorias descriptivas en formato Word/PDF.  
Incluye autenticación personalizada, panel de administración ofuscado y API REST para integración externa.

---

## 🚀 Características principales
- **Login personalizado** con diseño futurista (Orbitron / JetBrains Mono).
- **Panel protegido** con rutas ofuscadas mediante tokens dinámicos.
- **Carga de planos PDF** con validaciones de tamaño y formato.
- **Procesamiento automático** de PDFs:
  - Extracción de texto y datos.
  - Generación de memoria descriptiva en Word.
  - Conversión automática a PDF.
- **Gestión de estados**: pendiente, procesando, completado, error.
- **Acciones rápidas**:
  - Descargar memoria en Word/PDF.
  - Reprocesar planos.
  - Subir memoria a Google Drive (placeholder).
  - Eliminar planos.
- **API REST** con Django REST Framework para clientes externos.

---

## 🛠️ Tecnologías utilizadas
- **Backend**: Django 6.0, Django REST Framework
- **Frontend**: HTML5, CSS3, Lucide Icons
- **Base de datos**: PostgreSQL (Render)
- **Procesamiento de documentos**:
  - `python-docx`
  - `docx2pdf`
- **Servidor de producción**: Gunicorn + Whitenoise
- **Despliegue**: Render.com

---

## ⚙️ Instalación local

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tuusuario/agrimensores_sde.git
   cd agrimensores_sde

Crear entorno virtual:

bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
Instalar dependencias:

bash
pip install -r requirements.txt
Migrar base de datos:

bash
python manage.py migrate
Crear superusuario:

bash
python manage.py createsuperuser
Ejecutar servidor:

bash
python manage.py runserver
📦 Despliegue en Render
Crear un nuevo servicio web en Render.

Configurar:

Build Command:

bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
Start Command:

bash
gunicorn agrimensores_project.wsgi
Variables de entorno:

SECRET_KEY → clave secreta de Django.

DATABASE_URL → URL de PostgreSQL proporcionada por Render.

DEBUG → False.

📂 Estructura del proyecto
Código
agrimensores_sde/
│
├── agrimensores_project/   # Configuración principal de Django
├── planos/                 # App principal (vistas, modelos, urls)
│   ├── templates/          # Templates HTML
│   ├── static/             # Archivos CSS/JS
│   └── utils/              # Procesadores PDF/Docx
│
├── requirements.txt
├── Procfile
└── README.md

👩‍💻 Autores
Sandra Soledad Sánchez – Arquitectura, desarrollo y documentación técnica.

Equipo de soporte técnico y colaboradores: Yenina Barrera

📜 Licencia
Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente.

C:\ngrok\ngrok.exe config add-authtoken TU_AUTHTOKEN

python manage.py runserver 8000

C:\ngrok\ngrok.exe http 8000

