from django.db import models
from geopy.geocoders import Nominatim
from django.contrib.auth.models import User
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import PIL

class Restaurant(models.Model):
    CUISINE_CHOICES = [
        ('polish', 'Polska'),
        ('italian', 'Włoska'),
        ('asian', 'Azjatycka'),
        ('fastfood', 'Fast Food'),
        ('vegan', 'Wegańska'),
        ('other', 'Inna'),
    ]
     
    name = models.CharField(max_length=100)
    address = models.TextField()
    cuisine_type = models.CharField(max_length=50)
    image = models.ImageField(upload_to='restaurant_images/', blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)  
    longitude = models.FloatField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def average_rating(self):
        ratings = [comment.rating for comment in self.comments.all()]
        return sum(ratings) / len(ratings) if ratings else 0

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.address:
            geolocator = Nominatim(user_agent="restaurant_app")
            try:
                location = geolocator.geocode(self.address)
                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
            except (GeocoderTimedOut, GeocoderServiceError):
                pass
        super().save(*args, **kwargs)


class Comment(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    text = models.TextField()
    rating = models.IntegerField() 

    def __str__(self):
        return f"{self.author} - {self.rating}/5"


# class MenuItem(models.Model):
#     name = models.CharField(max_length=255)
#     restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menuitem')
