from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
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
    print("Datos recibidos:", data)  # Log para verificar los datos recibidos
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
                print("Venta agregada:", venta_obj.__dict__)  # Log para verificar las ventas agregadas
            else:
                print(f'Error en la fecha: {fecha}')  # Log para errores en la fecha
        else:
            print(f'Departamento inválido: {departamento}')  # Log para departamentos inválidos

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
    print("Ventas devueltas:", ventas)  # Log para verificar las ventas devueltas
    return jsonify({'ventas': ventas})

@app.route('/config/obtenerVentasXML', methods=['GET'])
def getVentasXML():
    root = ET.Element("resultados")
    departamentos_elem = ET.SubElement(root, "departamentos")
    ventas_por_departamento = {}

    # Contar ventas por departamento
    for venta in listadoVentas:
        if venta.departamento in ventas_por_departamento:
            ventas_por_departamento[venta.departamento] += venta.cantidad
        else:
            ventas_por_departamento[venta.departamento] = venta.cantidad

    # Crear XML solo con departamentos que tienen ventas
    for departamento, cantidad in ventas_por_departamento.items():
        if cantidad > 0:
            departamento_elem = ET.SubElement(departamentos_elem, departamento.replace(" ", ""))
            cantidad_elem = ET.SubElement(departamento_elem, "cantidadVentas")
            cantidad_elem.text = str(cantidad)

    # Prettify XML usando minidom
    xml_str = ET.tostring(root, encoding='utf-8', method='xml')
    dom = minidom.parseString(xml_str)
    pretty_xml_str = dom.toprettyxml(indent="  ")

    return Response(pretty_xml_str, mimetype='application/xml')

@app.route('/config/obtenerVentasPorDepartamento/<departamento>', methods=['GET'])
def getVentasPorDepartamento(departamento):
    if departamento not in DEPARTAMENTOS_VALIDOS:
        return jsonify({'message': f'Departamento no válido: {departamento}'})

    ventas_departamento = [
        {'fecha': venta.fecha, 'cantidad': venta.cantidad}
        for venta in listadoVentas if venta.departamento == departamento
    ]

    if ventas_departamento:
        print("Ventas por departamento devueltas:", ventas_departamento)  # Log para verificar las ventas por departamento
        return jsonify({'ventas': ventas_departamento})
    else:
        return jsonify({'message': f'No hay ventas registradas para el departamento: {departamento}'})

@app.route('/config/limpiarDatos', methods=['GET'])
def limpiarDatos():
    listadoVentas.clear()
    print("Datos de ventas limpiados")  # Log para verificar la limpieza de datos
    return jsonify({'message': 'Datos de ventas limpiados'})

@app.route('/config/obtenerDatosGrafico', methods=['GET'])
def obtenerDatosGrafico():
    ventas_por_departamento = {}

    # Contar ventas por departamento
    for venta in listadoVentas:
        if venta.departamento in ventas_por_departamento:
            ventas_por_departamento[venta.departamento] += venta.cantidad
        else:
            ventas_por_departamento[venta.departamento] = venta.cantidad

    # Crear una lista de datos para el gráfico
    datos_grafico = [{'departamento': departamento, 'cantidad': cantidad}
                     for departamento, cantidad in ventas_por_departamento.items() if cantidad > 0]

    return jsonify(datos_grafico)

if __name__ == '__main__':
    app.run(debug=True, port=5000)