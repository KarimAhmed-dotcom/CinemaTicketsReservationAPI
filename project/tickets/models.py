from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Guest Movie Reservation

class Movie(models.Model):
    hall=models.CharField(max_length=10)
    movie=models.CharField(max_length=10)
    date=models.DateField()
    
class Guest(models.Model):
    name=models.CharField(max_length=10)
    mobile=models.CharField(max_length=10)
    
class Reservation(models.Model):
    guest=models.ForeignKey(Guest,related_name='reservations',on_delete=models.CASCADE)
    movie=models.ForeignKey(Movie,related_name='reservations',on_delete=models.CASCADE)
    
    
class Post(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=50)
    body=models.TextField()