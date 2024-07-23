import React, { useEffect } from 'react';
import "./Sing.css"

export default function Sign() {
    useEffect(() => {
        setupFirmaModal();
    }, []);

    function setupFirmaModal() {
        var canvas = document.getElementById('canvas');
        var firmaInput = document.getElementById('firma');
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

    function limpiarFirma() {
        var canvas = document.getElementById('canvas');
        var firmaInput = document.getElementById('firma');
        var contexto = canvas.getContext('2d');

        contexto.clearRect(0, 0, canvas.width, canvas.height);
        firmaInput.value = '';
    }

    function guardarFirma() {
        document.forms[0].submit();
    }

    return (
        <div className='container mt-5 p-5'>
            <div className="modal-body">
                <form method="POST" onSubmit={(e) => { e.preventDefault(); guardarFirma(); }}>
                    {/*  */}
                    <h5>Coloca el identificador que contiene el contrato.</h5>
                    <p className="fw-medium text-muted fs-6">El nombre del identificador debe ir dentro de corchetes "[ ]"</p>
                    <input type="text" name="identificador" placeholder="Ejemplo: [Firma del cliente]" style={{ width: '100%' }} />
                    <div className="canvas-container">
                        <canvas className="canvas canvas-design" id="canvas" width="300" height="250"></canvas>
                    </div>
                    <br />
                    <input type="hidden" name="firma" id="firma" />
                    <input type="hidden" name="carpeta" value="nombre_de_la_carpeta" />
                    <input type="hidden" name="documento" value="nombre_del_documento" />
                    <input type="hidden" name="documentoId" value="id_del_documento" />
                    <br />
                    <div className="d-grid gap-1 justify-content-end d-flex justify-content-center ">
                        <button className="btn btn-primary" type="button" onClick={() => limpiarFirma()}>Limpiar</button>
                        <button className="btn btn-secondary" type="submit" name="firmaguardar">Guardar Firma</button>
                    </div>
                </form>
            </div>
        </div>
    );
}
