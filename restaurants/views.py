from django.shortcuts import render, get_object_or_404, redirect
from geopy.distance import distance as geopy_distance 
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Restaurant
import requests
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import RestaurantForm

@login_required
def restaurant_add(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('restaurant_list')
    else:
        form = RestaurantForm()
    return render(request, 'restaurants/restaurant_form.html', {'form': form})

def logout_view(request):
    logout(request)
    return render(request, 'registration/logout.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        errors = []

        if not username or not email or not password1 or not password2:
            errors.append("Wszystkie pola są wymagane.")
        if password1 != password2:
            errors.append("Hasła nie są identyczne.")
        if User.objects.filter(username=username).exists():
            errors.append("Użytkownik o takiej nazwie już istnieje.")
        if User.objects.filter(email=email).exists():
            errors.append("Użytkownik o takim adresie email już istnieje.")

        if errors:
            return render(request, 'register.html', {'errors': errors})

        # Jeśli nie ma błędów, tworzymy użytkownika
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Rejestracja zakończona sukcesem. Możesz się teraz zalogować.")
        return redirect('login')  # przekieruj na stronę logowania

    return render(request, 'registration/register.html')


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






