from django.db import models
from django.contrib.auth.models import User


class Plano(models.Model):
    """Modelo para almacenar planos de agrimensura cargados"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Procesamiento'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=255, help_text="Título descriptivo del plano")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción adicional")
    
    # Archivo
    archivo_pdf = models.FileField(upload_to='uploads/planos/', help_text="Archivo PDF del plano")
    
    # Estado del procesamiento
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Metadatos
    fecha_carga = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planos', null=True, blank=True)
    
    # Resultados del procesamiento
    texto_extraido = models.TextField(blank=True, null=True, help_text="Texto extraído del PDF")
    datos_procesados = models.JSONField(blank=True, null=True, help_text="Datos estructurados extraídos")
    
    # Memoria descriptiva generada
    memoria_path = models.CharField(max_length=500, blank=True, null=True, help_text="Ruta de la memoria Word generada")
    
    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'
        ordering = ['-fecha_carga']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"