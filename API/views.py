from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as login_user
from Models.models import Account, Category, Course, Topic, Subtopic, Example, Submission, Activity, Game, PlayerProfile
from django.db.utils import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

def index(request):
    return JsonResponse({"message": "Welcome to the API!"})

@api_view(['GET', 'POST'])
@csrf_exempt
def users(request):
    if request.method == "GET":
        user = request.user 
        data = { 
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "date_of_birth": user.date_of_birth,
            "institution": user.institution,
            "course": user.course,
            "year_level": user.year_level,
            "programming_experience": user.programming_experience,
                }
        return JsonResponse(data, safe=False)
    elif request.method == "POST":
        data = json.loads(request.body)
        print(data)
        user = Account(
            username=data["email"],
            first_name=data["firstName"],   
            last_name=data["lastName"],
            email=data["email"],
            password=make_password(data["password"]),
            date_of_birth=data["dateOfBirth"],
            institution=data["institution"],
            course=data["course"],
            year_level=data["yearLevel"],
            programming_experience=data["programmingExperience"],
            preferred_languages=data["preferredLanguages"],
            expectations=data["expectations"]
        )
        try:
            user.save()
            
            return JsonResponse({"message": "success"}, safe = False) 
        except IntegrityError:
            return JsonResponse({"error": "User already exists"}, status=400)   
    
    

@csrf_exempt
def user_detail(request, pk):
    try:
        user = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(user)
    elif request.method == "PUT":
        # Handle user update logic here
        pass
    elif request.method == "DELETE":
        user.delete()
        return JsonResponse({"message": "User deleted"}, status=204)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_auth(request):
    if request.user.is_authenticated: 
        user = { 
            "id": request.user.id, 
            "username": request.user.username, 
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email, 
            "date_of_birth": request.user.date_of_birth, 
            "institution": request.user.institution, 
            "course": request.user.course, 
            "year_level": request.user.year_level, 
            "programming_experience": request.user.programming_experience, 
            "preferred_languages": request.user.preferred_languages, 
            "expectations": request.user.expectations 
        }
        return JsonResponse(user, safe=False) 
    else:
        return JsonResponse({"error": "User not authenticated"}, status=400) 
    
   
@csrf_exempt    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_activity(request):
    data = json.loads(request.body)
    print(data)
    activity = Activity.objects.get(activity_code=data["activity_id"])
    submission, created = Submission.objects.update_or_create(
        student=request.user,
        activity=activity,
        defaults = { 
                    'score': data["score"], 
                    'time_spent': data["timeSpent"],
                    }
        
    )
    submission.save()
    
    return JsonResponse({"message": "Submitted Successfully"}, safe=False)

@csrf_exempt  
@api_view(['POST'])
def login(request): 
    data = json.loads(request.body)
    print(data)
    user = get_object_or_404(Account, email=data["email"])   
    if user.check_password(data["password"]):
        login_user(request, user)  
        refresh = RefreshToken.for_user(user)
        user = { 
            "id": user.id, 
            "username": user.username, 
            "first_name": user.first_name,  
            "last_name": user.last_name,
            "email": user.email, 
            "date_of_birth": user.date_of_birth, 
            "institution": user.institution, 
            "course": user.course, 
            "year_level": user.year_level, 
            "programming_experience": user.programming_experience, 
            "preferred_languages": user.preferred_languages, 
            "expectations": user.expectations}
        return JsonResponse({"refresh": str(refresh), "access": str(refresh.access_token), "user": user}, safe=False)
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=400)

@csrf_exempt
def categories(request):
    if request.method == "GET":
        categories = list(Category.objects.all().values())
        return JsonResponse(categories, safe=False)
    elif request.method == "POST":
        # Handle category creation logic here
        pass

