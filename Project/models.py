from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Users(AbstractUser):
    full_name=models.CharField(max_length=20)
    # email=models.EmailField()
    # Password=models.CharField(max_length=20)
    experience_level=models.CharField(max_length=10)
    prefered_location=models.CharField(max_length=10)
    def __str__(self):
        return self.full_name
    
class Resume(models.Model):
    user=models.ForeignKey('Users',on_delete=models.CASCADE) 
    file=models.FileField(upload_to='resumes/')
    parsed_text=models.TextField(blank=True,null=True)
    version_no=models.IntegerField(default=1)
    is_primary=models.BooleanField(default=True)
    uploaded_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f" {self.user.full_name}-Resume{self.version_no}"

class Job(models.Model):
    user=models.ForeignKey('Users',on_delete=models.CASCADE)  
    title=models.CharField(max_length=15)
    raw_text=models.TextField()
    source=models.CharField(max_length=10)
    created_at=models.DateTimeField()
    def __str__(self):
        return f"{self.user.full_name}-{self.title}"
    
class ResumeSources(models.Model):
    resume=models.ForeignKey('Resume',on_delete=models.CASCADE)  
    job_description=models.ForeignKey('Job',on_delete=models.CASCADE)
    macth_score=models.DecimalField(max_digits=5,decimal_places=5)
    missing_skills=models.CharField(max_length=50)
    suggestions=models.TextField()
    created_at=models.DateTimeField()
    def __str__(self):
        return f"{self.resume.file}-{self.macth_score}" 
    
class Companies(models.Model):
    name=models.CharField(max_length=10)
    website=models.CharField(max_length=10)
    logo_url=models.CharField(max_length=20)
    def __str__(self):
        return self.name

class Jobposts(models.Model):
    company=models.ForeignKey('Companies',on_delete=models.CASCADE)
    title=models.CharField(max_length=10)
    descriptiom=models.TextField()
    location=models.CharField(max_length=10)
    source_portal=models.CharField(max_length=10)
    source_url=models.CharField(max_length=10)
    posted_date=models.DateTimeField()
    skills_required=models.CharField(max_length=10)
    def __str__(self):
        return f"{self.company.name}-{self.title}-{self.location}"

class Applications(models.Model):
    user=models.ForeignKey('Users',on_delete=models.CASCADE)
    # job=models.ForeignKey('Jobposts',on_delete=models.CASCADE)
    company_name=models.CharField(max_length=50)
    role=models.CharField(max_length=50)
    location=models.CharField(max_length=20)
    # resume=models.ForeignKey('Resume',on_delete=models.CASCADE)
    applied_date=models.DateField(default=timezone.now)
    status=models.CharField(max_length=20,default="Applied")
    # notes=models.TextField()
    def __str__(self):
        return f"{self.user.full_name}-{self.company_name}"
    
class Emails(models.Model):
    user=models.ForeignKey('Users',on_delete=models.CASCADE)
    application=models.ForeignKey('Applications',on_delete=models.CASCADE)
    email_type=models.CharField(max_length=10)
    generated_content=models.TextField()
    created_at=models.DateTimeField()
    def __str__(self):
        return f"{self.user.full_name}-{self.application.company}"
    
class Notifications(models.Model):
    user=models.ForeignKey('Users',on_delete=models.CASCADE)
    type=models.CharField(max_length=10)
    message=models.TextField()
    is_read=models.BooleanField(default=False)
    trigger_date=models.DateTimeField()
    def __str__(self):
        return f"{self.user.full_name}-{self.type}-{self.trigger_date}"
    

    







