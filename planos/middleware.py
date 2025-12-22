"""
Middleware de seguridad personalizado
"""
import logging
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('django.security')


class SecurityMiddleware:
    """
    Middleware de seguridad personalizado para agrimensores_sde
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Logging de accesos
        self.log_access(request)
        
        # Validar IP si está configurada lista blanca
        if hasattr(settings, 'ALLOWED_IPS'):
            if not self.validate_ip(request):
                logger.warning(f"Acceso denegado desde IP: {self.get_client_ip(request)}")
                return HttpResponseForbidden("Acceso denegado: IP no autorizada")
        
        # Rate limiting básico
        if not self.check_rate_limit(request):
            logger.warning(f"Rate limit excedido para IP: {self.get_client_ip(request)}")
            return HttpResponseForbidden("Demasiadas solicitudes. Intente más tarde.")
        
        response = self.get_response(request)
        
        # Agregar headers de seguridad adicionales
        response = self.add_security_headers(response)
        
        return response
    
    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def validate_ip(self, request):
        """Validar si la IP está en lista blanca"""
        client_ip = self.get_client_ip(request)
        allowed_ips = getattr(settings, 'ALLOWED_IPS', [])
        
        if not allowed_ips:
            return True  # Si no hay lista, permitir todos
        
        return client_ip in allowed_ips
    
    def check_rate_limit(self, request):
        """Rate limiting simple basado en IP"""
        if not hasattr(settings, 'RATE_LIMIT_ENABLED') or not settings.RATE_LIMIT_ENABLED:
            return True
        
        client_ip = self.get_client_ip(request)
        cache_key = f'rate_limit_{client_ip}'
        
        # Límite: 100 requests por minuto
        limit = getattr(settings, 'RATE_LIMIT_PER_MINUTE', 100)
        
        requests_count = cache.get(cache_key, 0)
        
        if requests_count >= limit:
            return False
        
        cache.set(cache_key, requests_count + 1, 60)  # 60 segundos
        return True
    
    def log_access(self, request):
        """Registrar accesos al sistema"""
        logger.info(
            f"Acceso: {request.method} {request.path} | "
            f"IP: {self.get_client_ip(request)} | "
            f"Usuario: {request.user if request.user.is_authenticated else 'Anónimo'}"
        )
    
    def add_security_headers(self, response):
        """Agregar headers de seguridad adicionales"""
        # Política de seguridad de contenido
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Otros headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=()'
        )
        
        return response


class FileUploadSecurityMiddleware:
    """
    Middleware específico para validar seguridad en subida de archivos
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.method == 'POST' and request.FILES:
            # Validar archivos antes de procesarlos
            if not self.validate_files(request):
                logger.warning(f"Intento de subida de archivo malicioso desde IP: {self.get_client_ip(request)}")
                return HttpResponseForbidden("Archivo no permitido o potencialmente peligroso")
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def validate_files(self, request):
        """Validar archivos subidos"""
        for file_field, uploaded_file in request.FILES.items():
            # Validar extensión
            allowed_extensions = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', ['.pdf'])
            file_extension = '.' + uploaded_file.name.split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                logger.warning(f"Extensión no permitida: {file_extension}")
                return False
            
            # Validar tamaño
            max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 10485760)
            if uploaded_file.size > max_size:
                logger.warning(f"Archivo demasiado grande: {uploaded_file.size} bytes")
                return False
            
            # Validar content type
            if not uploaded_file.content_type.startswith('application/pdf'):
                logger.warning(f"Content-Type no permitido: {uploaded_file.content_type}")
                return False
        
        return True


class AuditMiddleware:
    """
    Middleware para auditoría de acciones críticas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Auditar acciones POST, PUT, DELETE
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.audit_action(request, response)
        
        return response
    
    def audit_action(self, request, response):
        """Registrar acciones importantes"""
        logger.info(
            f"AUDITORÍA: {request.method} {request.path} | "
            f"Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'} | "
            f"IP: {self.get_client_ip(request)} | "
            f"Status: {response.status_code}"
        )
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip