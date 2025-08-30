from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

@login_required
@permission_required('dashboard.index_viewer', raise_exception=True)
def index(request):
    response = requests.get(settings.API_URL)  # URL de la API
    reservations_data = response.json()  # Convertir la respuesta a JSON
    
    # Convertir el objeto de reservas a una lista
    # La API devuelve un objeto donde las claves son los IDs
    reservations = []
    for reservation_id, reservation in reservations_data.items():
        reservation['id'] = reservation_id  # Agregar el ID como campo
        reservations.append(reservation)
    
    #Número total de reservas
    total_reservations = len(reservations)
    
    #Cantidad de clientes diferentes (usando "name")
    unique_clients = len(set(reservation.get('name', '') for reservation in reservations if reservation.get('name')))
    
    #Promedio de personas por mesa (usando "people")
    total_people = 0
    for reservation in reservations:
        people_str = reservation.get('people', '0')
        # Manejar casos como "5+" o "2"
        if isinstance(people_str, str):
            people_str = people_str.replace('+', '')
        try:
            people_count = int(people_str)
            total_people += people_count
        except (ValueError, TypeError):
            continue
    
    avg_people_per_table = round(total_people / total_reservations, 1) if total_reservations > 0 else 0
    
    #Usuario con mayor cantidad de reservas
    client_reservation_counts = {}
    for reservation in reservations:
        client_name = reservation.get('name', '')
        if client_name:
            client_reservation_counts[client_name] = client_reservation_counts.get(client_name, 0) + 1
    
    max_reservations_client = max(client_reservation_counts.items(), key=lambda x: x[1]) if client_reservation_counts else ('', 0)
    top_client_name, top_client_reservations = max_reservations_client
    
    # Preparar datos para la tabla
    table_data = []
    for reservation in reservations:
        table_data.append({
            'reservation_id': reservation.get('id', ''),
            'people': reservation.get('people', ''),
            'date': reservation.get('date', '')
        })
    
    # Implementar paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(table_data, 10)  # 10 elementos por página
    page_obj = paginator.get_page(page_number)
    
    # Calcular datos para el gráfico: cantidad de personas por día
    date_people_stats = {}
    for reservation in reservations:
        date = reservation.get('date', '')
        people_str = reservation.get('people', '0')
        
        # Manejar casos como "5+" o "2"
        if isinstance(people_str, str):
            people_str = people_str.replace('+', '')
        try:
            people_count = int(people_str)
        except (ValueError, TypeError):
            people_count = 0
        
        if date not in date_people_stats:
            date_people_stats[date] = 0
        
        date_people_stats[date] += people_count
    
    # Ordenar por fecha para el gráfico
    chart_data = []
    for date, total_people in sorted(date_people_stats.items()):
        chart_data.append({
            'date': date,
            'total_people': total_people
        })

    data = {
        'title': "Dashboard de Reservas",
        'total_reservations': total_reservations,
        'unique_clients': unique_clients,
        'avg_people_per_table': avg_people_per_table,
        'top_client_name': top_client_name,
        'top_client_reservations': top_client_reservations,
        'reservations': reservations,
        'table_data': page_obj,
        'page_obj': page_obj,
        'chart_data': chart_data,
    }

    return render(request, 'dashboard/index.html', data)

