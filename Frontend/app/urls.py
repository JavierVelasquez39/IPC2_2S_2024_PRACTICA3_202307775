from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cargar_archivo/', views.cargar_archivo, name='cargar_archivo'),
    path('revisar_datos/', views.revisar_datos, name='revisar_datos'),
    path('ver_grafico/', views.ver_grafico, name='ver_grafico'),
    path('datos_estudiante/', views.datos_estudiante, name='datos_estudiante'),
]