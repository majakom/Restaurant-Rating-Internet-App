from django.shortcuts import render, get_object_or_404
from geopy.distance import distance as geopy_distance 
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
    cuisine_query = request.GET.get('menu_search', '')
    sort_order = request.GET.get('sort', 'asc')
    distance = request.GET.get('distance')

    restaurants = Restaurant.objects.all()

    # Filtr odległości
    if distance:
        user_ip = get_client_ip(request)
        try:
            response = requests.get(f'https://ipapi.co/{user_ip}/json/')
            data = response.json()
            user_location = (float(data['latitude']), float(data['longitude']))
        except Exception:
            user_location = (52.4064, 16.9252)

        try:
            max_distance_km = float(distance)
        except ValueError:
            max_distance_km = 100

        nearby_restaurants = []
        for restaurant in restaurants:
            if restaurant.latitude is not None and restaurant.longitude is not None:
                rest_location = (restaurant.latitude, restaurant.longitude)
                dist = geopy_distance(user_location, rest_location).km
                if dist <= max_distance_km:
                    nearby_restaurants.append(restaurant)
        restaurants = nearby_restaurants

    # Filtrowanie po nazwie
    if search_query:
        if isinstance(restaurants, list):
            restaurants = [r for r in restaurants if search_query.lower() in r.name.lower()]
        else:
            restaurants = restaurants.filter(name__icontains=search_query)

    # Filtrowanie po typie kuchni
    if cuisine_query:
        if isinstance(restaurants, list):
            restaurants = [r for r in restaurants if cuisine_query.lower() in r.cuisine_type.lower()]
        else:
            restaurants = restaurants.filter(cuisine_type__icontains=cuisine_query)

    # Sortowanie
    if isinstance(restaurants, list):
        restaurants = sorted(restaurants, key=lambda r: r.name.lower(), reverse=(sort_order == 'desc'))
    else:
        if sort_order == 'asc':
            restaurants = restaurants.order_by('name')
        elif sort_order == 'desc':
            restaurants = restaurants.order_by('-name')

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants
    })


def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant
    })






