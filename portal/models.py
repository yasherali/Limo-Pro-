from django.db import models


# Create your models here.
class Admin(models.Model):
    admin_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)


class CreatingAdmin(models.Model):
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    admin_pnumber = models.CharField(max_length= 100)
    approved = models.BooleanField(default=False)
