# planos/api.py
from rest_framework import viewsets
from .models import Plano
from .serializers import PlanoSerializer, PlanoListSerializer, PlanoCreateSerializer, PlanoUpdateSerializer
from .services import procesar_pdf

class PlanoViewSet(viewsets.ModelViewSet):
    queryset = Plano.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return PlanoListSerializer
        elif self.action == 'create':
            return PlanoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PlanoUpdateSerializer
        return PlanoSerializer

    def perform_create(self, serializer):
        plano = serializer.save(estado="procesando")
        procesar_pdf(plano)
