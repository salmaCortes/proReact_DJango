import base64
import json
import os
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import fitz  # PyMuPDF
from PIL import Image
from .models import Documento, DocumentoVersion
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import DocumentoSerializer
import tempfile
import shutil
#NOTA: RECUERDA QUE LAS CARPETAS MENCIONADAS EN ESTE CÓDIGO, SON SUBCARPETAS QUE SE CREARÁN en la carpeta definida en   ruta_pdf_original
# que en este caso es la carpeta "media"
class CrearDocViewSet(viewsets.ViewSet):
    
    # Método para obtener los documentos PDFs a firmar
    def list(self, request):
        if request.method == 'GET':
            documentos = Documento.objects.all()
            serializer = DocumentoSerializer(documentos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


    #SUbir el documento pdf a firmar 
    def create(self, request):
        if request.method == 'POST':
            serializer = DocumentoSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Documento creado correctamente', 'documento': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FirmarDoc(APIView):

    @staticmethod
    #encontrar las coordenadas del identificador en el documento pdf, ya que se lo pasamos a esta función y esta función la tiene en la 
    # variable "patron"
    def encontrar_coordenadas(pdf_path, patron):
        pdf_reader = fitz.open(pdf_path)
        coords = []

        for page_num in range(pdf_reader.page_count):
            pdf_page = pdf_reader[page_num]
            page_text = pdf_page.get_text()

            if patron in page_text:
                coords.append((patron, page_num))

        return coords

    @staticmethod
    def agregar_imagen_a_pdf(pdf_input, pdf_output, imagen_path, coords, escala=0.5):
        #pdf_input es el path del archivo  pdf
        # Abre el archivo PDF
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
            imagen = Image.open(imagen_path) #se abre la imagen de  la firma  en el path "media/documentos/firmas_generadas"
            imagen.save("temp_image.png", "PNG") #se guarda de forma temporal la imagen de la firma generada y la guarda en backSign

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

            # Agregar la imagen a la página del pdf en donde esté el patrón con las nuevas coordenadas y tamaño escalado
            page.insert_image((x_nuevo, y_nuevo, x_nuevo + imagen_width, y_nuevo + imagen_height), filename="temp_image.png")

        # Guardar el PDF modificado en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_filename = temp_file.name
            pdf_writer.save(temp_filename)
        
        # Mover el archivo temporal al destino final
        shutil.move(temp_filename, pdf_output)
        
        pdf_writer.close()

    @csrf_exempt
    def post(self, request):
        #if request.method == 'POST' and 'firmaguardar' in request.POST:
        if request.method == 'POST':
            data = json.loads(request.body)

            #Parametros que se necesitan en la solicitud POST:

            firma_data_url = data.get('firma') #este se obtiene de la modal de firmar 
            identificador = data.get('identificador')#este se obtiene de la modal de firmar 
            carpeta = data.get('carpeta')
            documentoContrato = data.get('documento')
            documentoId = data.get('documentoId')
            #

            documentoparafirmar = Documento.objects.get(id=documentoId) #instancia de la entidad "Documento", el cual, 
            #obtiene el registro u objeto en la BD del codumento a  firmar

            if firma_data_url:
                # Decodificar la firma y guardarla como archivo
                formato, imgstr = firma_data_url.split(';base64,')
                ext = formato.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name='firma.{}'.format(ext))
                ubicacion = os.path.join('firmas_generadas', data.name) #nombre de la carpeta en donde se guardará la firma

                # Crear una instancia de la clase "Documento" para que en la tabla de la entidad "Documento", guardar la firma generada por el usuario
                contratoFirmado = Documento(
                    documento="Firma_generada_por_usuario",
                    carpeta=carpeta,
                    tipo_documento="Firma",
                    descripcion=documentoContrato,
                )
                contratoFirmado.archivo.save(ubicacion, data, save=True)# se guarda la firma

                # Ruta del archivo original y archivo de salida PDF
                ruta_pdf_original = os.path.join(settings.MEDIA_ROOT, documentoparafirmar.archivo.name)#obtiene el nombre del archivo pdf a  firmar gracias al " input field" de la clase "Documento"
                rutaArchivo = os.path.join(documentoparafirmar.archivo.name )#aquí es de con que nombre se va a guardar el documento pdf firmado y en que carpeta se guardará
                                                                            #que en este caso, es para guardarlo en "media/documentos"porque dije en "models.py" que los 
                                                                            #documentos se guarden en la subcarpeta "documentos"
                                                                            
                pdf_output = os.path.join(settings.MEDIA_ROOT, rutaArchivo) #pdf_output es el path final del documento ya firmado

                # Encontrar coordenadas del patrón(identificador) en el PDF
                coords = FirmarDoc.encontrar_coordenadas(ruta_pdf_original, identificador)
                
               
                imagen_path = contratoFirmado.archivo.path #se obtiene el path de la firma
                FirmarDoc.agregar_imagen_a_pdf(ruta_pdf_original, pdf_output, imagen_path, coords, escala=0.4)

                # Crear una nueva versión del documento
                cantidad_archivos = DocumentoVersion.objects.filter(documento_padre=documentoparafirmar.id).count()#obtiene el id del documento que se manda a firmar para así, 
                                                                                                                    #el número de versión del documento
                nueva_version = DocumentoVersion(
                    nombre_documento_padre=documentoContrato,
                    documento_padre=documentoparafirmar.id,
                    archivo=rutaArchivo,
                    carpeta=carpeta,
                    version=f"V{cantidad_archivos + 1}",
                    descripcion="Nueva versión con firma incorporada"
                )
                nueva_version.save()

                return Response({'message': 'Firma agregada correctamente', 'pdf_output': pdf_output})#pdf_output es el path del documento firmado

        return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
