from rest_framework import serializers
from .models import Plano


class PlanoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Plano"""
    
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    archivo_pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Plano
        fields = [
            'id',
            'titulo',
            'descripcion',
            'archivo_pdf',
            'archivo_pdf_url',
            'estado',
            'estado_display',
            'fecha_carga',
            'fecha_actualizacion',
            'usuario',
            'usuario_username',
            'texto_extraido',
            'datos_procesados',
        ]
        read_only_fields = [
            'id',
            'fecha_carga',
            'fecha_actualizacion',
            'estado',
            'texto_extraido',
            'datos_procesados',
        ]
    
    def get_archivo_pdf_url(self, obj):
        """Obtener URL completa del archivo PDF"""
        if obj.archivo_pdf:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo_pdf.url)
            return obj.archivo_pdf.url
        return None


class PlanoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar planos"""
    
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = Plano
        fields = [
            'id',
            'titulo',
            'descripcion',
            'estado',
            'estado_display',
            'fecha_carga',
            'usuario_username',
        ]


class PlanoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear un plano"""
    
    class Meta:
        model = Plano
        fields = [
            'titulo',
            'descripcion',
            'archivo_pdf',
        ]
    
    def validate_archivo_pdf(self, value):
        """Validar el archivo PDF"""
        # Validar extensión
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError('El archivo debe ser un PDF.')
        
        # Validar tamaño (10MB máximo)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('El archivo no debe superar los 10MB.')
        
        return value
    
    def create(self, validated_data):
        """Crear el plano con el usuario actual"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        
        return super().create(validated_data)


class PlanoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar un plano"""
    
    class Meta:
        model = Plano
        fields = [
            'titulo',
            'descripcion',
        ]