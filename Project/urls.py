from django.urls import path
from .views import TestGroq
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    Registerview,
    Loginview,
    Resumeview,
    Jobview,
    Dashboard,
    ResumeAnalyser,
    Emailgenerator,
    JobTracker,
    Notification,
    Interview,
    JobBoard
)

urlpatterns = [

    # Authentication
    path("register/", Registerview.as_view(), name="register"),
    path("login/", Loginview.as_view(), name="login"),

    # Resume CRUD
    path("resume/", Resumeview.as_view(), name="resume-list-create"),
    path("resume/<int:pk>/", Resumeview.as_view(), name="resume-detail"),

    # Job CRUD
    path("job/", Jobview.as_view(), name="job-list-create"),
    path("job/<int:pk>/", Jobview.as_view(), name="job-detail"),

    # Dashboard
    path("dashboard/", Dashboard.as_view(), name="dashboard"),

    # Resume Analyzer
    path("resume-analyser/", ResumeAnalyser.as_view(), name="resume-analyser"),

    # Email Generator
    path("email-generator/", Emailgenerator.as_view(), name="email-generator"),

    # Job Tracker
    path("job-tracker/", JobTracker.as_view(), name="job-tracker"),

    # Notifications
    path("notifications/", Notification.as_view(), name="notifications"),

   path("test-groq/", TestGroq.as_view()),

   path("interview/",Interview.as_view(),name="interview"),

   path("jobboard/",JobBoard.as_view(),name="jobboard"),

   path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh")

]