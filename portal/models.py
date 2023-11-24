from django.db import models
from django.utils.crypto import get_random_string
from django.core.validators import FileExtensionValidator


# Create your models here.
class Admin(models.Model):
    admin_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)


class CreatingAdmin(models.Model):
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    admin_password = models.CharField(max_length= 100, null=True)
    admin_city = models.CharField(max_length=100)
    status = models.CharField(max_length=10, default='Unapproved')
    timestamp = models.DateTimeField(auto_now_add=True, null=True)


class LimoUser(models.Model):
    user_profilepic = models.ImageField(upload_to='driver/profile_pic', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], default='driver/profile_pic/Upic.jpg')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length= 100, null=True)
    password = models.CharField(max_length= 100, null=True)
    confirm_password = models.CharField(max_length= 100, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    player_id = models.CharField(max_length=50, null=True)
    otp = models.CharField(max_length=4, null=True)


class CustomUserToken(models.Model):
    user = models.OneToOneField(LimoUser, on_delete=models.CASCADE)
    key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate a unique key for the token
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        # Generate a unique key for the token
        return get_random_string(length=40)

    def __str__(self):
        return self.key


class Booking(models.Model):
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=100)
    phone_number = models.CharField(max_length= 100, null=True)
    email = models.EmailField(null = True)
    billing_email = models.EmailField(null = True)
    payment_mode = models.CharField(max_length=100, null = True)
    current_location = models.CharField(max_length=255, blank=True, null = True)
    current_coordinates = models.JSONField(null=True)
    destination_location = models.CharField(max_length=255, blank=True, null = True)
    destination_coordinates = models.JSONField(null=True, blank=True)
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    driver_name = models.CharField(max_length=100)
    comment = models.CharField(max_length=100, null = True)
    ride_status = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=100)
    price = models.CharField(max_length=100, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    request_id = models.CharField(max_length=100, null=True)
    link = models.CharField(max_length=200, null=True)


class LimoDriver(models.Model):
    driver_profilepic = models.ImageField(upload_to='driver/profile_pic', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], default='driver/profile_pic/Dpic.png')
    email = models.EmailField(unique=True, null = True)
    otp = models.CharField(max_length=4)
    password = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length= 100, null=True)
    car_name = models.CharField(max_length= 100, null=True)
    year_vehicle = models.CharField(max_length= 100, null=True)
    license_plate = models.CharField(max_length= 100, null=True)
    car_image = models.ImageField(upload_to='driver/car_images', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], null=True)
    driving_license = models.ImageField(upload_to='driver/documents', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], null=True)
    license_plate_image = models.ImageField(upload_to='driver/documents', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], null=True)
    car_insurance_image = models.ImageField(upload_to='driver/documents', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], null=True)
    status = models.CharField(max_length=15, default='pending')
    active = models.CharField(max_length=15, default='offline')
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    wallet = models.CharField(max_length=100, null=True)
    current_location = models.CharField(max_length=255, blank=True, null = True)
    current_coordinates = models.JSONField(null=True)
    rating = models.FloatField(default=0.0)
    total_earning = models.FloatField(default=0.0)
    wallet = models.CharField(max_length=100, default='0')
    total_booking = models.FloatField(default=0)
    player_id = models.CharField(max_length=50, null=True)


class CustomDriverToken(models.Model):
    driver = models.OneToOneField(LimoDriver, on_delete=models.CASCADE)
    key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate a unique key for the token
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        # Generate a unique key for the token
        return get_random_string(length=40)

    def __str__(self):
        return self.key


class DriverReview(models.Model):
    driver = models.ForeignKey(LimoDriver, on_delete=models.CASCADE)
    user = models.ForeignKey(LimoUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # You can use a rating scale (e.g., 1-5 stars)
    review = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.driver.name} by {self.user.name}"


class Notification(models.Model):
    driver = models.ForeignKey(LimoDriver, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(LimoUser, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.driver} - {self.title}"


class Message(models.Model):
    user = models.ForeignKey(LimoUser, on_delete=models.CASCADE, null=True)
    message = models.TextField()
    reply = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return f"Message from {self.user.username}"


class TravellingHistory(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null = True)
    user_profilepic = models.ImageField(upload_to='driver/profile_pic', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], default='driver/profile_pic/Upic.jpg')
    current_location = models.CharField(max_length=255, blank=True, null = True)
    destination_location = models.CharField(max_length=255, blank=True, null = True)
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    driver_name = models.CharField(max_length=100)
    driver_email = models.EmailField(null = True)
    driver_profilepic = models.ImageField(upload_to='driver/profile_pic', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], default='driver/profile_pic/Dpic.png')
    price = models.CharField(max_length=100, null=True)
    timestamp = models.DateTimeField(null=True)