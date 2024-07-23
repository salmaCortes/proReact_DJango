----------L O G I C A  views.py  D E  D J A N G O---------
def encontrar_coordenadas(pdf_path, patron):
        pdf_reader = fitz.open(pdf_path)
        coords = []

        for page_num in range(pdf_reader.page_count):
            pdf_page = pdf_reader[page_num]
            page_text = pdf_page.get_text()

            if patron in page_text:
                coords.append((patron, page_num))

        return coords

    def agregar_imagen_a_pdf(pdf_input, pdf_output, imagen_path, coords, escala=0.5):
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
    if carpeta_id:
        nombreCarpeta = request.GET.get('carpeta_nombre')
        if request.method == 'POST' and 'firmaguardar2' in request.POST: # aquí firmaguardar2
            print("Estoy en el if")
            firma_data_url = request.POST.get('firmaSubcarpeta')
            carpeta = request.POST.get('carpeta')
            documentoContrato = request.POST.get('documento')
            documentoId = request.POST.get('documentoId')
            documentoparafirmar = DocumentoPDF.objects.get(id = documentoId)
            identificador = request.POST.get('identificador')

            if firma_data_url:
                print("Estoy en el if de firma")
                # Decodificar los datos de la firma en formato base64
                formato, imgstr = firma_data_url.split(';base64,')
                ext = formato.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name='firma.{}'.format(ext))
                ubicacion = os.path.join(user.username, nombreCarpeta, data.name)
                

                # Crear el objeto DocumentoPDF y guardar la firma en el campo 'archivo'
                contratoFirmado = DocumentoPDF(
                    nombre="Firma",
                    carpeta=carpeta,
                    jador=trabajador, traba # Asegúrate de asignar el objeto Trabajador correcto aquí
                    customuser=user.username,
                    tipo_documento="Firma",
                    descripcion=documentoContrato,
                )
                contratoFirmado.archivo.save(ubicacion, data, save=True)
                ruta_pdf_original = os.path.join(settings.CUSTOM_UPLOAD_PATH, 'media', documentoparafirmar.archivo.name)
                # Crear una nueva versión del archivo y guardarlo en la base de datos
                cantidad_archivos = VersionesArchivos.objects.filter(documentoPadre=documentoparafirmar.id).count()
                rutaArchivo = os.path.join('pdfs', user.username, nombreCarpeta, 'documento_modificado.pdf')

                #
                print(f"Ruta del rutaArchivo: {rutaArchivo}")
                nueva_version = VersionesArchivos(
                    nombre_documento_padre= documentoContrato,
                    documentoPadre= documentoparafirmar.id,
                    archivo= rutaArchivo,
                    carpeta=carpeta,
                    version=f"V{cantidad_archivos+1}",
                    usuario=user.username, #aquí,  vamos a incorcoporar el nombre del usuario?
                    descripcion="Nueva versión con firma incorporada"
                )
                nueva_version.save()
                # Rutas de los archivos
                pdf_input = ruta_pdf_original
                # Guardar el archivo temporal en la nueva versión
                pdf_output = os.path.join(settings.CUSTOM_UPLOAD_PATH, 'media', 'pdfs', user.username, nombreCarpeta, 'documento_modificado.pdf') # Ruta de salida del archivo PDF
                
                print(f"Ruta del archivoVersion: {nueva_version.archivo}")
                imagen_path = contratoFirmado.archivo # Asegúrate de tener una imagen con canal alfa (transparencia)
                patron = identificador

                # Encontrar las coordenadas del patrón en el PDF
                coords = encontrar_coordenadas(pdf_input, patron)

                # Agregar la imagen y quitar el texto utilizando las coordenadas y escala encontradas
                agregar_imagen_a_pdf(pdf_input, pdf_output, imagen_path, coords, escala=0.4)
                print(f"Se ha agregado la imagen al documento PDF: {pdf_output}")
            return redirect('welcome')


--------M O D A L  F I R M A  H T M L--------
<div class="d-grid gap-2 d-flex justify-content-end">
    <!-- <svg id="miBoton{{ documento_pdf.id }}" class="oculto" xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="currentColor" class="btn btn-light bi bi-pencil-square" viewBox="0 0 16 16" >
        <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
        <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
    </svg> -->
    <div class="modal fade" id="firmarModalDoc{{ documento_pdf.id }}" tabindex="-1" role="dialog" aria-labelledby="firmarModalDocLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-sm" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="firmarModalLabel">Firmar Documento</h5>
                </div>
                
                <div class="modal-body">
                    <form method="POST" onsubmit="guardarFirma({{ documento_pdf.id }})">
                        {% csrf_token %}#aquí
                        <h5>Coloca el identificador que contiene el contrato.</h5>
                        <p class="fw-medium text-muted fs-6">El nombre del identificador debe ir dentro de corchetes "[ ]"</p>
                        <input type="text" name="identificador" placeholder="Ejemplo: [Firma del cliente]" style="width: 100%;">
                        <canvas class="canvas" id="canvas{{ documento_pdf.id }}" width="253" height="200"></canvas>
                        <br>
                        
                        <input type="hidden" name="firma" id="firma{{ documento_pdf.id }}">
                        <input type="hidden" name="carpeta" value="{{ documento_pdf.carpeta }}">
                        <input type="hidden" name="documento" value="{{ documento_pdf.nombre }}">
                        <input type="hidden" name="documentoId" value="{{ documento_pdf.id }}">
                        <br>
                        <div class="d-grid gap-1 justify-content-end d-flex">
                            <button class="btn btn-primary" type="button" onclick="limpiarFirma({{ documento_pdf.id }})">Limpiar</button>
                            <button class="btn btn-secondary" type="submit" name="firmaguardar">Guardar Firma</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
                        
<script>
    document.addEventListener("DOMContentLoaded", function() {
        setupFirmaModal({{ documento_pdf.id }});
    });
</script>


----------S C R I P T  F I R M A--------
<script>
    function setupFirmaModal(documentoId) {
        var canvas = document.getElementById('canvas' + documentoId);
        var firmaInput = document.getElementById('firma' + documentoId);
        var contexto = canvas.getContext('2d');
        var painting = false;

        canvas.addEventListener('mousedown', function (e) {
            painting = true;
            dibujar(e, canvas, firmaInput, contexto, painting);
        });

        canvas.addEventListener('mousemove', function (e) {
            if (painting) {
                dibujar(e, canvas, firmaInput, contexto, painting);
            }
        });

        canvas.addEventListener('mouseup', function () {
            painting = false;
            contexto.beginPath();
        });

        function dibujar(e, canvas, firmaInput, contexto, painting) {
            if (!painting) return;

            contexto.lineWidth = 2;
            contexto.lineCap = 'round';
            contexto.strokeStyle = '#000';

            contexto.lineTo(e.clientX - canvas.getBoundingClientRect().left, e.clientY - canvas.getBoundingClientRect().top);
            contexto.stroke();
            contexto.beginPath();
            contexto.moveTo(e.clientX - canvas.getBoundingClientRect().left, e.clientY - canvas.getBoundingClientRect().top);

            firmaInput.value = canvas.toDataURL();
        }
    }

    function limpiarFirma(documentoId) {
        var canvas = document.getElementById('canvas' + documentoId);
        var firmaInput = document.getElementById('firma' + documentoId);
        var contexto = canvas.getContext('2d');

        contexto.clearRect(0, 0, canvas.width, canvas.height);
        firmaInput.value = '';
    }

    function guardarFirma(documentoId) {
        document.forms[0].submit();
    }
</script>