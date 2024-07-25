import React, { useEffect } from 'react';
import "./Sign.css";

export default function Sign() {
    useEffect(() => {
        setupFirmaModal();
    }, []);

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
            // Aquí puedes manejar la respuesta del servidor
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    return (
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
                    <input type="hidden" name="documentoId" value="19" />
                    <br />
                    <div className="d-grid gap-1 justify-content-end d-flex justify-content-center ">
                        <button className="btn btn-primary" type="button" onClick={() => limpiarFirma()}>Limpiar</button>
                        <button className="btn btn-secondary" type="submit" >Guardar Firma</button>
                        {/* El botón "Guardar Firma" tenía una propiedad nave con valor "firmarguardar"*/}
                    </div>
                </form>
            </div>
        </div>
    );
}
