# planos/decorators.py
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import logging

logger = logging.getLogger('django.security')

def superuser_required(view_func):
    """
    Decorador para restringir acceso solo a superusuarios.
    """
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser)(view_func)

def ip_whitelist_required(allowed_ips=None):
    """
    Decorador para permitir solo IPs específicas
    
    Uso:
        @ip_whitelist_required(['192.168.1.1', '10.0.0.1'])
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            
            if allowed_ips and client_ip not in allowed_ips:
                logger.warning(f"Acceso denegado desde IP no autorizada: {client_ip}")
                return HttpResponseForbidden("Acceso denegado: IP no autorizada")
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def rate_limit(max_requests=10, time_window=60):
    """
    Decorador para limitar rate de requests
    
    Uso:
        @rate_limit(max_requests=5, time_window=60)  # 5 requests por minuto
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            cache_key = f'rate_limit_{view_func.__name__}_{client_ip}'
            
            requests_count = cache.get(cache_key, 0)
            
            if requests_count >= max_requests:
                logger.warning(f"Rate limit excedido para {view_func.__name__} desde IP: {client_ip}")
                return HttpResponseForbidden(
                    f"Demasiadas solicitudes. Máximo {max_requests} por {time_window} segundos."
                )
            
            cache.set(cache_key, requests_count + 1, time_window)
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def audit_action(action_type="ACCESS"):
    """
    Decorador para auditar acciones
    
    Uso:
        @audit_action(action_type="UPLOAD_PLANO")
        def upload_plano(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            username = request.user.username if request.user.is_authenticated else 'Anónimo'
            
            logger.info(
                f"AUDITORÍA [{action_type}]: "
                f"Vista: {view_func.__name__} | "
                f"Usuario: {username} | "
                f"IP: {client_ip} | "
                f"Método: {request.method}"
            )
            
            response = view_func(request, *args, **kwargs)
            
            logger.info(
                f"AUDITORÍA [{action_type}] COMPLETADA: "
                f"Vista: {view_func.__name__} | "
                f"Status: {response.status_code}"
            )
            
            return response
        return wrapped_view
    return decorator


def require_internal_network(view_func):
    """
    Decorador para requerir red interna (IPs locales)
    
    Uso:
        @require_internal_network
        def admin_action(request):
            ...
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        client_ip = get_client_ip(request)
        
        # IPs permitidas (red interna)
        internal_ips = [
            '127.0.0.1',
            'localhost',
        ]
        
        # Rangos de red privada
        if not (client_ip.startswith('192.168.') or 
                client_ip.startswith('10.') or 
                client_ip.startswith('172.16.') or
                client_ip in internal_ips):
            logger.warning(f"Acceso denegado desde IP externa: {client_ip}")
            return HttpResponseForbidden("Acceso denegado: Solo red interna permitida")
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


def require_authenticated(view_func):
    """
    Decorador mejorado que requiere autenticación y registra intentos
    
    Uso:
        @require_authenticated
        def mi_vista(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        client_ip = get_client_ip(request)
        
        logger.info(
            f"Usuario autenticado accediendo: "
            f"{request.user.username} | "
            f"IP: {client_ip} | "
            f"Vista: {view_func.__name__}"
        )
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


def validate_file_upload(allowed_extensions=None, max_size_mb=10):
    """
    Decorador para validar archivos subidos
    
    Uso:
        @validate_file_upload(allowed_extensions=['.pdf'], max_size_mb=10)
        def upload_file(request):
            ...
    """
    if allowed_extensions is None:
        allowed_extensions = ['.pdf']
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.method == 'POST' and request.FILES:
                for field_name, uploaded_file in request.FILES.items():
                    # Validar extensión
                    file_extension = '.' + uploaded_file.name.split('.')[-1].lower()
                    if file_extension not in allowed_extensions:
                        logger.warning(
                            f"Extensión no permitida: {file_extension} | "
                            f"Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}"
                        )
                        return HttpResponseForbidden(
                            f"Extensión de archivo no permitida. Solo se permiten: {', '.join(allowed_extensions)}"
                        )
                    
                    # Validar tamaño
                    max_size_bytes = max_size_mb * 1024 * 1024
                    if uploaded_file.size > max_size_bytes:
                        logger.warning(
                            f"Archivo demasiado grande: {uploaded_file.size} bytes | "
                            f"Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}"
                        )
                        return HttpResponseForbidden(
                            f"Archivo demasiado grande. Máximo permitido: {max_size_mb}MB"
                        )
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


# Función auxiliar
def get_client_ip(request):
    """Obtener IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip