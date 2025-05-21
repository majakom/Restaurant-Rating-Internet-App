from django.shortcuts import render, get_object_or_404
from geopy.distance import distance
from .models import Restaurant
import requests

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def restaurant_list(request):
    search_query = request.GET.get('search', '')
    sort_order = request.GET.get('sort', 'asc')
    
    restaurants = Restaurant.objects.all()
    
    if search_query:
        restaurants = restaurants.filter(name__icontains=search_query)
    
    if sort_order == 'desc':
        restaurants = restaurants.order_by('-name')
    else:
        restaurants = restaurants.order_by('name')

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants
    })


def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant
    })



def nearby_restaurants(request):
    user_ip = get_client_ip(request)

    try:
        response = requests.get(f'https://ipapi.co/{user_ip}/json/')
        data = response.json()
        user_location = (float(data['latitude']), float(data['longitude']))
    except Exception:
        user_location = (52.4064, 16.9252)

    try:
        max_distance_km = float(request.GET.get('distance', 5))
    except ValueError:
        max_distance_km = 5

    nearby = []

    for restaurant in Restaurant.objects.all():
        rest_location = (restaurant.latitude, restaurant.longitude)
        dist = distance(user_location, rest_location).km
        if dist <= max_distance_km:
            nearby.append((restaurant, round(dist, 2)))

    return render(request, 'restaurants/nearby_restaurants.html', {
        'restaurants': nearby,
        'user_location': user_location,
        'distance': max_distance_km
    })