from django.shortcuts import render
from .models import Admin, CreatingAdmin
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import views, status
from rest_framework.response import Response
from django.core.mail import send_mail
import random
import string


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


class CreatingAdminView(APIView):
    def post(self, request):
        admin_name = request.data.get('admin_name')
        admin_email = request.data.get('admin_email')
        admin_pnumber = request.data.get('admin_pnumber')

        # Check if admin already exists with the provided admin_name
        try:
            admin = CreatingAdmin.objects.get(admin_name=admin_name)
            return Response({"message": "Admin already exists."}, status=status.HTTP_400_BAD_REQUEST)
        except CreatingAdmin.DoesNotExist:
            # Create new admin object and save it to the database
            admin = CreatingAdmin(admin_name=admin_name, admin_email=admin_email, admin_pnumber=admin_pnumber)
            admin.save()
            return Response({"message": "Admin created successfully"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def admins(request):
    unapproved_admins = CreatingAdmin.objects.filter(approved=False)

    data = []
    for admin in unapproved_admins:
        data.append({
            'admin_name': admin.admin_name,
            'admin_email': admin.admin_email,
            'admin_pnumber': admin.admin_pnumber
        })

    return Response({'unapproved_admins': data})


class ApproveAdminView(views.APIView):
    def post(self, request, *args, **kwargs):
        admin_name = request.data.get('admin_name')
        admin_email = request.data.get('admin_email')
        admin_pnumber = request.data.get('admin_pnumber')
        approved = request.data.get('approved')

        try:
            admin = CreatingAdmin.objects.get(
                admin_name=admin_name,
                admin_email=admin_email,
                admin_pnumber=admin_pnumber
            )

            if approved:
                # Generate a random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

                # Save the admin to the Admin model with the generated password
                from .models import Admin
                admin_record, created = Admin.objects.get_or_create(admin_name=admin_name)
                admin_record.password = password
                admin_record.save()

                # Send an email with the password to the admin_email
                subject = 'Request for Admin Account is APPROVED'
                message = f'Email: {admin_email} \n Password: {password}'
                from_email = 'Falcondigitalserv@gmail.com'  # Replace with your email
                recipient_list = [admin_email]

                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            else:
                # Delete the CreatingAdmin record if not approved
                admin.delete()

            return Response({'message': 'Admin request updated successfully'}, status=status.HTTP_200_OK)

        except CreatingAdmin.DoesNotExist:
            return Response({'error': 'Admin request not found'}, status=status.HTTP_404_NOT_FOUND)