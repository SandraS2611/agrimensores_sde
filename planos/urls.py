import uuid
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views
from rest_framework.routers import DefaultRouter
from .api import PlanoViewSet
from .views import login_view

# Generamos tokens aleatorios al iniciar el servidor
def random_token():
    return uuid.uuid4().hex[:8]

LISTA_TOKEN = random_token()
UPLOAD_TOKEN = random_token()
DETALLE_TOKEN = random_token()
LOGOUT_TOKEN = random_token()
REPROCESAR_TOKEN = random_token()
DESCARGAR_TOKEN = random_token()
DESCARGAR_PDF_TOKEN = random_token()
DRIVE_TOKEN = random_token()
REPORTE_TOKEN = random_token()
ELIMINAR_TOKEN = random_token()

# Router para la API REST
router = DefaultRouter()
router.register(r'planos', PlanoViewSet)

urlpatterns = [
    # Raíz muestra login.html
    path("", login_view, name="login"),

    # Rutas ofuscadas (HTML)
    path(f'panel/{LISTA_TOKEN}/', views.lista_planos, name='lista_planos'),
    path(f'panel/{UPLOAD_TOKEN}/upload/', views.upload_plano, name='upload_plano'),
    path(f'panel/{DETALLE_TOKEN}/detalle/<int:plano_id>/', views.detalle_plano, name='detalle_plano'),
    path(f'panel/{LOGOUT_TOKEN}/logout/', LogoutView.as_view(next_page="/"), name="logout"),
    path(f'panel/{REPROCESAR_TOKEN}/reprocesar/<int:plano_id>/', views.reprocesar_plano, name='reprocesar_plano'),
    path(f'panel/{DESCARGAR_TOKEN}/descargar-memoria/<int:plano_id>/', views.descargar_memoria, name='descargar_memoria'),
    path(f'panel/{DESCARGAR_PDF_TOKEN}/descargar-memoria-pdf/<int:plano_id>/', views.descargar_memoria_pdf, name='descargar_memoria_pdf'),
    path(f'panel/{DRIVE_TOKEN}/subir-drive/<int:plano_id>/', views.subir_memoria_drive, name='subir_memoria_drive'),
    path(f'panel/{REPORTE_TOKEN}/reporte/<int:plano_id>/', views.ver_reporte, name='ver_reporte'),
    path(f'panel/{ELIMINAR_TOKEN}/eliminar/<int:plano_id>/', views.eliminar_plano, name='eliminar_plano'),

    # API REST (sin ofuscación, para clientes externos)
    path('api/', include(router.urls)),
]
