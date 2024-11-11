# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import JSONField  
import uuid

class Account(AbstractUser):
    """
    CustomUser extends the AbstractUser model to include additional fields specific to the application's requirements.
    Attributes:
        date_of_birth (DateField): The user's date of birth. Optional.
        institution (CharField): The name of the institution the user is affiliated with. Optional.
        course (CharField): The course the user is enrolled in. Optional.
        year_level (CharField): The user's current year level in their course. Optional.
        programming_experience (CharField): The user's level of programming experience. Optional.
        preferred_languages (JSONField): A JSON field to store the user's preferred programming languages. Optional.
        expectations (TextField): A text field to store the user's expectations. Optional.
    Methods:
        __str__(): Returns the username of the user.
    """
    date_of_birth = models.DateField(null=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    year_level = models.CharField(max_length=50, null=True, blank=True)
    programming_experience = models.CharField(max_length=50, null=True, blank=True)
    preferred_languages = JSONField(null=True, blank=True)
    expectations = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE)
    duration = models.CharField(max_length=50)
    level = models.CharField(max_length=50)
    users = models.ManyToManyField(Account, related_name='enrolled_courses', blank=True)

    def __str__(self):
        return self.title

    def compute_student_score(self, student):
        submissions = Submission.objects.filter(student=student, activity__subtopic__topic__course=self)
        total_score = 0
        total_possible_score = 0
        for submission in submissions:
            total_score += submission.score
            total_possible_score += submission.activity.max_score
        return {"total_score": total_score, "total_possible_score": total_possible_score}
    
    def is_completed_by_user(self, user):
        subtopics = Subtopic.objects.filter(topic__course=self)
        for subtopic in subtopics:
            activities = Activity.objects.filter(subtopic=subtopic)
            for activity in activities:
                if not Submission.objects.filter(student=user, activity=activity).exists():
                    return False
                
                
        return True

class Topic(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, related_name='topics', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Subtopic(models.Model):
    name = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic, related_name='subtopics', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Example(models.Model):
    subtopic = models.ForeignKey(Subtopic, related_name='examples', on_delete=models.CASCADE)
    description = models.TextField()
    code = models.TextField()

    def __str__(self):
        return self.description


class Activity(models.Model):
    """
    Activity model to store multiple questions, options, and correct answers for each subtopic.
    """
    subtopic = models.ForeignKey(Subtopic, related_name='activities', on_delete=models.CASCADE)
    time_limit = models.IntegerField(help_text="Time limit in seconds for the activity")
    activity_code = models.UUIDField(unique=True, editable=False, default = uuid.uuid4())
    quiz_type = models.CharField(max_length=50, help_text="Type of quiz, e.g., 'multiple_choice'")
    max_score = models.IntegerField(default=0, editable=False)
    questions = JSONField(help_text="List of questions with options and correct answers")
    
    def save(self, *args, **kwargs):
        self.max_score = sum(question.get('points', 0) for question in self.questions)
        super(Activity, self).save(*args, **kwargs)

    def __str__(self):
        return f"Activity {self.activity_code} for {self.subtopic.name}"

class Progress(models.Model):
    """
    Progress model to track the completion status of subtopics for each student.
    """
    student = models.ForeignKey(Account, related_name='progress', on_delete=models.CASCADE)
    subtopic = models.ForeignKey(Subtopic, related_name='progress', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    grade = models.FloatField(null=True, blank=True)

    def __str__(self):
        status = 'Completed' if self.completed else 'Incomplete'
        return f"{self.student.username} - {self.subtopic.name} - {status}"
    
class Submission(models.Model):
    """
    Submission model to track the answers submitted by students for each activity.
    """
    student = models.ForeignKey(Account, related_name='submissions', on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='submissions', on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    time_spent = models.IntegerField(help_text="Time spent in seconds to complete the activity")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.activity.subtopic.name}"

    def is_correct(self):
        return self.selected_option == self.activity.correct_answer

    def get_score(self):
        return 1.0 if self.is_correct() else 0.0
    
    
    
class Game(models.Model):
    """
    Game model to store different types of educational games.
    """
    GAME_TYPES = [
        ('multipleChoice', 'Multiple Choice'),
        ('sortableCode', 'Sortable Code'),
        ('tagMatcher', 'Tag Matcher'),
    ]

    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=GAME_TYPES)
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_LEVELS)
    questions = JSONField(null=True, blank=True)
    code_blocks = JSONField(null=True, blank=True)
    tags = JSONField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    
class PlayerProfile(models.Model):
    """
    PlayerProfile model to store the player's profile information
    """
    user = models.OneToOneField(Account, related_name='profile', on_delete=models.CASCADE)
    level = models.CharField(max_length=50, default='Beginner')
    experience_points = models.IntegerField(default=0)
    games_played = models.ManyToManyField(Game, related_name='players', blank=True)
    lives = models.IntegerField(default=3)  
    points = models.IntegerField(default=0) 

    def __str__(self):
        return self.user.username

    def update_experience_points(self, points):
        self.experience_points += points
        if self.experience_points < 0:
            self.experience_points = 0
        self.save()
        return self.experience_points

    def update_level(self):
        if self.experience_points < 100:
            self.level = 'Beginner'
        elif self.experience_points < 200:
            self.level = 'Intermediate'
        else:
            self.level = 'Advanced'
        self.save()
        return self.level

    def add_game(self, game):
        self.games_played.add(game)
        self.save()
        
    def remove_life(self):
        self.lives -= 1
        self.save()
        return self.lives
    
    def add_life(self):
        self.lives += 1
        self.save()
        return self.lives
    
    # a function to generate life every 30 minutes 
    def generate_life(self):
        self.lives += 1
        self.save()
        return self.lives

