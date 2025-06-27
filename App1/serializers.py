from rest_framework import serializers
from .models import *



class DepartmentSerialisers(serializers.ModelSerializer):
    class Meta:
        model=Departments
        fields='__all__'

class RoleSerialisers(serializers.ModelSerializer):
    class Meta:
        model=Roles
        fields='__all__'

class UserSerialisers(serializers.ModelSerializer):
    class Meta:
        model=users
        fields='__all__'


class ClientSerializers(serializers.ModelSerializer):
    class Meta:
        model=Clients
        fields='__all__'


class ProjectSerialisers(serializers.ModelSerializer):
    class Meta:
        model=Project
        fields='__all__'

class SupportingImagesSerialisers(serializers.ModelSerializer):
    class Meta:
        model = SupportingImages
        fields = ['image']  



class ConstructionStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionStage
        fields = ['name', 'description', 'house_type', 'sequence']

class HomeSerialisers(serializers.ModelSerializer):
    images = SupportingImagesSerialisers(many=True, write_only=True) 
    construction_stages = ConstructionStageSerializer(many=True, read_only=True) 

    class Meta:
        model = TypesOfHouse
        fields = ['id', 'name', 'description', 'images', 'construction_stages']  

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])  
        house = TypesOfHouse.objects.create(**validated_data)
        for image_data in images_data:
            SupportingImages.objects.create(type_house=house, **image_data)
        return house
    
class leadserialiser(serializers.ModelSerializer):
    class Meta:
        model=leads
        fields='__all__'



class ConstructionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionDetail
        fields = '__all__'

class DesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = '__all__'

class MinutesofMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinutesofMeeting
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class ProjectTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projectteam
        fields = '__all__'

class RequestPasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField()


class VerifyResetCodeSerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)



class ProjectDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project_Documents
        fields = ['id', 'project', 'document', 'name', 'created_at', 'updated_at']

class ChangeOfRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeOfRequest
        fields = '__all__'
