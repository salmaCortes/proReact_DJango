from django.db import models

class Documento(models.Model):
    documento = models.CharField(null=True,max_length=255)
    carpeta = models.CharField(max_length=255)
    tipo_documento = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    archivo = models.FileField(upload_to='documentos/')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.documento

class DocumentoVersion(models.Model):
    documento_padre = models.IntegerField(null=True)
    nombre_documento_padre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='pdfs/')
    carpeta = models.CharField(max_length=255)
    version = models.CharField(max_length=10)
    descripcion = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre_documento_padre} - {self.version}'
