from django.shortcuts import render,redirect
import json
from .models import Users,Resume,Job,Applications,Notifications
from .serializers import UsersSerializers,ResumeSerializers,JobSerializers,ApplicationsSerializers,NotificationsSerializers
from rest_framework.views import APIView
from rest_framework.response import Response
import fitz
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
import os 
import requests
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from groq import Groq
from django.conf import settings
client = Groq(api_key=settings.GROQ_API_KEY)

# Health Check API
@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})



class Registerview(APIView):
    def post(self,request):
        serializer=UsersSerializers(data=request.data)
        #Serializer Check whether the client sent all the required fields correctly or not.
        if serializer.is_valid():
            # The Data is Saved into the Database
            # 201 is Good request and 401 is Bad Request
            serializer.save()
            return Response({"message":"Data Saved Successfully"},status=201)
        else:
            return Response({"message":"Not Saved Successfully",
                             "errors":serializer.errors},status=400)    


class Loginview(APIView):
    def post(self,request):
        username=request.data.get("username")
        password=request.data.get("password")
        user=authenticate(
            username=username,
            password=password
        )
        print("Authenticate:",user)
        if user:
            refresh=RefreshToken.for_user(user)
            return Response({"access":str(refresh.access_token),
                             "refresh":str(refresh)})
        else:
            return Response({"message":"Login Failed Due to Invalid Credentials"})

class Resumeview(APIView):
   
    permission_classes=[IsAuthenticated]
   
    
    def post(self,request):
       
        print("POST method called")
        try:
            serializer = ResumeSerializers(data=request.data)

            if serializer.is_valid():
                obj = serializer.save(user=request.user)
                print("Saved:", obj.id)
                return Response({"message": "Saved Successfully"})

            return Response(serializer.errors, status=400)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {
                "error": type(e).__name__,
                "message": str(e)
            },
            status=500
            )

     
        # import traceback
        # print("USER:", request.user)
        # print("USER ID:", request.user.id)
        # serializer=ResumeSerializers(data=request.data)
        # if serializer.is_valid():
        #     try:
        #          obj=serializer.save(user=request.user)
        #          print("Saved ID:", obj.id)
        #          return Response({"message":"Saved Successfully",
        #                      "data":serializer.data})
        #     except Exception:
        #           traceback.print_exc()
        #           raise
            
        # else:
        #     return Response(serializer.errors)    
        
    # 2.Get All resumes And Single Resume:
    # We cannot write Two get Methods inside the Same Class so we can write Like this 
    def get(self,request,pk=None):
        if pk is None:
            resumes=Resume.objects.filter(user=request.user)
            serializer=ResumeSerializers(resumes,many=True)
            return Response({"message":"Fetched Successfully",
                            "data":serializer.data})
        else:

    
            resume=Resume.objects.get(pk=pk,user=request.user)
            serializer=ResumeSerializers(resume)
        
            return Response({"message":"Fetched Successsfully",
                                "data":serializer.data})
        
        
    # 4.Update Resume
    def put(self,request,pk):
        resume=Resume.objects.get(pk=pk,user=request.user)
        serializer=ResumeSerializers(resume,data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message":"Saved Successsfully",
                            "data":serializer.data})
        else:
            return Response({"message":"Fetched Failed",
                            "errors":serializer.errors})
        
    # 5.Delete Resume
    def delete(self,request,pk):
        resume=Resume.objects.get(pk=pk,user=request.user)
        resume.delete()
        return Response({"message":"Deleted Successsfully"})
    
class Jobview(APIView):
    def post(self,request):
        serializer=JobSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Saved Successfully",
                             "data":serializer.data})
        else:
            return Response({"errors":serializer.errors})
    def get(self,request,pk=None):
        if pk is None:
            job=Job.objects.all()
            serializer=JobSerializers(job,many=True)
            return Response({"message":"Fetched Successfully",
                             "data":serializer.data})
        else:
            job=Job.objects.get(pk=pk)
            serializer=JobSerializers(job)
            return self.Response({"message":"Fetched Successfully",
                                  "data":serializer.data})  
    def put(self,request,pk):
        job=Job.objects.get(pk=pk)
        serializer=JobSerializers(job,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Saved Successfully",
                             "data":serializer.data})
        else:
            return Response({"errors":serializer.errors})
    def delete(self,request,pk):
        job=Job.objects.get(pk=pk)
        job.delete()
        return Response({"message":"Deleted Successsfully"})
    
