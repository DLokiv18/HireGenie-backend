from rest_framework import serializers
from.models import Users,Resume,Job,ResumeSources,Companies,Jobposts,Applications,Emails,Notifications

class UsersSerializers(serializers.ModelSerializer):
    class Meta:
        model=Users
        fields = [
            "username",
            "full_name",
            "email",
            "password",
            "experience_level",
            "prefered_location",
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }
    def create(self, validated_data):
        password = validated_data.pop("password")

        user = Users(**validated_data)
        user.set_password(password)   # Hashes the password
        user.save()

        return user    

class ResumeSerializers(serializers.ModelSerializer):
    class Meta:
        model=Resume
        fields="__all__"
        read_only_fields = ["user"]
        
class  JobSerializers(serializers.ModelSerializer):
    class Meta:
        model=Job
        fields="__all__"  

class  ResumeSourcesSerializers(serializers.ModelSerializer):
    class Meta:
        model=ResumeSources
        fields="__all__"

class  CompaniesSerializers(serializers.ModelSerializer):
    class Meta:
        model=Companies
        fields="__all__"

class JobpostsSerializers(serializers.ModelSerializer):
    class Meta:
        model=Jobposts
        fields="__all__"

class ApplicationsSerializers(serializers.ModelSerializer):
    class Meta:
        model=Applications
        fields="__all__"
        read_only_fields = ["user"]

class  EmailsSerializers(serializers.ModelSerializer):
    class Meta:
        model=Emails
        fields="__all__"

class NotificationsSerializers(serializers.ModelSerializer):
    class Meta:
        model=Notifications
        fields="__all__"

        





