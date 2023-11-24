from django.shortcuts import render
from .models import Admin, CreatingAdmin, LimoUser, CustomUserToken, Booking, LimoDriver, CustomDriverToken, DriverReview, Notification, Message, TravellingHistory
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import views, status
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from random import randint
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from geopy.distance import great_circle
from geopy import distance
import requests
import geopy.distance
import random
import string
import os


# Create your views here.
class AdminView(APIView):
    def post(self, request):
        admin_name = request.data.get('admin_name')
        password = request.data.get('password')

        # Check if admin already exists with the provided admin_name
        try:
            admin = Admin.objects.get(admin_name=admin_name)
            return Response({"message": "Admin already exists."}, status=status.HTTP_400_BAD_REQUEST)
        except Admin.DoesNotExist:
            pass

        # Create new admin object and save to database
        admin = Admin(admin_name=admin_name, password=password)
        admin.save()

        return Response({"message": "Admin created successfully"}, status=status.HTTP_201_CREATED)


class AdminLoginView(APIView):
    def post(self, request):
        admin_name = request.data.get('admin_name')
        password = request.data.get('password')

        try:
            admin = Admin.objects.get(admin_name=admin_name, password=password)
        except Admin.DoesNotExist:
            return Response({"message": "Invalid admin credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"message": "Admin login successfully", "admin_name": admin.admin_name, "admin_id": admin.id}, status=status.HTTP_200_OK)


class CreateAdminView(APIView):
    def post(self, request):
        admin_name = request.data.get('admin_name')
        admin_email = request.data.get('admin_email')
        admin_password = request.data.get('admin_password')
        admin_city = request.data.get('admin_city')

        try:
            # Check if an admin with the same email already exists
            existing_admin = CreatingAdmin.objects.get(admin_email=admin_email)
            return JsonResponse({'error': 'Admin with the provided email already exists.'}, status=400)
        except CreatingAdmin.DoesNotExist:
            # Admin with the provided email does not exist, create and approve
            new_admin = CreatingAdmin(
                admin_name=admin_name,
                admin_email=admin_email,
                admin_password=admin_password,
                admin_city=admin_city,
                status='Approved'
            )
            new_admin.save()

            # Send an email with the credentials
            send_mail(
                'Admin Credentials',
                f'Your admin credentials:\nName: {admin_name}\nPassword: {admin_password}',
                'Falcondigitalserv@gmail.com',  # Sender's email
                [admin_email],
                fail_silently=False,
            )

            # Save the credentials in the Admin model
            admin_credentials = Admin(admin_name=admin_name, password=admin_password)
            admin_credentials.save()

            return JsonResponse({'message': 'Admin created and approved'}, status=201)


class CreatingAdminListView(APIView):
    def get(self, request):
        # Query the CreatingAdmin model to retrieve the desired fields
        creating_admins = CreatingAdmin.objects.all().values('admin_name', 'admin_email', 'status', 'timestamp')

        # Convert the queryset to a list for better serialization
        creating_admins_list = list(creating_admins)

        return JsonResponse(creating_admins_list, safe=False)


class CreatingAdminSearchView(APIView):
    def post(self, request):
        admin_name = request.data.get('admin_name')
        admin_email = request.data.get('admin_email')
        status = request.data.get('status')

        filter_conditions = {}

        if admin_name:
            filter_conditions['admin_name__icontains'] = admin_name

        if admin_email:
            filter_conditions['admin_email__icontains'] = admin_email

        if status:
            filter_conditions['status__iexact'] = status  # Case-insensitive exact match

        creating_admins = CreatingAdmin.objects.filter(**filter_conditions).values('admin_name', 'admin_email', 'status', 'timestamp')

        creating_admins_list = list(creating_admins)

        return JsonResponse(creating_admins_list, safe=False)


class ChangeAdminStatusView(APIView):
    def post(self, request):
        admin_name = request.data.get('admin_name')
        admin_email = request.data.get('admin_email')
        new_status = request.data.get('status')

        try:
            # Check if an admin with the provided email exists
            creating_admin = CreatingAdmin.objects.get(admin_email=admin_email)

            if new_status == 'Approved':
                # Send an email with the credentials
                send_mail(
                    'Admin Credentials',
                    f'Your admin credentials:\nName: {admin_name}\nPassword: {creating_admin.admin_password}',
                    'Falcondigitalserv@gmail.com',  # Sender's email
                    [admin_email],
                    fail_silently=False,
                )

                # Save the credentials in the Admin model
                admin = Admin(admin_name=admin_name, password=creating_admin.admin_password)
                admin.save()
            elif new_status == 'Unapproved':
                # If the status is changing from 'Approved' to 'Unapproved', remove the entry from the Admin model
                Admin.objects.filter(admin_name=admin_name).delete()

            # Update the status in the CreatingAdmin model
            creating_admin.status = new_status
            creating_admin.save()

            return JsonResponse({'message': 'Admin status updated'}, status=200)

        except CreatingAdmin.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=404)


class GetLimoUserDetailsView(APIView):
    def get(self, request):
        limo_users = LimoUser.objects.all().values('name', 'email', 'phone_number', 'timestamp')

        # Convert the queryset to a list for better serialization
        limo_users_list = list(limo_users)

        return JsonResponse(limo_users_list, safe=False)


class LimoUserSearchView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')

        filter_conditions = {}

        if name:
            filter_conditions['name__icontains'] = name  # Case-insensitive search

        if email:
            filter_conditions['email__icontains'] = email  # Case-insensitive search

        if phone_number:
            filter_conditions['phone_number__icontains'] = phone_number  # Case-insensitive search

        limo_users = LimoUser.objects.filter(**filter_conditions).values('name', 'email', 'phone_number', 'timestamp')

        limo_users_list = list(limo_users)

        return JsonResponse(limo_users_list, safe=False)


class GetDriverDataView(APIView):
    def get(self, request):
        try:
            drivers = LimoDriver.objects.all()

            # Create a list to store driver data
            driver_data = []

            for driver in drivers:
                # Retrieve driver data and images
                driver_info = {
                    'email': driver.email,
                    'name': driver.name,
                    'phone_number': driver.phone_number,
                    'car_name': driver.car_name,
                    'year_vehicle': driver.year_vehicle,
                    'license_plate': driver.license_plate,
                    'car_image': driver.car_image.url if driver.car_image else None,
                    'driving_license': driver.driving_license.url if driver.driving_license else None,
                    'license_plate_image': driver.license_plate_image.url if driver.license_plate_image else None,
                    'car_insurance_image': driver.car_insurance_image.url if driver.car_insurance_image else None,
                    'status': driver.status,
                    'active': driver.active,
                    'timestamp': driver.timestamp,
                    'wallet': driver.wallet,
                }

                driver_data.append(driver_info)

            return Response({'driver_data': driver_data}, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Drivers not found'}, status=status.HTTP_400_BAD_REQUEST)


class LimoDriverSearchView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')

        filter_conditions = {}

        if name:
            filter_conditions['name__icontains'] = name  # Case-insensitive search

        if email:
            filter_conditions['email__icontains'] = email  # Case-insensitive search

        if phone_number:
            filter_conditions['phone_number__icontains'] = phone_number  # Case-insensitive search

        limo_drivers = LimoDriver.objects.filter(**filter_conditions).values('name', 'email', 'phone_number', 'car_name', 'year_vehicle', 'license_plate', 'car_image', 'driving_license', 'license_plate_image', 'status')

        limo_drivers_list = list(limo_drivers)

        return Response(limo_drivers_list, status=200)


class ChangeDriverStatusView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        new_status = request.data.get('status')

        try:
            # Check if a driver with the provided email and name exists
            driver = LimoDriver.objects.get(email=email, name=name)

            if new_status == 'Approved':
                # Generate a random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                # Send an email with the credentials
                send_mail(
                    'Driver Credentials',
                    f'Your driver credentials: \nEmail: {email}\nPassword: {password}',
                    'Falcondigitalserv@gmail.com',  # Sender's email
                    [email],
                    fail_silently=False,
                )

                # Update the status to 'Approved' and save the generated password
                driver.status = 'Approved'
                driver.password = password

            elif new_status == 'Unapproved':
                # Update the status to 'Unapproved' and clear the password
                driver.status = 'Unapproved'
                driver.password = None

            driver.save()

            return Response({'message': 'Driver status updated'}, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)


class ApprovedDriversView(APIView):
    def get(self, request):
        # Retrieve drivers with status 'Approved'
        approved_drivers = LimoDriver.objects.filter(status='Approved')

        # Serialize the data as needed (using a serializer or manual serialization)
        serialized_drivers = [
            {
                'name': driver.name,
                'email': driver.email,
                'phone_number': driver.phone_number,
                'car_name': driver.car_name,
                'timestamp': driver.timestamp,
                'status': driver.status,
                'active': driver.active,
                # Add other fields you need here
            }
            for driver in approved_drivers
        ]

        return Response({'approved_drivers': serialized_drivers}, status=status.HTTP_200_OK)


class UnApprovedDriversView(APIView):
    def get(self, request):
        # Retrieve drivers with status 'Approved'
        approved_drivers = LimoDriver.objects.filter(status='Unapproved')

        # Serialize the data as needed (using a serializer or manual serialization)
        serialized_drivers = [
            {
                'name': driver.name,
                'email': driver.email,
                'phone_number': driver.phone_number,
                'car_name': driver.car_name,
                'timestamp': driver.timestamp,
                'status': driver.status,
                'active': driver.active,
                # Add other fields you need here
            }
            for driver in approved_drivers
        ]

        return Response({'unapproved_drivers': serialized_drivers}, status=status.HTTP_200_OK)


class UpdateBookingPrice(APIView):
    def post(self, request):
        id = request.data.get('id')
        name = request.data.get('name')
        email = request.data.get('email')
        price = request.data.get('price')

        try:
            # Retrieve the booking based on name and email
            booking = Booking.objects.get(id=id, name=name, email=email)

            # Update the price
            booking.price = price
            booking.save()

            return Response({'message': 'Price updated for the booking'}, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateBookinglink(APIView):
    def post(self, request):
        id = request.data.get('id')
        name = request.data.get('name')
        email = request.data.get('email')
        link = request.data.get('link')

        try:
            # Retrieve the booking based on name and email
            booking = Booking.objects.get(id=id, name=name, email=email)

            # Update the price
            booking.link = link
            booking.save()

            return Response({'message': 'link updated for the booking'}, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

class SendBookingBill(APIView):
    def post(self, request):
        id = request.data.get('id')
        email = request.data.get('email')
        billing_email = request.data.get('billing_email')

        try:
            # Retrieve the booking based on the provided email
            booking = Booking.objects.get(id=id, billing_email=billing_email)

            # Compose the email subject and message
            subject = 'Limo Pro Booking Bill'
            message = f'Your Current Location: {booking.current_location}\n'
            message += f'Your Destination Location: {booking.destination_location}\n'
            message += f'Your Bill Price: {booking.price}\n'
            message += f'Your Bill Link: {booking.link}\n'
            # Add other fields you want in the email message

            # Send the email
            send_mail(subject, message, 'Falcondigitalserv@gmail.com', [billing_email], fail_silently=False)

            booking.payment_status = 'Bill has been sent'
            booking.save()

            # Prepare the OneSignal push notification
            title = 'Check your email for Bill!'
            body = 'Your booking bill has been sent.'
            user = LimoUser.objects.get(email=email)

            # Prepare the OneSignal API request payload
            payload = {
                'app_id': settings.ONESIGNAL_APP_ID,
                'include_player_ids': [user.player_id],
                'headings': {'en': title},
                'contents': {'en': body},
                'data': {},  # Additional data can be added to the notification if needed
                'android_channel_id': 'e5203025-325a-44b3-9e7b-f29f1993db0b',
            }

            # Make the POST request to OneSignal API
            response = requests.post(settings.ONESIGNAL_API_URL, json=payload, headers=settings.ONESIGNAL_API_HEADERS)
            response.raise_for_status()

            notification = Notification(user=user, title=title, body=body)
            notification.save()

            return Response({'message': 'Bill sent to the provided email address'}, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdatePaymentStatus(APIView):
    def post(self, request):
        id = request.data.get('id')
        name = request.data.get('name')
        email = request.data.get('email')
        payment_status = request.data.get('payment_status')

        try:
            # Retrieve the booking based on name and email
            booking = Booking.objects.get(id=id, name=name, email=email)

            # Update the price
            booking.payment_status = payment_status
            booking.save()

            # Send a notification based on payment_status
            if payment_status.lower() == 'paid':
                # Payment is marked as 'paid', send a notification
                user = LimoUser.objects.get(email=email)
                title = 'Payment Received!'
                body = 'Your payment has been received.'

                # Prepare the OneSignal API request payload
                payload = {
                    'app_id': settings.ONESIGNAL_APP_ID,
                    'include_player_ids': [user.player_id],
                    'headings': {'en': title},
                    'contents': {'en': body},
                    'data': {},  # Additional data can be added to the notification if needed
                    'android_channel_id': 'e5203025-325a-44b3-9e7b-f29f1993db0b',
                }

                # Make the POST request to OneSignal API
                response = requests.post(settings.ONESIGNAL_API_URL, json=payload, headers=settings.ONESIGNAL_API_HEADERS)
                response.raise_for_status()

                notification = Notification(user=user, title=title, body=body)
                notification.save()

            return Response({'message': 'Payment status updated for the booking'}, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateRideStatus(APIView):
    def post(self, request):
        id = request.data.get('id')
        name = request.data.get('name')
        email = request.data.get('email')
        ride_status = request.data.get('ride_status')

        try:
            # Retrieve the booking based on name and email
            booking = Booking.objects.get(id=id, name=name, email=email)

            # Update the price
            booking.ride_status = ride_status
            booking.save()

            # Send a notification based on payment_status
            if ride_status.lower() == 'confirmed':
                # ride is marked as 'confirmed', send a notification
                user = LimoUser.objects.get(email=email)
                title = 'Confirmed Ride!'
                body = 'Your Ride has been confirmed.'

                # Prepare the OneSignal API request payload
                payload = {
                    'app_id': settings.ONESIGNAL_APP_ID,
                    'include_player_ids': [user.player_id],
                    'headings': {'en': title},
                    'contents': {'en': body},
                    'data': {},  # Additional data can be added to the notification if needed
                    'android_channel_id': 'e5203025-325a-44b3-9e7b-f29f1993db0b',
                }

                # Make the POST request to OneSignal API
                response = requests.post(settings.ONESIGNAL_API_URL, json=payload, headers=settings.ONESIGNAL_API_HEADERS)
                response.raise_for_status()

                notification = Notification(user=user, title=title, body=body)
                notification.save()

            return Response({'message': 'Ride status updated for the booking'}, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

class GettebView(APIView):
    def get(self, request):
        try:
            # Retrieve all drivers
            drivers = LimoDriver.objects.all()

            # Create a list to store driver details
            drivers_list = []

            # Extract relevant information from each driver
            for driver in drivers:
                driver_details = {
                    'id': driver.id,
                    'name': driver.name,
                    'email': driver.email,
                    'phone_number': driver.phone_number,
                    'total_booking': driver.total_booking,
                    'total_earning': driver.total_earning,
                    'wallet': driver.wallet,
                }
                drivers_list.append(driver_details)

            # Return the list of drivers as a JSON response
            return Response({'drivers': drivers_list}, status=200)
        except LimoDriver.DoesNotExist:
            return Response({'error': 'No drivers found'}, status=404)


class SearchtebView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')

        filter_conditions = {}

        if name:
            filter_conditions['name__icontains'] = name  # Case-insensitive search

        if email:
            filter_conditions['email__icontains'] = email  # Case-insensitive search

        if phone_number:
            filter_conditions['phone_number__icontains'] = phone_number  # Case-insensitive search

        limo_drivers = LimoDriver.objects.filter(**filter_conditions).values('id', 'name', 'email', 'phone_number', 'total_booking', 'total_earning', 'wallet')

        limo_drivers_list = list(limo_drivers)

        return Response(limo_drivers_list, status=200)


class AddToTotalEarning(APIView):
    def post(self, request):
        # Get data from the request
        driver_id = request.data.get('driver_id')
        wallet = request.data.get('wallet')

        try:
            # Retrieve the driver based on the provided driver_id
            driver = LimoDriver.objects.get(id=driver_id)

            # Add the amount to total_earning
            driver.total_earning += float(wallet)

            # Set wallet to 0
            driver.wallet = 0

            # Save the changes
            driver.save()

            return Response({'message': 'Amount added to total earning', 'total_earning': driver.total_earning}, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)

class SignupLimoUserView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        player_id = request.data.get('player_id')

        if not name or not email or not phone_number or not password or not confirm_password:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        if not player_id:
            return JsonResponse({'error': 'playerID is required'}, status=400)

        # Check if the email is already registered
        if LimoUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)

        # Check if the password and confirm_password match
        if password != confirm_password:
            return JsonResponse({'error': 'Password and confirm password do not match'}, status=400)

        # Create a new LimoUser instance and save it to the database
        limo_user = LimoUser(
            name=name,
            email=email,
            phone_number=phone_number,
            password=password,
            confirm_password=confirm_password,
            player_id=player_id
        )
        limo_user.save()

        return JsonResponse({'message': 'LimoUser signup successful'}, status=200)


class LoginLimoUserView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        try:
            user = LimoUser.objects.get(email=email)

            # Check if the provided password matches the user's password
            if user.password != password:
                return JsonResponse({'error': 'Incorrect password'}, status=400)

            # Generate a custom token for the user
            token, created = CustomUserToken.objects.get_or_create(user=user)

            title = 'Login Successful'
            body = 'You have successfully logged in to Limo Pro.'

            # Prepare the OneSignal API request payload
            payload = {
                'app_id': settings.ONESIGNAL_APP_ID,
                'include_player_ids': [user.player_id],
                'headings': {'en': title},
                'contents': {'en': body},
                'data': {},  # Additional data can be added to the notification if needed
                'android_channel_id': 'e5203025-325a-44b3-9e7b-f29f1993db0b',
            }

            # Make the POST request to OneSignal API
            response = requests.post(settings.ONESIGNAL_API_URL, json=payload, headers=settings.ONESIGNAL_API_HEADERS)
            response.raise_for_status()

            notification = Notification(user=user, title=title, body=body)
            notification.save()

            return JsonResponse({'token': token.key, 'email': email}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)


class VerifyUserEmail(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Check if the provided email exists in the LimoUser model
            user = LimoUser.objects.get(email=email)
        except LimoUser.DoesNotExist:
            return JsonResponse({'error': 'Email not found in LimoUser model'}, status=404)

        # Generate OTP
        otp = str(randint(1000, 9999))
        user.otp = otp  # Update the existing user's otp field
        user.save()

        # Send OTP to the user's email
        send_mail(
            'Forgot Password OTP Verification',
            f'Your OTP code for verification is {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        # Return the verified email in the response
        return JsonResponse({'verified_email': email, 'otp': otp}, status=200)


class VerifyOTPFPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Please provide your email and OTP'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = LimoUser.objects.get(email=email)

            # Check if the provided OTP matches the stored OTP
            if user.otp != otp:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

            # You can take further action here, such as marking the email as verified

            return Response({'success': 'OTP has been verified', 'email': email}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not email or not new_password or not confirm_password:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        try:
            # Check if the provided email exists in the LimoUser model
            user = LimoUser.objects.get(email=email)
        except LimoUser.DoesNotExist:
            return JsonResponse({'error': 'Email not found in LimoUser model'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the new password matches the confirm password
        if new_password != confirm_password:
            return JsonResponse({'error': 'New password and confirm password do not match'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the user's password with the new password
        user.password = new_password
        user.confirm_password = new_password  # Update confirm_password as well
        user.save()

        return JsonResponse({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

class CreateBookingView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Retrieve the user based on their email
            user = LimoUser.objects.get(email=email)

            # Retrieve the booking details from the request body
            billing_email = request.data.get('billing_email')
            name = request.data.get('name')
            service_type = request.data.get('service_type')
            vehicle_type = request.data.get('vehicle_type')
            phone_number = request.data.get('phone_number')
            payment_mode = request.data.get('payment_mode')
            current_location = request.data.get('current_location')
            current_coordinates = request.data.get('current_coordinates')
            destination_location = request.data.get('destination_location')
            destination_coordinates = request.data.get('destination_coordinates')
            date = request.data.get('date')
            time = request.data.get('time')
            comment = request.data.get('comment')

            if not email or not name or not billing_email or not service_type or not vehicle_type or not phone_number or not payment_mode or not current_location or not current_coordinates or not destination_location or not destination_coordinates or not date or not time or not comment:
                return JsonResponse({'error': 'All fields are required'}, status=400)

            # Generate a random request_id
            request_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))

            # Create a new booking associated with the user
            booking = Booking(
                billing_email=billing_email,
                name=name,
                service_type=service_type,
                vehicle_type=vehicle_type,
                phone_number=phone_number,
                email=email,
                payment_mode=payment_mode,
                current_location=current_location,
                current_coordinates=current_coordinates,
                destination_location=destination_location,
                destination_coordinates=destination_coordinates,
                date=date,
                time=time,
                comment=comment,
                ride_status='Pending',
                payment_status='Unpaid',
                request_id=request_id,  # Save the generated request_id
            )
            booking.save()

            # Send an email notification
            subject = 'New Booking'
            message = f'There has been a new booking. Check the admin portal.'
            recipient_email = 'marseil5@aol.com'  # Change this to the specific email you want to notify
            send_mail(subject, message, 'Falcondigitalserv@gmail.com', [recipient_email], fail_silently=False)

            # Include request_id in the response
            response_data = {
                'message': 'Booking created successfully',
                'request_id': request_id,
            }

            return JsonResponse(response_data, status=200)

        except LimoUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)


class GetBookingDetailsView(APIView):
    def get(self, request):
        # Retrieve specific fields from the Booking model
        bookings = Booking.objects.values(
            'id',
            'current_location',
            'destination_location',
            'name',
            'phone_number',
            'email',
            'billing_email',
            'payment_mode',
            'ride_status',
            'payment_status',
            'timestamp',
            'driver_name',
            'price'
        )

        # Convert the queryset to a list for better serialization
        booking_list = list(bookings)

        return Response(booking_list)


class CheckBookingView(APIView):
    def post(self, request):
        email = request.data.get('email')

        # Retrieve bookings for the given email
        bookings = Booking.objects.filter(email=email)
        num_bookings = bookings.count()

        if num_bookings == 0:
            # No bookings found for the email
            response_data = {
                'message': 'Proceed to booking',
            }
            return Response(response_data, status=status.HTTP_200_OK)
        elif num_bookings > 1:
            # Multiple bookings found for the email
            response_data = {
                'message': 'More than one booking found. Do you want to make another booking?',
                'bookings_count': num_bookings,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # Single booking found for the email
            response_data = {
                'message': 'You have an existing booking. Would you like to view it?',
                'bookings_count': 1,
            }
            return Response(response_data, status=status.HTTP_200_OK)


class VerifyEmailAndCheckBooking(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Verify if the email exists in the LimoUser model
            user = LimoUser.objects.get(email=email)

            # Check if there is a booking with the provided email and ride_status "Ride has been Started"
            booking = Booking.objects.filter(email=email, ride_status__in=["Ride has been Started", "Customer is in car"]).first()

            if booking:
                response_data = {
                    'ride_status': booking.ride_status,
                    'request_id': booking.request_id
                }
                return Response(response_data, status=200)
            else:
                return Response({'error': 'No booking found with ride_status "Ride has been Started" for the given email.'}, status=404)

        except LimoUser.DoesNotExist:
            return Response({'error': 'Email not found in LimoUser model'}, status=404)

class CalculateEstimatedTime(APIView):
    def post(self, request):
        request_id = request.data.get('request_id')

        try:
            # Retrieve the booking based on the provided request_id
            booking = Booking.objects.get(request_id=request_id)

            # Check if a driver is associated with the booking
            if not booking.driver_name:
                return JsonResponse({'error': 'No driver assigned to this booking'}, status=400)

            # Retrieve driver's details based on the driver's name
            driver_name = booking.driver_name
            try:
                driver = LimoDriver.objects.get(name=driver_name)
            except LimoDriver.DoesNotExist:
                return JsonResponse({'error': 'Driver not found'}, status=404)

            # Retrieve user's current coordinates from the booking
            user_current_coordinates = booking.current_coordinates

            if user_current_coordinates and driver.current_coordinates:
                # Extract latitude and longitude from the coordinates
                user_latitude, user_longitude = user_current_coordinates['current_lat'], user_current_coordinates['current_long']
                driver_latitude, driver_longitude = driver.current_coordinates['current_lat'], driver.current_coordinates['current_long']

                # Calculate the distance between user and driver using the coordinates
                user_location = (user_latitude, user_longitude)
                driver_location = (driver_latitude, driver_longitude)
                distance = geopy.distance.distance(user_location, driver_location).km  # You can use other units as well

                # Calculate estimated time based on distance and speed (e.g., 30 mph)
                estimated_time = distance / 30  # Adjust the speed as needed
                estimated_time_minutes = estimated_time * 60
                estimated_time_formatted = round(estimated_time_minutes, 1)

                # Prepare the response data
                response_data = {
                    'driver name': driver.name,
                    'driver profile pic': driver.driver_profilepic.url if driver.driver_profilepic else None,
                    'rating': driver.rating,  # Assuming you have a 'rating' field in your driver model
                    'phone_number': driver.phone_number,
                    'estimated_time': estimated_time_formatted,
                    'user_current_location': {
                        'location': booking.current_location,
                        'coordinates': user_current_coordinates,
                    },
                    'driver_current_location': {
                        'location': driver.current_location,
                        'coordinates': driver.current_coordinates,
                    },
                    'ride status': booking.ride_status,
                }

                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({'error': 'Coordinates are missing'}, status=400)

        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)


class GetCarInfoView(APIView):
    def post(self, request):
        # Get the request_id from the request data
        request_id = request.data.get('request_id')

        try:
            # Retrieve the booking associated with the request_id
            booking = Booking.objects.get(request_id=request_id)
            driver_name = booking.driver_name

            # Now, use the driver_name to retrieve car information
            try:
                driver = LimoDriver.objects.get(name=driver_name)
                car_info = {
                    'car_name': driver.car_name,
                    'year_vehicle': driver.year_vehicle,
                    'license_plate': driver.license_plate,
                    'car_image': driver.car_image.url if driver.car_image else None,
                }
                return Response(car_info, status=200)
            except LimoDriver.DoesNotExist:
                return Response({'error': 'Driver not found'}, status=404)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=404)


class GetDriverInfoView(APIView):
    def post(self, request):
        # Get the request_id from the request data
        request_id = request.data.get('request_id')

        try:
            # Retrieve the booking associated with the request_id
            booking = Booking.objects.get(request_id=request_id)
            driver_name = booking.driver_name

            # Use the driver_name to fetch driver's rating
            try:
                driver = LimoDriver.objects.get(name=driver_name)
                driver_rating = driver.rating  # Replace 'rating' with the actual field name

                # Calculate the estimated time and distance
                current_coordinates = driver.current_coordinates
                destination_coordinates = booking.destination_coordinates
                if current_coordinates and destination_coordinates:
                    # Calculate the distance in kilometers using geopy library
                    coords_1 = (current_coordinates['current_lat'], current_coordinates['current_long'])
                    coords_2 = (destination_coordinates['dest_lat'], destination_coordinates['dest_long'])
                    distance = geopy.distance.distance(coords_1, coords_2).km
                    estimated_distance_formatted = round(distance, 1)

                    # Assuming an average speed of 30 km/h, calculate the estimated time in hours
                    estimated_time = distance / 30  # Adjust the speed as needed
                    estimated_time_minutes = estimated_time * 60
                    estimated_time_formatted = round(estimated_time_minutes, 1)

                    user_current_location = {
                        'current_location': booking.current_location,
                        'current_coordinates': current_coordinates
                    }

                    user_destination_location = {
                        'destination_location': booking.destination_location,
                        'destination_coordinates': destination_coordinates
                    }

                    return Response({
                        'user_email': booking.email,
                        'driver_name': driver_name,
                        'driver profile pic': driver.driver_profilepic.url if driver.driver_profilepic else None,
                        'rating': driver_rating,
                        'estimated_time': estimated_time_formatted,
                        'estimated_distance_km': estimated_distance_formatted,
                        'current_location': user_current_location,
                        'destination_location': user_destination_location
                    }, status=200)
                else:
                    return Response({'error': 'Coordinates are missing'}, status=400)
            except LimoDriver.DoesNotExist:
                return Response({'error': 'Driver not found'}, status=404)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=404)


class SubmitDriverReview(APIView):
    def post(self, request):
        user_email = request.data.get('user_email')
        driver_name = request.data.get('driver_name')
        rating = request.data.get('rating')
        review = request.data.get('review')

        try:
            # Retrieve the user and driver based on their tokens
            user = LimoUser.objects.get(email=user_email)
            driver = LimoDriver.objects.get(name=driver_name)

            # Create a new driver review
            driver_review = DriverReview(
                driver=driver,
                user=user,
                rating=rating,
                review=review
            )
            driver_review.save()

            return Response({'message': 'Review and rating submitted successfully'}, status=status.HTTP_200_OK)
        except LimoUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)


class GetNotificationsByEmail(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Check if the email belongs to a LimoUser
            user = LimoUser.objects.get(email=email)
            notifications = Notification.objects.filter(user=user).order_by('-timestamp')
        except LimoUser.DoesNotExist:
            return JsonResponse({'error': 'User not found for the provided email'}, status=404)

        # Serialize notifications as a list of dictionaries
        notifications_list = []
        for notification in notifications:
            notifications_list.append({
                'title': notification.title,
                'body': notification.body,
                'timestamp': notification.timestamp
            })

        return JsonResponse(notifications_list, safe=False)


class GetUserinfoDetails(APIView):
    def post(self, request):
        # Get email from the request
        email = request.data.get('email')

        try:
            # Retrieve the user based on the provided email
            user = LimoUser.objects.get(email=email)

            # Extract relevant details
            user_details = {
                'id': user.id,
                'picture': user.user_profilepic.url if user.user_profilepic else None,
                'email': user.email,
                'name': user.name,
                'phone_number': user.phone_number,
                # Add more fields as needed
            }

            return Response(user_details, status=status.HTTP_200_OK)

        except LimoUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateUserDetails(APIView):
    def post(self, request):
        # Get user_id and updated details from the request
        user_id = request.data.get('user_id')
        name = request.data.get('name')
        phone_number = request.data.get('phone_number')
        profilepic = request.FILES.get('profilepic')

        try:
            # Retrieve the user based on the provided user_id
            user = LimoUser.objects.get(id=user_id)

            # Update user details
            user.name = name
            user.phone_number = phone_number
            user.user_profilepic = profilepic

            # Save the changes
            user.save()

            return Response({'message': 'User details updated successfully'}, status=status.HTTP_200_OK)

        except LimoUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class GetUserTravellingHistory(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Verify if the provided driver_email exists in LimoDriver
            user = LimoUser.objects.get(email=email)

            # Retrieve traveling history based on the driver's email
            history_entries = TravellingHistory.objects.filter(email=email).values(
                'driver_name',
                'driver_profilepic',
                'driver_email',
                'current_location',
                'destination_location',
                'price',
                'timestamp'
            )

            # Convert the queryset to a list
            history_list = list(history_entries)

            return Response({'travelling_history': history_list}, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)


class GenerateOTPAPI(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Please provide your email'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email is already registered
        if LimoDriver.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = str(randint(1000, 9999))

        # Save the email and OTP to the model
        driver = LimoDriver(email=email, otp=otp)
        driver.save()

        # Send OTP to the user's email
        send_mail(
            'OTP Verification',
            f'Your OTP is {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({'success': 'OTP has been sent to your email address.', 'email': email, 'otp': otp}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Please provide your email and OTP'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = LimoDriver.objects.get(email=email)

            # Check if the provided OTP matches the stored OTP
            if driver.otp != otp:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

            # You can take further action here, such as marking the email as verified

            return Response({'success': 'OTP has been verified', 'email': email}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)


class LimoDriverSignupView(APIView):
    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name')
        phone_number = request.data.get('phone_number')
        car_name = request.data.get('car_name')
        year_vehicle = request.data.get('year_vehicle')
        license_plate = request.data.get('license_plate')
        player_id = request.data.get('player_id')

        if not email or not name or not phone_number or not car_name or not year_vehicle or not license_plate:
            return Response({'error': 'All are required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email already exists in the model
        driver, created = LimoDriver.objects.get_or_create(email=email)

        # Update the driver's information
        driver.name = name
        driver.phone_number = phone_number
        driver.car_name = car_name
        driver.year_vehicle = year_vehicle
        driver.license_plate = license_plate
        driver.player_id = player_id
        driver.save()

        if created:
            message = 'Driver registered successfully'
        else:
            message = 'Driver information updated'

        return Response({'message': message, 'email': email, 'name': name}, status=status.HTTP_200_OK)


class PostPicturesView(APIView):
    def post(self, request):
        email = request.data.get('email')
        driver_profilepic = request.FILES.get('driver_profilepic')
        car_image = request.FILES.get('car_image')
        driving_license = request.FILES.get('driving_license')
        license_plate_image = request.FILES.get('license_plate')
        car_insurance_image = request.FILES.get('car_insurance_image')

        if not email or not driver_profilepic or not car_image or not driving_license or not license_plate_image or not car_insurance_image:
            return Response({'error': 'Something is missing, please provide all the details.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = LimoDriver.objects.get(email=email)

            # Upload and associate the pictures with the user
            if driver_profilepic:
                driver.driver_profilepic = driver_profilepic
            if car_image:
                driver.car_image = car_image
            if driving_license:
                driver.driving_license = driving_license
            if license_plate_image:
                driver.license_plate_image = license_plate_image
            if car_insurance_image:
                driver.car_insurance_image = car_insurance_image

            driver.save()

            return Response({'message': 'Pictures uploaded successfully', 'email': email}, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_400_BAD_REQUEST)


class LoginLimoDriverView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        try:
            driver = LimoDriver.objects.get(email=email)

            # Check if the provided password matches the user's password
            if driver.password != password:
                return JsonResponse({'error': 'Incorrect password'}, status=400)

            # Generate a custom token for the user
            token, created = CustomDriverToken.objects.get_or_create(driver=driver)

            title = 'Login Successful'
            body = 'You have successfully logged in to Limo Pro.'

            # Prepare the OneSignal API request payload
            payload = {
                'app_id': settings.ONESIGNAL_APP_ID,
                'include_player_ids': [driver.player_id],
                'headings': {'en': title},
                'contents': {'en': body},
                'data': {},  # Additional data can be added to the notification if needed
                'android_channel_id': 'e5203025-325a-44b3-9e7b-f29f1993db0b',
            }

            # Make the POST request to OneSignal API
            response = requests.post(settings.ONESIGNAL_API_URL, json=payload, headers=settings.ONESIGNAL_API_HEADERS)
            response.raise_for_status()

            notification = Notification(driver=driver, title=title, body=body)
            notification.save()

            return JsonResponse({'token': token.key, 'email': driver.email}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)


class ChangeDriverStatus(APIView):
    def post(self, request):
        token_key = request.data.get('token')
        new_active_status = request.data.get('active')  # 'offline' or 'online'

        if not token_key or not new_active_status:
            return Response({'error': 'Please provide token and new active status'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = CustomDriverToken.objects.get(key=token_key)
            driver = LimoDriver.objects.get(id=token.driver_id)

            if new_active_status not in ('offline', 'online'):
                return Response({'error': 'Invalid active status'}, status=status.HTTP_400_BAD_REQUEST)

            driver.active = new_active_status
            driver.save()

            return Response({'message': f'Active status changed to {new_active_status}'}, status=status.HTTP_200_OK)

        except CustomDriverToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateDriverLocation(APIView):
    def post(self, request):
        token_key = request.data.get('token')
        current_location = request.data.get('current_location')
        current_coordinates = request.data.get('current_coordinates')

        if not token_key or not current_location or not current_coordinates:
            return Response({'error': 'Provide all details'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = CustomDriverToken.objects.get(key=token_key)
            driver = LimoDriver.objects.get(id=token.driver_id)

            if current_location:
                driver.current_location = current_location
            if current_coordinates:
                driver.current_coordinates = current_coordinates

            driver.save()

            return Response({'message': 'Driver location updated successfully'}, status=status.HTTP_200_OK)

        except CustomDriverToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)


class GetOnlineDrivers(APIView):
    def get(self, request):
        # Query the database for drivers with active status "online"
        online_drivers = LimoDriver.objects.filter(active='online')

        # Serialize the list of drivers to return in the response
        driver_data = [{'name': driver.name, 'email': driver.email} for driver in online_drivers]

        return Response(driver_data, status=status.HTTP_200_OK)


class UpdateDriverName(APIView):
    def post(self, request):
        id = request.data.get('id')
        name = request.data.get('name')
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        driver_name = request.data.get('driver_name')

        # Query the database to find the booking based on the provided name, phone_number, and email
        try:
            booking = Booking.objects.get(id=id, name=name, phone_number=phone_number, email=email)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update the driver_name in the booking
        booking.driver_name = driver_name
        booking.save()

        return Response({'message': 'Driver name updated in the booking'}, status=status.HTTP_200_OK)


class GetBookingsByDriver(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Retrieve the driver based on the provided email
            driver = LimoDriver.objects.get(email=email)

            # Retrieve confirmed bookings for the driver
            confirmed_bookings = Booking.objects.filter(driver_name=driver.name, ride_status='Confirmed')

            if not confirmed_bookings.exists():
                return Response({'error': 'No confirmed bookings found for the driver'}, status=status.HTTP_404_NOT_FOUND)

            # Prepare the response data
            response_data = []
            for booking in confirmed_bookings:
                user = LimoUser.objects.get(email=booking.email)

                user_coordinates = (
                    float(booking.current_coordinates['current_lat']),
                    float(booking.current_coordinates['current_long'])
                )
                user_destination = (
                    float(booking.destination_coordinates['dest_lat']),
                    float(booking.destination_coordinates['dest_long'])
                )

                driver_coordinates = (
                    float(driver.current_coordinates['current_lat']),
                    float(driver.current_coordinates['current_long'])
                )

                # Calculate pickup and destination distances
                pickup_distance = round(distance.distance(user_coordinates, driver_coordinates).km, 2)
                destination_distance = round(distance.distance(user_coordinates, user_destination).km, 2)

                booking_data = {
                    'request_id': booking.request_id,
                    'name': booking.name,
                    'current_location': booking.current_location,
                    'destination_location': booking.destination_location,
                    'pickup_distance': pickup_distance,
                    'destination_distance': destination_distance,
                    'user_profile_pic': user.user_profilepic.url if user.user_profilepic else None,
                    'date': booking.date,
                    'time': booking.time,
                }

                response_data.append(booking_data)

            return Response(response_data, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)

class CheckOngoingRide(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Retrieve the driver based on the provided email
            driver = LimoDriver.objects.get(email=email)

            # Check if the driver has an ongoing ride
            ongoing_ride = Booking.objects.filter(driver_name=driver.name, ride_status__in=['Ride has been Started', 'Customer is in car']).first()

            if ongoing_ride:
                return Response({'message': 'Complete your previous ride before accepting a new one'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No ongoing rides'}, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)

class StartRide(APIView):
    def post(self, request):
        request_id = request.data.get('request_id')

        try:
            # Retrieve the booking based on the provided request_id
            booking = Booking.objects.get(request_id=request_id)

            # Update the ride_status to "Ride has been Started"
            booking.ride_status = "Ride has been Started"
            booking.save()

            # Send a notification to the user's player_id using OneSignal
            user_email = booking.email
            user = LimoUser.objects.get(email=user_email)

            title = 'Ride has been started'
            body = 'Go to your GPS tracking and live track your driver.'

            # Prepare the OneSignal API request payload
            payload = {
                'app_id': settings.ONESIGNAL_APP_ID,
                'include_player_ids': [user.player_id],
                'headings': {'en': title},
                'contents': {'en': body},
                'data': {},  # Additional data can be added to the notification if needed
                'android_channel_id': 'e5203025-325a-44b3-9e7b-f29f1993db0b',
            }

            # Make the POST request to OneSignal API
            response = requests.post(settings.ONESIGNAL_API_URL, json=payload, headers=settings.ONESIGNAL_API_HEADERS)
            response.raise_for_status()

            return Response({'message': 'Ride has been started. Notification sent to user.', 'email': user_email, 'request_id': request_id}, status=200)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=404)


class DriverpickupCoordinates(APIView):
    def post(self, request):
        request_id = request.data.get('request_id')
        driver_coordinates = request.data.get('driver_coordinates')

        try:
            # Retrieve the booking based on the provided request_id
            booking = Booking.objects.get(request_id=request_id)

            # Retrieve the driver associated with the booking
            driver = LimoDriver.objects.get(name=booking.driver_name)

            # Update the driver's current coordinates
            driver.current_coordinates = driver_coordinates
            driver.save()

            # Calculate the estimated time between driver and user coordinates
            user_coordinates = (
                float(booking.current_coordinates['current_lat']),
                float(booking.current_coordinates['current_long'])
            )
            driver_coordinates = (
                float(driver_coordinates['current_lat']),
                float(driver_coordinates['current_long'])
            )

            # Assuming an average speed of 30 km/h, calculate the estimated time in hours
            distance_km = distance.distance(user_coordinates, driver_coordinates).km
            estimated_time = distance_km / 30  # Adjust the speed as needed
            estimated_time_minutes = round(estimated_time * 60, 2)

            # Prepare the response data
            user = LimoUser.objects.get(email=booking.email)
            response_data = {
                'name': booking.name,
                'user_profilepic': user.user_profilepic.url if user.user_profilepic else None,
                'driver_current_coordinates': driver.current_coordinates,
                'user_current_coordinates': booking.current_coordinates,
                'phone_number': booking.phone_number,
                'estimated_time_minutes': estimated_time_minutes,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateRideStatusafterpickup(APIView):
    def post(self, request):
        request_id = request.data.get('request_id')

        try:
            # Retrieve the booking based on the provided request_id
            booking = Booking.objects.get(request_id=request_id)

            # Update the ride_status to "Customer is in car"
            booking.ride_status = "Customer is in car"
            booking.save()

            return Response({'request_id': request_id, 'ride_status': booking.ride_status}, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

class UpdateDriverdestinationCoordinates(APIView):
    def post(self, request):
        request_id = request.data.get('request_id')
        driver_coordinates = request.data.get('driver_coordinates')

        try:
            # Retrieve the booking based on the provided request_id
            booking = Booking.objects.get(request_id=request_id)

            # Retrieve the driver associated with the booking
            driver = LimoDriver.objects.get(name=booking.driver_name)
            driver_token = CustomDriverToken.objects.get(driver=driver)

            # Update the driver's current coordinates
            driver.current_coordinates = driver_coordinates
            driver.save()

            # Calculate the distance and estimated time between driver and user destination coordinates
            user_destination_coordinates = (
                float(booking.destination_coordinates['dest_lat']),
                float(booking.destination_coordinates['dest_long'])
            )
            driver_coordinates = (
                float(driver_coordinates['current_lat']),
                float(driver_coordinates['current_long'])
            )

            # Calculate the distance in kilometers using geopy library
            distance_km = distance.distance(driver_coordinates, user_destination_coordinates).km

            # Assuming an average speed of 30 km/h, calculate the estimated time in hours
            estimated_time = distance_km / 30  # Adjust the speed as needed
            estimated_time_minutes = round(estimated_time * 60, 2)

            # Prepare the response data
            user = LimoUser.objects.get(email=booking.email)
            response_data = {
                'name': booking.name,
                'user_profilepic': user.user_profilepic.url if user.user_profilepic else None,
                'driver_coordinates': driver.current_coordinates,
                'user_destination_coordinates': booking.destination_coordinates,
                'distance_km': round(distance_km, 2),
                'estimated_time_minutes': estimated_time_minutes,
                'driver_email': driver.email,
                'driver_token': driver_token.key,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)


class EndRide(APIView):
    def post(self, request):
        request_id = request.data.get('request_id')

        try:
            # Retrieve the booking based on the provided request_id
            booking = Booking.objects.get(request_id=request_id)

            # Retrieve the associated driver information
            driver = LimoDriver.objects.get(name=booking.driver_name)

            # Retrieve the driver's token
            driver_token = CustomDriverToken.objects.get(driver=driver)

            # Create a TravellingHistory entry using the booking details
            TravellingHistory.objects.create(
                name=booking.name,
                email=booking.email,
                current_location=booking.current_location,
                destination_location=booking.destination_location,
                date=booking.date,
                time=booking.time,
                driver_name=booking.driver_name,
                driver_email=LimoDriver.objects.get(name=booking.driver_name).email,
                price=booking.price,
                timestamp=booking.timestamp
            )

            # Delete the booking entry
            booking.delete()

            return Response({'message': 'Ride ended successfully', 'driver_email': driver.email, 'driver_token': driver_token.key,}, status=status.HTTP_200_OK)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)


class GetDriverTravellingHistory(APIView):
    def post(self, request):
        driver_email = request.data.get('driver_email')

        try:
            # Verify if the provided driver_email exists in LimoDriver
            driver = LimoDriver.objects.get(email=driver_email)

            # Retrieve traveling history based on the driver's email
            history_entries = TravellingHistory.objects.filter(driver_email=driver_email).values(
                'name',
                'user_profilepic',
                'email',
                'current_location',
                'destination_location',
                'price',
                'timestamp'
            )

            # Convert the queryset to a list
            history_list = list(history_entries)

            return Response({'travelling_history': history_list}, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)


class GetDriverTotalEarning(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Verify if the provided driver_email exists in LimoDriver
            driver = LimoDriver.objects.get(email=email)

            # Get the total earning for the driver
            total_earning = driver.total_earning
            total_bookings = TravellingHistory.objects.filter(driver_email=email).count()

            return Response({'wallet': total_earning, 'total_bookings': total_bookings}, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_driver_image(request, folder, filename):
    # Define the base directory where the driver images are stored
    base_directory = os.path.join(settings.MEDIA_ROOT, 'driver')

    # Construct the path to the image file
    image_path = os.path.join(base_directory, folder, filename)

    # Check if the file exists
    if not os.path.exists(image_path):
        return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

    # Open the file using FileResponse and return it as the response
    return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')


class UserMessageAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        message = request.data.get('message')

        if not email or not message:
            return Response({'error': 'Email and message are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Assuming you have a CustomUser model with email field
            user = LimoUser.objects.get(email=email)
        except LimoUser.DoesNotExist:
            return Response({'error': 'User not found with the provided email'}, status=status.HTTP_404_NOT_FOUND)

        # Create a UserMessage instance
        user_message = Message(user=user, message=message)
        user_message.save()

        subject = 'New Message'
        message = f'There has been a new message from user. Check the admin portal.'
        recipient_email = 'marseil5@aol.com'  # Change this to the specific email you want to notify
        send_mail(subject, message, 'Falcondigitalserv@gmail.com', [recipient_email], fail_silently=False)

        # Return an instant reply
        reply_message = "Thank you for reaching out to us with your message! We appreciate you taking the time to connect, and we want you to know that your feedback, questions, or thoughts are important to us."
        return Response({'message': reply_message}, status=status.HTTP_200_OK)


class GetUserMessagesView(APIView):
    def post(self, request):
        # Get the email from the request body
        email = request.data.get('email')

        try:
            # Retrieve the user based on the provided email
            user = LimoUser.objects.get(email=email)

            # Query the database for messages associated with the user
            user_messages = Message.objects.filter(user=user)

            # Create a list to store message details
            message_list = []

            # Extract relevant information from each message
            for message in user_messages:
                # Only include messages with non-null replies
                if message.reply is not None:
                    message_details = {
                        'message_id': message.id,
                        'message': message.message,
                        'reply': message.reply,
                    }
                    message_list.append(message_details)

            # Return the list of messages and replies as JSON response
            return JsonResponse({'user_messages': message_list}, status=200)

        except LimoUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

class GetUnrepliedMessagesView(APIView):
    def get(self, request):
        # Query the database for messages with null replies
        unreplied_messages = Message.objects.filter(reply__exact='')

        # Create a list to store message details
        message_list = []

        # Extract relevant information from each message
        for message in unreplied_messages:
            message_details = {
                'user_id': message.user.id,
                'message_id': message.id,
                'message': message.message,
                'reply': message.reply,
            }
            message_list.append(message_details)

        # Return the list of unreplied messages as JSON response
        return JsonResponse({'unreplied_messages': message_list})


class PostReplyView(APIView):
    def post(self, request):
        # Get the message ID and reply from the request body
        message_id = request.data.get('message_id')
        user_id = request.data.get('user_id')
        reply = request.data.get('reply')

        try:
            # Retrieve the message from the database
            message = Message.objects.get(id=message_id, user_id=user_id)

            # Update the message with the reply
            message.reply = reply
            message.save()

            user = LimoUser.objects.get(id=user_id)

            title = 'Admin replied'
            body = 'Check message admin has replied you'

            # Prepare the OneSignal API request payload
            payload = {
                'app_id': settings.ONESIGNAL_APP_ID,
                'include_player_ids': [user.player_id],
                'headings': {'en': title},
                'contents': {'en': body},
                'data': {},  # Additional data can be added to the notification if needed
                'android_channel_id': 'e5203025-325a-44b3-9e7b-f29f1993db0b',
            }

            # Make the POST request to OneSignal API
            response = requests.post(settings.ONESIGNAL_API_URL, json=payload, headers=settings.ONESIGNAL_API_HEADERS)
            response.raise_for_status()

            notification = Notification(user=user, title=title, body=body)
            notification.save()

            return JsonResponse({'message': 'Reply added successfully', 'id': user.player_id}, status=200)

        except Message.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)


class GetDriverReviewsView(APIView):
    def get(self, request):
        # Query all driver reviews
        reviews = DriverReview.objects.all()

        # Create a list to store review details
        review_list = []

        # Extract relevant information from each review
        for review in reviews:
            driver_details = {
                'driver_name': review.driver.name,
                'driver_phone_number': review.driver.phone_number,
                'driver_email': review.driver.email,
                'rating': review.rating,
                'review': review.review,
            }
            review_list.append(driver_details)

        # Return the list of reviews as JSON response
        return JsonResponse({'driver_reviews': review_list}, status=200)


class VerifyDriverEmailAndCheckBooking(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Verify if the email exists in the LimoDriver model
            driver = LimoDriver.objects.get(email=email)

            # Get the driver's name
            driver_name = driver.name

            # Check if there is a booking with the provided driver name and ride_status
            booking = Booking.objects.filter(driver_name=driver_name, ride_status__in=["Ride has been Started", "Customer is in car"]).first()

            if booking:
                response_data = {
                    'ride_status': booking.ride_status,
                    'request_id': booking.request_id
                }
                return Response(response_data, status=200)
            else:
                return Response({'error': 'No booking found with the given driver email and ride_status'}, status=404)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Email not found in LimoDriver model'}, status=404)


class GetNotificationsByDriverEmail(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            # Check if the email belongs to a LimoUser
            driver = LimoDriver.objects.get(email=email)
            notifications = Notification.objects.filter(driver=driver).order_by('-timestamp')
        except LimoUser.DoesNotExist:
            return JsonResponse({'error': 'User not found for the provided email'}, status=404)

        # Serialize notifications as a list of dictionaries
        notifications_list = []
        for notification in notifications:
            notifications_list.append({
                'title': notification.title,
                'body': notification.body,
                'timestamp': notification.timestamp
            })

        return JsonResponse(notifications_list, safe=False)


class GetDriverReviews(APIView):
    def post(self, request):
        driver_email = request.data.get('driver_email')

        try:
            # Verify if the provided driver_email exists in LimoDriver
            driver = LimoDriver.objects.get(email=driver_email)

            # Get the reviews for the driver, ordered by timestamp (most recent first)
            driver_reviews = DriverReview.objects.filter(driver=driver).order_by('-timestamp')

            # Serialize reviews as a list of dictionaries
            reviews_list = []
            for review in driver_reviews:
                reviews_list.append({
                    'user_name': review.user.name,
                    'rating': review.rating,
                    'review': review.review,
                    'timestamp': review.timestamp
                })

            return Response({'reviews': reviews_list}, status=status.HTTP_200_OK)

        except LimoDriver.DoesNotExist:
            return Response({'error': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)