# Dashboard API View
class Dashboard(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        users=Users.objects.count()
        resumes=Resume.objects.filter(user=request.user).count()
        jobs=Applications.objects.filter(user=request.user).count()
        data={
            "total_users":users,
            "total_resumes":resumes,
            "total_jobs":jobs
        }
        return Response({"message":"Dashboard Successfully Fetched",
                         "data":data})
        
    
# Resume Analyzer   
class ResumeAnalyser(APIView):
    def post(self,request):
        resume_id=request.data.get("resume")
        Job_description=request.data.get("Jobdescription")
        
        if not resume_id:
            return Response({"message":"Resume Not Found"})
        if not Job_description:
            return Response({"message":"Job Description Not Found"})
        try:
            resume=Resume.objects.get(id=resume_id)
        except Resume.DoesNotExist:
            return Response({"message":"The Resume is Not Existed"})
        try:
            doc=fitz.open(resume.file.path)
            resume_text=""
            for page in doc:
                resume_text+=page.get_text()
            doc.close()    
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "message": str(e)
            }, status=500)    
        
        Resume_Text=resume_text.lower()
        Job_Text=Job_description.lower()
        prompt = f"""
You are an expert ATS Resume Analyzer.

Compare the following Resume and Job Description.

Resume:
{Resume_Text}

Job Description:
{Job_Text}

Return ONLY valid JSON in this format:

{{
    "ATS_Score": 85,
    "Matched_Skills": ["Python", "Django"],
    "Missing_Skills": ["Docker", "AWS"],
    "Strengths": [
        "Strong Python knowledge",
        "Good Full Stack projects"
    ],
    "Weaknesses": [
        "No Cloud experience"
    ],
    "Suggestions": [
        "Learn Docker",
        "Add AWS projects",
        "Improve resume summary"
    ],
    "Resume_Summary":"Short professional summary"
}}
Return ONLY a valid JSON object.
Do not include any explanation.
Do not include markdown.
Do not wrap the JSON in ```json fences.
"""

        try:

            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )

            ai_response = completion.choices[0].message.content

            result = json.loads(ai_response)

            return Response(result)

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=500
            )

# Email Generation   
class Emailgenerator(APIView):
    def post(self,request):
        User_name=request.data.get("user")
        Receiptent_name=request.data.get("receiptent")
        Company_name=request.data.get("company")
        Role_name=request.data.get("role")
        email_type=request.data.get("type")
        Job_description=request.data.get("Job_description")
        if not Receiptent_name:
            return Response({"message":"Not Found"})
        if not User_name:
            return Response({"message":"Not Found"})
        if not Company_name:
            return Response({"message":"Not Found"})
        if not Role_name:
            return Response({"message":"Not Found"})
        if not email_type:
            return Response({"message":"Not Found"})
        if not Job_description:
            return Response({"message":"Not Found"})
        prompt=f""""
You are an Expert Email Generator
Take the inputs and Generate Professional Email Using These
User_name:
{User_name}   
Receiptent_name:
{Receiptent_name} 
Company_name:
{Company_name}    
Role_name:
{Role_name}
email_type:
{email_type}
Job_description:
{Job_description}

Return Only Valid Json Format Only Like This
{{
   "Email":"Professional Email"
}}

Do not return markdown.
Return only JSON.
"""  
        try:
            completion=client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ],
              temperature=0.5
            )  
            ai_response=completion.choices[0].message.content
            result1=json.loads(ai_response)
            return Response(result1)
        except Exception as e:
            return Response({"message":str(e)})       
class JobTracker(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        serializer=ApplicationsSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"data":serializer.data})
    def get(self,request):
        applications=Applications.objects.filter(user=request.user)
        serializer=ApplicationsSerializers(applications,many=True)
        
        return Response({"Data":serializer.data})    

