import base64
import json
import os
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import fitz  # PyMuPDF
from PIL import Image
from .models import Documento, DocumentoVersion
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class FirmasViewSet(viewsets.ViewSet):
    
    def encontrar_coordenadas(self, pdf_path, patron):
        pdf_reader = fitz.open(pdf_path)
        coords = []

        for page_num in range(pdf_reader.page_count):
            pdf_page = pdf_reader[page_num]
            page_text = pdf_page.get_text()

            if patron in page_text:
                coords.append((patron, page_num))

        return coords

    def agregar_imagen_a_pdf(self, pdf_input, pdf_output, imagen_path, coords, escala=0.5):
        pdf_writer = fitz.open(pdf_input)

        for patron, patron_page_num in coords:
            page = pdf_writer[patron_page_num]

            # Obtener coordenadas del texto
            rectangulos = page.search_for(patron)

            for rectangulo in rectangulos:
                x, y, x1, y1 = rectangulo

                # Crear una forma con el mismo color que el fondo de la página
                page.draw_rect(fitz.Rect(x, y, x1, y1), fill=(1, 1, 1), width=0)

            # Convertir la imagen a formato PNG
            imagen = Image.open(imagen_path)
            imagen.save("temp_image.png", "PNG")

            # Escalar la imagen
            imagen = imagen.resize((int(imagen.width * escala), int(imagen.height * escala)))

            # Obtener las dimensiones de la imagen escalada
            imagen_width, imagen_height = imagen.size

            # Calcular las coordenadas para centrar la imagen sobre el patrón
            centro_patron_x = (x + x1) / 2
            centro_patron_y = (y + y1) / 2

            # Calcular las nuevas coordenadas para centrar la imagen sobre el patrón
            x_nuevo = centro_patron_x - imagen_width / 2
            y_nuevo = centro_patron_y - imagen_height / 2

            # Agregar la imagen a la página con las nuevas coordenadas y tamaño escalado
            page.insert_image((x_nuevo, y_nuevo, x_nuevo + imagen_width, y_nuevo + imagen_height), filename="temp_image.png")

        pdf_writer.save(pdf_output)
        pdf_writer.close()

    @action(detail=False, methods=['post']) #decorador - sirve para hacer que ciertas funciones se ejecuten cuando se haga un post en el servidor 
    def handle_signature(self, request):
        if request.method == 'POST':
            data = json.loads(request.body)
            firma_data_url = data.get('firma')
            carpeta = data.get('carpeta')
            documentoContrato = data.get('documento')
            documentoId = data.get('documentoId')
            identificador = data.get('identificador')

            carpeta_id = data.get('carpeta_id')
            if carpeta_id:
                nombreCarpeta = data.get('carpeta_nombre')
                if 'firmaguardar2' in data:
                    firma_data_url = data.get('firmaSubcarpeta')
                    documentoparafirmar = Documento.objects.get(id=documentoId)

                    if firma_data_url:
                        formato, imgstr = firma_data_url.split(';base64,')
                        ext = formato.split('/')[-1]
                        data = ContentFile(base64.b64decode(imgstr), name='firma.{}'.format(ext))
                        ubicacion = os.path.join('documentos', data.name)  

                        contratoFirmado = Documento(
                            nombre="Firma",
                            carpeta=carpeta,
                            tipo_documento="Firma",
                            descripcion=documentoContrato,
                        )
                        contratoFirmado.archivo.save(ubicacion, data, save=True)

                        ruta_pdf_original = os.path.join(settings.MEDIA_ROOT, documentoparafirmar.archivo.name)
                        
                        cantidad_archivos = DocumentoVersion.objects.filter(documentoPadre=documentoparafirmar.id).count()
                        rutaArchivo = os.path.join('pdfs', nombreCarpeta, 'documento_modificado.pdf')
                        pdf_output = os.path.join(settings.MEDIA_ROOT, rutaArchivo)

                        nueva_version = DocumentoVersion(
                            nombre_documento_padre=documentoContrato,
                            documentoPadre=documentoparafirmar.id,
                            archivo=rutaArchivo,
                            carpeta=carpeta,
                            version=f"V{cantidad_archivos+1}",
                            descripcion="Nueva versión con firma incorporada"
                        )
                        nueva_version.save()

                        imagen_path = contratoFirmado.archivo.path
                        patron = identificador

                        coords = self.encontrar_coordenadas(ruta_pdf_original, patron)
                        self.agregar_imagen_a_pdf(ruta_pdf_original, pdf_output, imagen_path, coords, escala=0.4)
                        
                        return Response({'message': 'Firma agregada correctamente', 'pdf_output': pdf_output})

        return Response({'error': 'Método no permitido'}, status=405)
