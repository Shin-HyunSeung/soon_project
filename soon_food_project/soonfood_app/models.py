from django.db import models

# Create your models here.
class soon_food(models.Model):
    num = models.IntegerField(blank = True)
    # num2 = models.IntegerField(blank = True)
    categori = models.CharField(max_length = 20)
    score = models.FloatField(max_length = 20)
    tell = models.CharField(max_length = 20)
    restaurant = models.CharField(max_length = 20)
    address = models.CharField(max_length = 50)
    sig_menu = models.CharField(max_length = 250)
    price = models.CharField(max_length = 250)
    menu = models.CharField(max_length = 250)
    lat = models.FloatField(max_length = 20)
    long = models.FloatField(max_length = 20)
    
    

class tourlist(models.Model):
    num = models.IntegerField(blank = True)
    # num2 = models.IntegerField(blank = True)
    restaurant = models.CharField(max_length = 20)
    address = models.CharField(max_length = 50)
    lat = models.FloatField(max_length = 20)
    long = models.FloatField(max_length = 20)

class check_select_food(models.Model):
    restaurant = models.CharField(max_length = 20)
