from django.db import models
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    cuisine_type = models.CharField(max_length=50)
    latitude = models.FloatField(blank=True, null=True)  
    longitude = models.FloatField(blank=True, null=True)

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
                # Możesz dodać logowanie błędów lub inne działania
                pass
        super().save(*args, **kwargs)


class Comment(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    text = models.TextField()
    rating = models.IntegerField()  # np. skala 1-5

    def __str__(self):
        return f"{self.author} - {self.rating}/5"
