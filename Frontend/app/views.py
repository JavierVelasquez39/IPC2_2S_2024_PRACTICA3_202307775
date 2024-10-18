from django.shortcuts import render
from .forms import FileForm
import requests
import xml.etree.ElementTree as ET

api = 'http://127.0.0.1:5000'

# Lista de departamentos válidos
DEPARTAMENTOS_VALIDOS = [
    'Guatemala', 'Baja Verapaz', 'Chimaltenango', 'Chiquimula', 'El Progreso', 
    'Escuintla', 'Huehuetenango', 'Izabal', 'Jalapa', 'Jutiapa', 'Petén', 
    'Quetzaltenango', 'Quiché', 'Retalhuleu', 'Sacatepéquez', 'San Marcos', 
    'Santa Rosa', 'Sololá', 'Suchitepéquez', 'Totonicapán', 'Zacapa', 'Alta Verapaz'
]

# Create your views here.
def index(request):
    return render(request, 'homepage.html')

def cargar_archivo(request):
    xml_content = ""
    ventas_validas = []
    ventas_invalidas = []
    
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            xml_content = file.read().decode('utf-8')
            # Procesar el contenido del XML
            root = ET.fromstring(xml_content)
            
            for venta in root.find('ListadoVentas'):
                departamento = venta.get('departamento')
                fecha = venta.find('Fecha').text
                venta_data = {
                    'departamento': departamento,
                    'fecha': fecha
                }
                if departamento in DEPARTAMENTOS_VALIDOS:
                    ventas_validas.append(venta_data)
                else:
                    ventas_invalidas.append(venta_data)
            
            # Enviar datos al backend Flask
            try:
                response = requests.post(api+'/config/postXML', data=xml_content.encode('utf-8'))
                if response.status_code == 200:
                    print("Respuesta del servidor Flask: ", response.json())
                else:
                    print("Error al enviar datos al backend Flask: ", response.text)
            except requests.ConnectionError:
                print("Error: No se pudo conectar al backend Flask")
        else:
            print(form.errors)
    else:
        form = FileForm()
    
    context = {
        'form': form,
        'ventas_validas': ventas_validas,
        'ventas_invalidas': ventas_invalidas,
        'xml_content': xml_content
    }
    return render(request, 'cargar_archivo.html', context)

def revisar_datos(request):
    try:
        response = requests.get(api+'/config/obtenerVentasXML')
        if response.status_code == 200:
            datos_procesados = response.content.decode('utf-8')
        else:
            datos_procesados = '<message>Error al obtener datos procesados</message>'
    except requests.ConnectionError:
        datos_procesados = '<message>Error: No se pudo conectar al backend Flask</message>'
    return render(request, 'revisar_datos.html', {'datos_procesados': datos_procesados})

def ver_grafico(request):
    try:
        response = requests.get(api+'/config/obtenerVentas')
        if response.status_code == 200:
            ventas = response.json()['ventas']
            labels = [venta['departamento'] for venta in ventas]
            data = [venta['cantidad'] for venta in ventas]
        else:
            labels = []
            data = []
    except requests.ConnectionError:
        labels = []
        data = []
    return render(request, 'ver_grafico.html', {'labels': labels, 'data': data})

def datos_estudiante(request):
    nombre_completo = "Tu Nombre Completo"
    carnet = "Tu Carnet"
    return render(request, 'datos_estudiante.html', {'nombre_completo': nombre_completo, 'carnet': carnet})

def subirXML(request):
    xml_content = ""
    response_message = ""

    if request.method == 'POST':
        xml_content = request.POST.get('xml', '')
        cleaned_xml_content = xml_content.encode('utf-8')
        try:
            response = requests.post(api+'/config/postXML', data=cleaned_xml_content)
            if response.status_code == 200:
                response_message = response.json().get('message', '')
        except requests.ConnectionError:
            response_message = "Error: No se pudo conectar al backend Flask"

    return render(request, 'configurar.html', {'xml_content': xml_content, 'response': response_message})