class JobBoard(APIView):
    def post(self,request):
        Skills=request.data.get("skill")
        Location=request.data.get("Location")
        Freshness=request.data.get("Freshness")
        Freshness=Freshness.lower()
        Experience=request.data.get("Experience")
        # query = f"{Skills} {Experience} jobs in {Location}"
        if str(Experience) == "0":
            query = f"{Skills} Fresher jobs in {Location}"
        elif str(Experience) == "1":
            query = f"{Skills} 1 year experience jobs in {Location}"
        else:
            query = f"{Skills} {Experience} years experience jobs in {Location}"

        url = "https://jsearch.p.rapidapi.com/search-v2"

        querystring = {
            "query": query,
            "country": "in",
            "num_pages": "1",
            "date_posted": Freshness
        }

        headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": "jsearch.p.rapidapi.com",
             "Content-Type": "application/json"
        }
        try:

            response = requests.get(
                url,
                headers=headers,
                params=querystring
            )

            data = response.json()
           
            
            if data.get("status") != "OK":
                return Response(data)

            jobs_data = data.get("data", [])

            jobs = []

            for job in jobs_data:

                # Apply URL
                apply_url = (
                    job.get("job_apply_link")
                    or job.get("applyLink")
                    or job.get("jobUrl")
                    or ""
                )

                if not apply_url:
                    options = job.get("apply_options", [])
                    if options:
                        apply_url = options[0].get("apply_link", "")

                jobs.append({

                    "company":
                        job.get("employer_name")
                        or job.get("companyName")
                        or "",

                    "title":
                        job.get("job_title")
                        or job.get("jobTitle")
                        or "",

                    "location":
                        job.get("job_city")
                        or job.get("locationName")
                        or "",

                    "employment_type":
                        job.get("job_employment_type")
                        or job.get("jobType")
                        or "",

                    "salary":
                        job.get("job_salary_string")
                        or job.get("job_salary")
                        or job.get("salary")
                        or "Not Disclosed",

                    "portal":
                        job.get("job_publisher")
                        or job.get("source")
                        or "",

                    "description":
                        job.get("job_description")
                        or job.get("description")
                        or "",

                    "posted":
                        job.get("job_posted_at")
                        or job.get("postedDate")
                        or "",

                    "apply_url": apply_url

                })

            return Response({
                "recommended_jobs": jobs[:5],
                "all_jobs": jobs
            })

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=500)
       
        
               
class Notification(APIView):
    def post(self,request):
        serializer=NotificationsSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Saved Successfully"})
    def get(self,request):
        Notification=Notification.objects.all()
        serializer=NotificationsSerializers(Notification,many=True)
        return Response(serializer.data)    

class Interview(APIView):
    def post(self,request):
        Role_name=request.data.get("role")
        print(Role_name)
        Company_name=request.data.get("Company_name")
        print(Company_name)  
        prompt=f"""
You are a Expert Interview Questions generator 
Take the Inputs Role_name and Company_name Generate Interview Questions
Role_name:
{Role_name}
Company_name:
{Company_name}
Return only valid JSON format Like This 
{{
   "Questions": [
        "1. What is an Index in MySQL?",
        "2. Explain HTTP Methods.",
        "3. Explain OOPs.",
        "4. ...",
        "5. ...",
        "6. ...",
        "7. ...",
        "8. ...",
        "9. ...",
        "10. ..."
        ]
}}
Generate Top 10 Questions
Use \n between each question.
Do not return markdown.
Return only JSON.
"""  
        try: 
            print("Before Groq")
            completion=client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                "role":"user",
                "content":prompt
                }
            ],
            temperature=0.5

            )
            print("After Groq")
            ai_response=completion.choices[0].message.content
            result=json.loads(ai_response)
            return Response(result)
        except Exception as e:
            return Response({"message":str(e)})

    


class TestGroq(APIView):
    def get(self, request):
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "user",
                        "content": "Say Hello from Groq"
                    }
                ]
            )

            return Response({
                "message": completion.choices[0].message.content
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)



        
        













    

        


