# 🔒 GUÍA DE IMPLEMENTACIÓN DE SEGURIDAD
## Sistema Agrimensores SDE

---

## 📋 CHECKLIST DE SEGURIDAD

### ✅ PASO 1: Configurar settings.py

1. Copiar configuraciones de `security_settings.py` a `agrimensores_project/settings.py`
2. Cambiar `DEBUG = False` en producción
3. Configurar `ALLOWED_HOSTS` con dominios/IPs reales
4. Generar nueva SECRET_KEY:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### ✅ PASO 2: Instalar Middleware de Seguridad

1. Copiar `security_middleware.py` a `agrimensores_sde/planos/middleware.py`

2. Agregar a `MIDDLEWARE` en `settings.py`:
   ```python
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'django.contrib.sessions.middleware.SessionMiddleware',
       'django.middleware.common.CommonMiddleware',
       'django.middleware.csrf.CsrfViewMiddleware',
       'django.contrib.auth.middleware.AuthenticationMiddleware',
       'django.contrib.messages.middleware.MessageMiddleware',
       'django.middleware.clickjacking.XFrameOptionsMiddleware',
       
       # Middlewares personalizados
       'planos.middleware.SecurityMiddleware',
       'planos.middleware.FileUploadSecurityMiddleware',
       'planos.middleware.AuditMiddleware',
   ]
   ```

### ✅ PASO 3: Implementar Decoradores

1. Copiar `security_decorators.py` a `agrimensores_sde/planos/decorators.py`

2. Aplicar decoradores a las views en `planos/views.py`:
   ```python
   from .decorators import (
       audit_action,
       rate_limit,
       validate_file_upload,
       require_authenticated
   )
   
   @audit_action(action_type="UPLOAD_PLANO")
   @rate_limit(max_requests=10, time_window=60)
   @validate_file_upload(allowed_extensions=['.pdf'], max_size_mb=10)
   def upload_plano(request):
       # Tu código aquí
       pass
   ```

### ✅ PASO 4: Configurar Variables de Entorno

1. Copiar `.env.security.example` a `.env`
2. Completar TODOS los valores
3. NUNCA commitear `.env` al repositorio
4. Asegurar permisos del archivo:
   ```bash
   chmod 600 .env
   ```

### ✅ PASO 5: Configurar Logging

1. Crear carpeta de logs:
   ```bash
   mkdir logs
   chmod 755 logs
   ```

2. Verificar que el logging esté en `settings.py` (ya está en security_settings.py)

### ✅ PASO 6: Configurar HTTPS (Producción)

1. Obtener certificado SSL (Let's Encrypt recomendado)
2. Configurar nginx/apache con SSL
3. Activar en `settings.py`:
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

### ✅ PASO 7: Configurar Firewall del Servidor

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Denegar todo lo demás
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

### ✅ PASO 8: Hardening de PostgreSQL

1. Editar `/etc/postgresql/XX/main/pg_hba.conf`:
   ```
   # Solo conexiones locales
   local   all             all                                     md5
   host    all             all             127.0.0.1/32            md5
   ```

2. Configurar password fuerte para usuario
3. Limitar privilegios del usuario de la app

### ✅ PASO 9: Configurar Backup Automático

```bash
# Crear script de backup
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/agrimensores"

# Backup de base de datos
pg_dump agrimensores_db > "$BACKUP_DIR/db_$DATE.sql"

# Backup de archivos media
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /ruta/a/media/

# Eliminar backups antiguos (más de 30 días)
find $BACKUP_DIR -type f -mtime +30 -delete
```

Cron job (diario a las 2 AM):
```bash
0 2 * * * /ruta/al/backup.sh
```

### ✅ PASO 10: Monitoreo y Alertas

1. Configurar monitoreo de logs:
   ```bash
   tail -f logs/security.log
   ```

2. Alertas por email para eventos críticos (implementar en middleware)

3. Usar herramientas como:
   - Sentry (errores)
   - Grafana + Prometheus (métricas)
   - Fail2ban (bloqueo de IPs)

---

## 🛡️ MEDIDAS DE SEGURIDAD IMPLEMENTADAS

### 1. AUTENTICACIÓN Y AUTORIZACIÓN
- ✅ Login requerido para acciones críticas
- ✅ Sesiones con timeout (30 minutos)
- ✅ Passwords fuertes (mínimo 12 caracteres)
- ✅ Cookies seguras (HttpOnly, Secure)

### 2. PROTECCIÓN CSRF
- ✅ Tokens CSRF en todos los formularios
- ✅ Validación en cada POST/PUT/DELETE
- ✅ SameSite cookies

### 3. VALIDACIÓN DE ARCHIVOS
- ✅ Solo PDFs permitidos
- ✅ Tamaño máximo 10MB
- ✅ Validación de content-type
- ✅ Sanitización de nombres de archivo

### 4. RATE LIMITING
- ✅ 100 requests/minuto por IP
- ✅ Límites específicos por endpoint
- ✅ Bloqueo temporal en caso de exceso

### 5. LOGGING Y AUDITORÍA
- ✅ Log de todos los accesos
- ✅ Log de acciones críticas
- ✅ Registro de IPs y usuarios
- ✅ Alertas de eventos sospechosos

### 6. HEADERS DE SEGURIDAD
- ✅ X-Frame-Options: DENY
- ✅ X-Content-Type-Options: nosniff
- ✅ Content-Security-Policy
- ✅ HSTS (HTTP Strict Transport Security)
- ✅ Referrer-Policy

### 7. PROTECCIÓN DE DATOS
- ✅ Encriptación de datos sensibles
- ✅ Backups automáticos
- ✅ Separación de entornos (dev/prod)

### 8. RED Y FIREWALL
- ✅ Lista blanca de IPs (opcional)
- ✅ Red interna solo para admin
- ✅ Firewall configurado

---

## 🚨 CHECKLIST FINAL ANTES DE PRODUCCIÓN

```
[ ] DEBUG = False
[ ] SECRET_KEY cambiada
[ ] ALLOWED_HOSTS configurado
[ ] HTTPS activado
[ ] Certificado SSL válido
[ ] Base de datos con password fuerte
[ ] Backups automáticos funcionando
[ ] Logs configurados
[ ] Firewall activo
[ ] Todas las dependencias actualizadas
[ ] Tests de seguridad realizados
[ ] Documentación actualizada
[ ] Plan de respuesta a incidentes definido
```

---

## 📞 CONTACTO EN CASO DE INCIDENTE

- **Admin Sistema**: [email/teléfono]
- **Responsable Seguridad**: [email/teléfono]
- **Soporte Técnico**: [email/teléfono]

---

## 📚 RECURSOS ADICIONALES

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/4.2/topics/security/)
- [Mozilla Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)

---

**IMPORTANTE**: Esta es una configuración robusta de seguridad, pero la seguridad es un proceso continuo. Revisar y actualizar regularmente.