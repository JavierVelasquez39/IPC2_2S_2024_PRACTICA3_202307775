from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
import re

#  Flask App
app = Flask(__name__)
CORS(app)

listadoVentas = []  # Lista para almacenar las ventas por departamento

# Clase Venta
class Venta:
    def __init__(self, departamento, fecha, cantidad):
        self.departamento = departamento
        self.fecha = fecha
        self.cantidad = cantidad

# Lista de departamentos válidos
DEPARTAMENTOS_VALIDOS = [
    'Guatemala', 'Baja Verapaz', 'Chimaltenango', 'Chiquimula', 'El Progreso', 
    'Escuintla', 'Huehuetenango', 'Izabal', 'Jalapa', 'Jutiapa', 'Petén', 
    'Quetzaltenango', 'Quiché', 'Retalhuleu', 'Sacatepéquez', 'San Marcos', 
    'Santa Rosa', 'Sololá', 'Suchitepéquez', 'Totonicapán', 'Zacapa', 'Alta Verapaz'
]

# Routes
@app.route('/')
def index():
    return 'Sistema de Procesamiento de Ventas por Departamento'

@app.route('/api', methods=['GET'])
def api():
    return jsonify({'message': 'Bienvenido al sistema de procesamiento de ventas'})

@app.route('/config/postXML', methods=['POST'])
def postXML():
    data = request.get_data()
    root = ET.fromstring(data)

    # Procesar ventas del XML
    for venta in root.findall('.//Venta'):
        departamento = venta.get('departamento')
        fecha = venta.find('Fecha').text

        # Verificar si el departamento es válido
        if departamento in DEPARTAMENTOS_VALIDOS:
            # Validar formato de la fecha (formato esperado: DD/MM/YYYY)
            patron_fecha = r'\b(\d{2}/\d{2}/\d{4})\b'
            fecha_valida = re.search(patron_fecha, fecha)
            if fecha_valida:
                venta_obj = Venta(departamento, fecha_valida.group(), 1)  # Cantidad fija a 1
                listadoVentas.append(venta_obj)
            else:
                return jsonify({'message': f'Error en la fecha: {fecha}'})
        else:
            return jsonify({'message': f'Departamento inválido: {departamento}'})

    return jsonify({'message': 'XML procesado correctamente'})

@app.route('/config/obtenerVentas', methods=['GET'])
def getVentas():
    ventas = []
    for venta in listadoVentas:
        ventas.append({
            'departamento': venta.departamento,
            'fecha': venta.fecha,
            'cantidad': venta.cantidad
        })

    return jsonify({'ventas': ventas})

@app.route('/config/obtenerVentasXML', methods=['GET'])
def getVentasXML():
    root = ET.Element("Ventas")
    for venta in listadoVentas:
        venta_elem = ET.SubElement(root, "Venta")
        departamento_elem = ET.SubElement(venta_elem, "Departamento")
        departamento_elem.text = venta.departamento
        fecha_elem = ET.SubElement(venta_elem, "Fecha")
        fecha_elem.text = venta.fecha
        cantidad_elem = ET.SubElement(venta_elem, "Cantidad")
        cantidad_elem.text = str(venta.cantidad)

    xml_str = ET.tostring(root, encoding='utf-8', method='xml')
    return Response(xml_str, mimetype='application/xml')

@app.route('/config/obtenerVentasPorDepartamento/<departamento>', methods=['GET'])
def getVentasPorDepartamento(departamento):
    if departamento not in DEPARTAMENTOS_VALIDOS:
        return jsonify({'message': f'Departamento no válido: {departamento}'})

    ventas_departamento = [
        {'fecha': venta.fecha, 'cantidad': venta.cantidad}
        for venta in listadoVentas if venta.departamento == departamento
    ]

    if ventas_departamento:
        return jsonify({'ventas': ventas_departamento})
    else:
        return jsonify({'message': f'No hay ventas registradas para el departamento: {departamento}'})

@app.route('/config/limpiarDatos', methods=['GET'])
def limpiarDatos():
    listadoVentas.clear()
    return jsonify({'message': 'Datos de ventas limpiados'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)