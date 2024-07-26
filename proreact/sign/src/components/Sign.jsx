import React, { useState, useEffect } from 'react';
import "./Sign.css";

export default function Sign() {
    const [documentos, setDocumentos] = useState([]);//obtener la lista de documentos
    const [selectedDocumento, setSelectedDocumento] = useState(null);//obtener el documento clickeado

    useEffect(() => {
        obtenerDocumentos();
        setupFirmaModal();
    }, []);

    //Handle para controlar cuando se hace click en un documento de la lista de documentos
    const handleDocumentoClick = (documento) => {
        setSelectedDocumento(documento);
    };

    //Petición GET para Obtener los documentos de la BD de postgres
    const obtenerDocumentos = () => {
        fetch('http://127.0.0.1:8000/firmas/crearDoc/')
            .then(response => response.json())
            .then(data => {
                // Mostrar documentos con el atributo "tipo_documento" "pdf" o "PDF"
                const documentosPdf = data.filter(documento =>
                    documento.tipo_documento === 'pdf' || documento.tipo_documento === 'PDF'
                );
                setDocumentos(documentosPdf);
            })
            .catch(error => console.error('Error al obtener los documentos a firmar:', error));
    };


    function setupFirmaModal() {
        const canvas = document.getElementById('canvas');
        const firmaInput = document.getElementById('firma');
        const contexto = canvas.getContext('2d');
        let painting = false;
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

    function limpiarFirma() {
        var canvas = document.getElementById('canvas');
        var firmaInput = document.getElementById('firma');
        var contexto = canvas.getContext('2d');

        contexto.clearRect(0, 0, canvas.width, canvas.height);
        firmaInput.value = '';
    }
    //petición POST al servidor de Django para guardar la imagen de la firma en el documento que se tiene que firmar
    function guardarFirma() {
        const firma = document.getElementById('firma').value;
        const identificador = document.querySelector('input[name="identificador"]').value;
        const carpeta = document.querySelector('input[name="carpeta"]').value;
        const documento = document.querySelector('input[name="documento"]').value;
        const documentoId = document.querySelector('input[name="documentoId"]').value;

        const data = {
            firma,
            identificador,
            carpeta,
            documento,
            documentoId
        };

        fetch('http://127.0.0.1:8000/firmas/firmaDoc/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    return (
        <div>
            {/*Lista de documentos*/}
           <div>
                <h2>Documentos</h2>
                <ul className='listaDoc'>
                    {documentos.map((documento, index) => (
                        <li
                            key={index}
                            className={ selectedDocumento === documento ? 'selected' : ''}
                            onClick={() => handleDocumentoClick(documento)}
                        >
                            {documento.documento}
                        </li>
                    ))}
                </ul>
            </div>

            <button>Firmar</button>

            <div className='container mt-5 p-5'>
                <div className="modal-body">
                    <form method="POST" onSubmit={(e) => { e.preventDefault(); guardarFirma(); }}>
                        <h5>Coloca el identificador que contiene el contrato.</h5>
                        <p className="fw-medium text-muted fs-6">El nombre del identificador debe ir dentro de corchetes "[ ]"</p>
                        <input type="text" name="identificador" placeholder="Ejemplo: [Firma del cliente]" style={{ width: '100%' }} />
                        <div className="canvas-container">
                            <canvas className="canvas canvas-design" id="canvas" width="300" height="250"></canvas>
                        </div>
                        <br />
                        <input type="hidden" name="firma" id="firma" />
                        <input type="hidden" name="carpeta" value="media" />
                        <input type="hidden" name="documento" value="docF" />
                        <input type="hidden" name="documentoId" value="23" />
                        <br />
                        <div className="d-grid gap-1 justify-content-end d-flex justify-content-center ">
                            <button className="btn btn-primary" type="button" onClick={() => limpiarFirma()}>Limpiar</button>
                            <button className="btn btn-secondary" type="submit">Guardar Firma</button>
                        </div>
                    </form>
                </div>
            </div>
            
        </div>
    );
}
