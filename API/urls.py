from django.urls import path 
from API import views

urlpatterns = [
    path("", views.index, name="index"),
    
    path("users", views.users, name="users"),
    path("users/<int:pk>", views.user_detail, name="user_detail"),
    path("verifyAuth", views.verify_auth, name="verify_auth"),
    path("login", views.login, name="login"),    
    path("categories", views.categories, name="categories"),
    path("categories/<int:pk>", views.category_detail, name="category_detail"),
    path("enroll", views.enroll, name="enroll"),
    path("courses", views.courses, name="courses"),
    path("courses/<int:pk>", views.course_detail, name="course_detail"),
    path("submitActivity", views.submit_activity, name="submit_activity"),
    path("userCourses", views.user_courses, name="user_courses"),
    path("topics/", views.topics, name="topics"),
    path("topics/<int:pk>", views.topic_detail, name="topic_detail"),
    path("subtopics/", views.subtopics, name="subtopics"),
    path("subtopics/<int:pk>", views.subtopic_detail, name="subtopic_detail"),
    path("examples", views.examples, name="examples"),
    path("examples/<int:pk>", views.example_detail, name="example_detail"),
    path("refreshToken", views.refresh_token, name="refresh_token"),    
    path("activities/<str:activity_code>", views.activities, name="activities"),
    path("checkEligibity/<int:pk>", views.check_eligibility, name="check_eligibility"),
]