@csrf_exempt
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return JsonResponse({"error": "Category not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(category)
    elif request.method == "PUT":
        # Handle category update logic here
        pass
    elif request.method == "DELETE":
        category.delete()
        return JsonResponse({"message": "Category deleted"}, status=204)

@csrf_exempt    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll(request):
    data = json.loads(request.body)
    course = Course.objects.get(pk=data["course_id"])
    user = request.user
    user.enrolled_courses.add(course)
    print(user.enrolled_courses.all())
    return JsonResponse({"message": "Enrolled Successfully"}, safe=False)

@api_view(['GET'])
def courses(request):
    if request.method == "GET":
        
        courses = Course.objects.all()
        data = [] 
        if request.user.is_authenticated:
            for course in courses:
                data.append({ 
                    "id": course.id,
                    "title": course.title,
                    "category": course.category.name,
                    "duration": course.duration,
                    "level": course.level,
                    "enrolled": True if course.users.filter(pk=request.user.id).exists() else False
                             }) 
                
        else:
            for course in courses:
                data.append({ 
                    "id": course.id,
                    "title": course.title,
                    "category": course.category.name,
                    "duration": course.duration,
                    "level": course.level,
                    
                            })
        return JsonResponse(data, safe=False)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
@csrf_exempt
def course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course not found"}, status=404)

    if request.method == "GET":
        data = {
            "id": course.id,
            "title": course.title,
            "category": course.category.name,
            "duration": course.duration,
            "level": course.level,
            "enrolledUsers": course.users.count(),
            "score": course.compute_student_score(request.user),
            "completed": course.is_completed_by_user(request.user),
            "topics": [
            {
                "id": topic.id,
                "name": topic.name,
                "subtopics": [
                {
                    "id": subtopic.id,
                    "name": subtopic.name,
                    "examples": [
                    {
                        "id": example.id,
                        "description": example.description,
                        "code": example.code
                    }
                    for example in subtopic.examples.all()
                    ],
                    "activities": [
                    {
                        "id": activity.activity_code,
                        "questions": activity.questions,
                        "submission": True if activity.submissions.filter(student=request.user).exists() else False
                    }
                    for activity in subtopic.activities.all()
                    ]
                }
                for subtopic in topic.subtopics.all()
                ]
            }
            for topic in course.topics.all()
            ]
        }
        return JsonResponse(data, safe=False)
   
@api_view(['GET'])   
@permission_classes([IsAuthenticated])  
def user_courses(request):
    user = request.user
    courses = user.enrolled_courses.all()
    data = [] 
    for course in courses:
        data.append({ 
            "id": course.id,
            "title": course.title,
            "category": course.category.name,
            "duration": course.duration,
            "level": course.level,
            
                     })
    return JsonResponse(data, safe=False)

@csrf_exempt
def topics(request):
    if request.method == "GET":
        topics = list(Topic.objects.all().values())
        return JsonResponse(topics, safe=False)
    elif request.method == "POST":
        # Handle topic creation logic here
        pass

@csrf_exempt
def topic_detail(request, pk):
    try:
        topic = Topic.objects.get(pk=pk)
    except Topic.DoesNotExist:
        return JsonResponse({"error": "Topic not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(topic)
    elif request.method == "PUT":
        # Handle topic update logic here
        pass
    elif request.method == "DELETE":
        topic.delete()
        return JsonResponse({"message": "Topic deleted"}, status=204)

@csrf_exempt
def subtopics(request):
    if request.method == "GET":
        subtopics = list(Subtopic.objects.all().values())
        return JsonResponse(subtopics, safe=False)
    elif request.method == "POST":
        # Handle subtopic creation logic here
        pass

@csrf_exempt
def subtopic_detail(request, pk):
    try:
        subtopic = Subtopic.objects.get(pk=pk)
    except Subtopic.DoesNotExist:
        return JsonResponse({"error": "Subtopic not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(subtopic)
    elif request.method == "PUT":
        # Handle subtopic update logic here
        pass
    elif request.method == "DELETE":
        subtopic.delete()
        return JsonResponse({"message": "Subtopic deleted"}, status=204)

@csrf_exempt
def examples(request):
    if request.method == "GET":
        examples = list(Example.objects.all().values())
        return JsonResponse(examples, safe=False)
    elif request.method == "POST":
        # Handle example creation logic here
        pass

@csrf_exempt
def example_detail(request, pk):
    try:
        example = Example.objects.get(pk=pk)
    except Example.DoesNotExist:
        return JsonResponse({"error": "Example not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(example)
    elif request.method == "PUT":
        # Handle example update logic here
        pass
    elif request.method == "DELETE":
        example.delete()
        return JsonResponse({"message": "Example deleted"}, status=204)


def refresh_token(request):
    data = json.loads(request.body)
    refresh = RefreshToken(data["refresh"])
    access = str(refresh.access_token)
    return JsonResponse({"access": access, "refresh": data["refresh"]}, safe=False) 

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def activities(request, activity_code):
    try:
        activity = Activity.objects.get(activity_code=activity_code)
    except Activity.DoesNotExist:
        return JsonResponse({"error": "Activity not found"}, status=404)

    data = {
        "id": activity.id,
        "subtopic": activity.subtopic.name,
        "timeLimit": activity.time_limit,
        "activityCode": activity.activity_code,
        "quizType": activity.quiz_type,
        "maxScore": activity.max_score,
        "questions": activity.questions
        
    }
    
    print(data)

    return JsonResponse(data, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_eligibility(request, pk):
    course = Course.objects.get(pk=pk)
    user = request.user

    return JsonResponse({"isEligible": course.is_completed_by_user(user)}, safe=False)

@api_view(['GET'])  
@permission_classes([IsAuthenticated])
def get_player_profile(request):
    user = request.user
    profile, created = PlayerProfile.objects.get_or_create(user=user)
    data = { 
        "points": profile.points
    }
    return JsonResponse(data, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def update_player_profile(request):
    user = request.user
    profile, created = PlayerProfile.objects.get_or_create(user=user)
    data = json.loads(request.body)
    profile.points = data["points"]
    profile.save()
    return JsonResponse({"message": "Profile updated successfully"}, safe=False)

def get_leaderboard(request):
    profiles = PlayerProfile.objects.all().order_by('-points')
    data = [] 
    for profile in profiles:
        data.append({ 
            "user": profile.user.first_name + " " + profile.user.last_name + (" (" + profile.user.username + ")" if profile.user.username else ""), 
            "points": profile.points
                     })
    return JsonResponse(data, safe=False)



@api_view(['GET'])   
@permission_classes([IsAuthenticated])
def get_courses(request): 
    courses = Course.objects.all()
    data = []
    for course in courses:
        course_data = {
            "id": course.id,
            "title": course.title,
            "category": course.category.name,
            "duration": course.duration,
            "level": course.level,
            "topics": []
        }
        for topic in course.topics.all():
            topic_data = {
                "id": topic.id,
                "name": topic.name,
                "subtopics": []
            }
            for subtopic in topic.subtopics.all():
                subtopic_data = {
                    "id": subtopic.id,
                    "name": subtopic.name,
                    "activities": []
                }
                for activity in subtopic.activities.all():
                    activity_data = {
                        "id": activity.id,
                        "activity_code": activity.activity_code,
                        "time_limit": activity.time_limit,
                        "quiz_type": activity.quiz_type,
             
                        "max_score": activity.max_score,
                        "questions": activity.questions
                    }
                    subtopic_data["activities"].append(activity_data)
                topic_data["subtopics"].append(subtopic_data)
            course_data["topics"].append(topic_data)
        data.append(course_data)

    return JsonResponse(data, safe=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    data = json.loads(request.body)
    
    newCourse, _ = Course.objects.update_or_create(
        title=data['title'],
        category=Category.objects.get(name=data['category']),
        duration=data['duration'],
        level=data['level'],
        defaults={
            'title': data['title'],
            'category': Category.objects.get(name=data['category']),
            'duration': data['duration'],
            'level': data['level']
        }
    )
    
    for topic_data in data['topics']:
        newTopic = Topic.objects.create(course=newCourse, name=topic_data['name'])
        
        for subtopic_data in topic_data['subtopics']:
            newSubtopic = Subtopic.objects.create(topic=newTopic, name=subtopic_data['name'])
            
            for activity_data in subtopic_data['activities']:
                Activity.objects.create(
                    subtopic=newSubtopic,
                    activity_code=activity_data['activity_code'],
                    time_limit=activity_data['time_limit'],
                    quiz_type=activity_data['quiz_type'],
                    max_score=activity_data['max_score'],
                    questions=activity_data['questions']
                )
    
    return JsonResponse({"message": "Course created successfully"}, safe=False)
