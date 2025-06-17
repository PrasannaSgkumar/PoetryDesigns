from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Clients, users, SuperAdmin
from django.contrib.auth.hashers import check_password
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser


class SuperAdminLoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data['username']
            password = serializer.validated_data['password']
            try:
                admin = SuperAdmin.objects.filter(username=identifier).first()
                if admin and check_password(password, admin.password):
                    return Response({
                        'status': 'success',
                        'user_type': 'SuperAdmin',
                        'user_id': admin.id,
                        'name': f"{admin.first_name} {admin.last_name}"
                    })
                return Response({'status': 'error', 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data['username']
            password = serializer.validated_data['password']
            try:
                user = users.objects.filter(username=identifier).first()
                if user and check_password(password, user.password):
                    return Response({
                        'status': 'success',
                        'user_type': 'User',
                        'user_id': user.id,
                        'name': f"{user.first_name} {user.last_name}"
                    })
                return Response({'status': 'error', 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientLoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data['username']
            password = serializer.validated_data['password']
            try:
                client = Clients.objects.filter(username=identifier).first()
                if client and check_password(password, client.password):
                    return Response({
                        'status': 'success',
                        'user_type': 'Client',
                        'user_id': client.id,
                        'name': f"{client.first_name} {client.last_name}"
                    })
                return Response({'status': 'error', 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from .models import users, PasswordResetCode
from .serializers import RequestPasswordResetSerializer
import random

class SendPasswordResetCodeAPIView(APIView):
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']

            try:
                user = users.objects.get(username=username)
                code = f"{random.randint(100000, 999999)}"

                # Save or update the code
                PasswordResetCode.objects.update_or_create(
                    username=username,
                    defaults={'code': code}
                )

                # Send email
                send_mail(
                    subject='Your Password Reset Code',
                    message=f'Your password reset verification code is {code}.',
                    from_email='no-reply@example.com',
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                return Response({'status': 'success', 'message': 'Verification code sent to email'}, status=status.HTTP_200_OK)

            except users.DoesNotExist:
                return Response({'status': 'error', 'message': 'Username not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class VerifyAndResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = VerifyResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']

            try:
                otp_entry = PasswordResetCode.objects.get(username=username, code=code)

                if otp_entry.is_expired():
                    return Response({'status': 'error', 'message': 'Verification code expired'}, status=status.HTTP_400_BAD_REQUEST)

                user = users.objects.get(username=username)
                user.password = make_password(new_password)
                user.save()

                otp_entry.delete()

                return Response({'status': 'success', 'message': 'Password reset successful'}, status=status.HTTP_200_OK)

            except PasswordResetCode.DoesNotExist:
                return Response({'status': 'error', 'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
            except users.DoesNotExist:
                return Response({'status': 'error', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class departmentview(APIView):
    def get(self, request):
        try:
            departments = Departments.objects.all()
            serializer = DepartmentSerialisers(departments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching departments: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = DepartmentSerialisers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Department created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid data',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class departmentdetailview(APIView):
    def get(self, request, id):
        try:
            department = get_object_or_404(Departments, id=id)
            serializer = DepartmentSerialisers(department)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error retrieving department: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            department = get_object_or_404(Departments, id=id)
            serializer = DepartmentSerialisers(department, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Department updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid data',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            department = get_object_or_404(Departments, id=id)
            department.delete()
            return Response({
                "status": "success",
                "message": "Department deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Roleview(APIView):
    def get(self, request):
        try:
            roles = Roles.objects.all()
            serializer = RoleSerialisers(roles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching roles: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = RoleSerialisers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Role created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class admindashboard(APIView):
    def get(self, request):
        try:
            user_count=users.objects.all().count()
            project_count=Project.objects.all().count()
            design_phase_count=Project.objects.filter(design_phase_completed=False, construction_phase_completed=False).count()
            construction_phase_count=Project.objects.filter(design_phase_completed=True, construction_phase_completed=False).count()
            return Response({
                'status': 'success',
                'user_count': user_count,
                'project_count': project_count,
                'design_phase_count': design_phase_count,
                'construction_phase_count': construction_phase_count,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching dashboard data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
class Roledetailview(APIView):
    def get(self, request, id):
        try:
            role = get_object_or_404(Roles, id=id)
            serializer = RoleSerialisers(role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error retrieving role: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            role = get_object_or_404(Roles, id=id)
            serializer = RoleSerialisers(role, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Role updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            role = get_object_or_404(Roles, id=id)
            role.delete()
            return Response({
                "status": "success",
                "message": "Role deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class userview(APIView):
    def get(self, request):
        try:
            user = users.objects.all()
            serializer = UserSerialisers(user, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching users: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = UserSerialisers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'User created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class userdetailview(APIView):
    def get(self, request, id):
        try:
            user = get_object_or_404(users, id=id)
            serializer = UserSerialisers(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error retrieving user: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            user = get_object_or_404(users, id=id)
            serializer = UserSerialisers(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "User updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            user = get_object_or_404(users, id=id)
            user.delete()
            return Response({
                "status": "success",
                "message": "User deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class clientview(APIView):
    def get(self, request):
        try:
            client = Clients.objects.all()
            serializer = ClientSerializers(client, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching client data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = ClientSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Client created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class clientdetailview(APIView):
    def get(self, request, id):
        try:
            client = get_object_or_404(Clients, id=id)
            serializer = ClientSerializers(client)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error retrieving client: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            client = get_object_or_404(Clients, id=id)
            serializer = ClientSerializers(client, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Client updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            client = get_object_or_404(Clients, id=id)
            client.delete()
            return Response({
                "status": "success",
                "message": "Client deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class Projectview(APIView):
    def get(self, request):
        try:
            project = Project.objects.all()
            serializer = ProjectSerialisers(project, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching project data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = ProjectSerialisers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Project created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class projectdetailview(APIView):
    def get(self, request, id):
        try:
            project = get_object_or_404(Project, id=id)
            serializer = ProjectSerialisers(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error retrieving project: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            project = get_object_or_404(Project, id=id)
            serializer = ProjectSerialisers(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Project updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            project = get_object_or_404(Project, id=id)
            project.delete()
            return Response({
                "status": "success",
                "message": "Project deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class CreateHouseWithImages(APIView):
    parser_classes = [MultiPartParser]

    def get(self, request):
        try:
            houses = TypesOfHouse.objects.all()
            serializer = HomeSerialisers(houses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching houses: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = {
                'name': request.data.get('name'),
                'description': request.data.get('description'),
                'images': []
            }

            images = []
            for key in request.FILES:
                if key.startswith('images[') and key.endswith('].image'):
                    images.append({'image': request.FILES[key]})

            data['images'] = images

            serializer = HomeSerialisers(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "House and images saved successfully.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "status": "error",
                "message": "Invalid data",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Typesofhouses(APIView):
    def get(self, request, id):
        try:
            house = get_object_or_404(TypesOfHouse, id=id)
            serializer = HomeSerialisers(house)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error retrieving house: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            house = get_object_or_404(TypesOfHouse, id=id)

            # Prepare data for update
            data = {
                'name': request.data.get('name', house.name),
                'description': request.data.get('description', house.description),
                'images': []
            }

            # Handle new images
            images = []
            for key in request.FILES:
                if key.startswith('images[') and key.endswith('].image'):
                    images.append({'image': request.FILES[key]})
            data['images'] = images if images else None  # Only include if there are new images

            # Optional: delete old images if replacing (depends on your logic)
            if images:
                house.images.all().delete()  # This assumes a reverse relationship from `TypesOfHouse` to images.

            serializer = HomeSerialisers(house, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "House and images updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            house = get_object_or_404(TypesOfHouse, id=id)
            house.delete()
            return Response({
                "status": "success",
                "message": "House deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.exceptions import NotFound

class stages(APIView):
    def get(self, request):
        try:
            stages = ConstructionStage.objects.all()
            serializer = ConstructionStageSerializer(stages, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            serializer = ConstructionStageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Details created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class stagesdetails(APIView):
    def get(self, request, id):
        try:
            stages = get_object_or_404(ConstructionStage, id=id)
            serializer = ConstructionStageSerializer(stages)
            return Response(serializer.data)
        except NotFound:
            return Response({
                'status': 'error',
                'message': 'Stage not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, id):
        try:
            stages = get_object_or_404(ConstructionStage, id=id)
            serializer = ConstructionStageSerializer(stages, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Stage Updated Successfully",
                    "data": serializer.data
                })
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, id):
        try:
            project = get_object_or_404(ConstructionStage, id=id)
            project.delete()
            return Response({"message": "Stage deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except NotFound:
            return Response({
                'status': 'error',
                'message': 'Stage not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.exceptions import NotFound

class leadsregistration(APIView):
    def get(self, request):
        try:
            lead = leads.objects.all()
            serializer = leadserialiser(lead, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            serializer = leadserialiser(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Details created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class leadsdetail(APIView):
    def get(self, request, id):
        try:
            lead = get_object_or_404(leads, id=id)
            serializer = leadserialiser(lead)
            return Response(serializer.data)
        except NotFound:
            return Response({
                'status': 'error',
                'message': 'Lead not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, id):
        try:
            lead = get_object_or_404(leads, id=id)
            serializer = leadserialiser(lead, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Lead Updated Successfully",
                    "data": serializer.data
                })
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, id):
        try:
            lead = get_object_or_404(leads, id=id)
            lead.delete()
            return Response({"message": "Lead deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except NotFound:
            return Response({
                'status': 'error',
                'message': 'Lead not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConstructionDetailList(APIView):
    def get(self, request):
        try:
            details = ConstructionDetail.objects.all()
            serializer = ConstructionDetailSerializer(details, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = ConstructionDetailSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Construction detail created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConstructionDetailDetail(APIView):
    def get(self, request, id):
        try:
            detail = ConstructionDetail.objects.get(id=id)
            serializer = ConstructionDetailSerializer(detail)
            return Response(serializer.data)
        except ConstructionDetail.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Construction detail not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            detail = ConstructionDetail.objects.get(id=id)
            serializer = ConstructionDetailSerializer(detail, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Construction detail updated successfully.',
                    'data': serializer.data
                })
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except ConstructionDetail.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Construction detail not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            detail = ConstructionDetail.objects.get(id=id)
            detail.delete()
            return Response({
                'status': 'success',
                'message': 'Construction detail deleted successfully.'
            }, status=status.HTTP_204_NO_CONTENT)
        except ConstructionDetail.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Construction detail not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DesignList(APIView):
    def get(self, request):
        try:
            designs = Design.objects.all()
            serializer = DesignSerializer(designs, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = DesignSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Design created successfully.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DesignDetail(APIView):
    def get(self, request, id):
        try:
            design = Design.objects.get(id=id)
            serializer = DesignSerializer(design)
            return Response(serializer.data)
        except Design.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Design not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            design = Design.objects.get(id=id)
            serializer = DesignSerializer(design, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Design updated successfully.',
                    'data': serializer.data
                })
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Design.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Design not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            design = Design.objects.get(id=id)
            design.delete()
            return Response({
                'status': 'success',
                'message': 'Design deleted successfully.'
            }, status=status.HTTP_204_NO_CONTENT)
        except Design.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Design not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MinutesOfMeetingList(APIView):
    def get(self, request):
        try:
            meetings = MinutesofMeeting.objects.all()
            serializer = MinutesofMeetingSerializer(meetings, many=True)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.data)

    def post(self, request):
        try:
            serializer = MinutesofMeetingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({
                    "status": "error",
                    "message": "Invalid data",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "success",
                "message": "Meeting saved successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

class MinutesOfMeetingDetail(APIView):
    def get(self, request, id):
        try:
            meeting = get_object_or_404(MinutesofMeeting, id=id)
            serializer = MinutesofMeetingSerializer(meeting)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.data)

    def put(self, request, id):
        try:
            meeting = get_object_or_404(MinutesofMeeting, id=id)
            serializer = MinutesofMeetingSerializer(meeting, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({
                    "status": "error",
                    "message": "Invalid data",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "success",
                "message": "Meeting updated successfully",
                "data": serializer.data
            })

    def delete(self, request, id):
        try:
            meeting = get_object_or_404(MinutesofMeeting, id=id)
            meeting.delete()
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": "Meeting deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



class ProjectTeam(APIView):
    def get(self, request):
        projectteam=Projectteam.objects.all()
        serializer=ProjectTeamSerializer(projectteam,many=True)
        return Response(serializer.data)
    
    def post(self, request):
        try:
            serializer = ProjectTeamSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({
                    "status": "error",
                    "message": "Invalid data",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "success",
                "message": "Project team saved successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)


class Projectteamdetails(APIView):
    def get(self, request, id):
        try:
            projectteam = Projectteam.objects.get(id=id)
            serializer = ProjectTeamSerializer(projectteam)
            return Response({
                "status": "success",
                "message": "Project team data fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Projectteam.DoesNotExist:
            return Response({
                "status": "error",
                "message": "No project team found for the given ID"
            }, status=status.HTTP_404_NOT_FOUND)


        
    def put(self, request, id):
        try:    
            # Get the 'project' value from the request data
            project = request.data.get('project')
            
            if not project:
                return Response({
                    "status": "error",
                    "message": "Project ID is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            projectteam=get_object_or_404(Projectteam, id=id)
            serializer=ProjectTeamSerializer(projectteam, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({
                    "status": "error",
                    "message": "Invalid data",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "status": "success",
                "message": "Porject Team updated successfully",
                "data": serializer.data
            })   

    def delete(self, request, id):
        try:
            projectteam = Projectteam.objects.get(id=id)
            projectteam.delete()
            return Response({
                "status": "success",
                "message": "Porject Team deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
