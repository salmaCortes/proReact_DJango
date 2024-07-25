from rest_framework import serializers
from .models import Documento

class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = ['documento', 'carpeta', 'tipo_documento', 'descripcion', 'archivo']
