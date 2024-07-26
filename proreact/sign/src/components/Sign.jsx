import React, { useState, useEffect } from 'react';
import "./Sign.css";

export default function Sign() {
    const [documentos, setDocumentos] = useState([]);
    const [selectedDocumento, setSelectedDocumento] = useState(null);
    
    const [modalValores, setModalValores] = useState({
        carpeta: '',
        documento: '',
        documentoId: null,
    });

    useEffect(() => {
        obtenerDocumentos();
        setupFirmaModal();
    }, []);


    const handleDocumentoClick = (documento) => {
        console.log('Documento Clickeado:', documento); 
        setSelectedDocumento(documento);
    };

    const clickbotonFirmar = () => {
        
        if (selectedDocumento) {
            console.log("Id del documento clickeado: ", selectedDocumento.id);
            setModalValores({
                carpeta: selectedDocumento.carpeta,
                documento: selectedDocumento.documento,
                documentoId: selectedDocumento.id
            });
        } else {
            console.error('Error: No hay documento seleccionado o el ID del documento no es válido');
        }
    };

    const obtenerDocumentos = () => {
        fetch('http://127.0.0.1:8000/firmas/crearDoc/')
            .then(response => response.json())
            .then(data => {
                console.log('Datos recibidos:', data); // Verifica los datos recibidos
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

    function guardarFirma() {
        const firma = document.getElementById('firma').value;
        const identificador = document.querySelector('input[name="identificador"]').value;
        const carpeta = modalValores.carpeta;
        const documento = modalValores.documento;
        const documentoId = modalValores.documentoId;

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
            <div>
                <h2>Documentos</h2>
                <ul className='listaDoc'>
                    {documentos.map((documento, index) => (
                        <li
                            key={index}
                            className={selectedDocumento === documento ? 'selected' : ''}
                            onClick={() => handleDocumentoClick(documento)}
                        >
                            {documento.documento}
                        </li>
                    ))}
                </ul>
            </div>

            <button onClick={clickbotonFirmar}>Firmar</button>

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
                        <input type="hidden" name="carpeta" value={modalValores.carpeta} />
                        <input type="hidden" name="documento" value={modalValores.documento} />
                        <input type="hidden" name="documentoId" value={modalValores.documentoId} />
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
