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
    posts = response.json()  # Convertir la respuesta a JSON
    
    #Número total de respuestas
    total_responses = len(posts)
    
    #Promedio de caracteres por título
    total_characters = sum(len(post.get('title', '')) for post in posts)
    avg_title_length = round(total_characters / total_responses, 1) if total_responses > 0 else 0
    
    #Número de posts con títulos largos (>50 caracteres)
    long_titles = sum(1 for post in posts if len(post.get('title', '')) > 50)
    
    #Usuario con más posts (basado en userId)
    user_post_counts = {}
    for post in posts:
        user_id = post.get('userId', 0)
        user_post_counts[user_id] = user_post_counts.get(user_id, 0) + 1
    
    max_posts_user = max(user_post_counts.items(), key=lambda x: x[1]) if user_post_counts else (0, 0)
    top_user_id, top_user_posts = max_posts_user
    
    # Preparar datos para la tabla
    table_data = []
    for post in posts:
        table_data.append({
            'user_id': post.get('userId', ''),
            'post_id': post.get('id', ''),
            'title': post.get('title', '')
        })
    
    # Implementar paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(table_data, 10)  # 10 elementos por página
    page_obj = paginator.get_page(page_number)
    
    # Calcular datos para el gráfico: promedio de caracteres en título por usuario
    user_title_stats = {}
    for post in posts:
        user_id = post.get('userId', 0)
        title_length = len(post.get('title', ''))
        
        if user_id not in user_title_stats:
            user_title_stats[user_id] = {'total_chars': 0, 'count': 0}
        
        user_title_stats[user_id]['total_chars'] += title_length
        user_title_stats[user_id]['count'] += 1
    
    # Calcular promedio por usuario
    chart_data = []
    for user_id, stats in user_title_stats.items():
        avg_chars = round(stats['total_chars'] / stats['count'], 1)
        chart_data.append({
            'user_id': user_id,
            'avg_title_length': avg_chars
        })
    
    # Ordenar por user_id para el gráfico
    chart_data.sort(key=lambda x: x['user_id'])

    data = {
        'title': "Landing Page Dashboard",
        'total_responses': total_responses,
        'avg_title_length': avg_title_length,
        'long_titles': long_titles,
        'top_user_id': top_user_id,
        'top_user_posts': top_user_posts,
        'posts': posts,
        'table_data': page_obj,
        'page_obj': page_obj,
        'chart_data': chart_data,
    }

    return render(request, 'dashboard/index.html', data)

