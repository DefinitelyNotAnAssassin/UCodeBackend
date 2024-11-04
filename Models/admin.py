from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from Models.models import Account, Category, Course, Topic, Subtopic, Example, Progress, Activity, Submission


class AccountAdmin(UserAdmin): 
    model = Account
    list_display = ('username', 'email', 'date_of_birth', 'institution', 'course', 'year_level', 'programming_experience', 'preferred_languages', 'expectations')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('date_of_birth', 'institution', 'course', 'year_level', 'programming_experience', 'preferred_languages', 'expectations')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('date_of_birth', 'institution', 'course', 'year_level', 'programming_experience', 'preferred_languages', 'expectations')}),
    ) 
    
admin.site.register(Account, AccountAdmin)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(Subtopic)
admin.site.register(Example)
admin.site.register(Progress)
admin.site.register(Activity)
admin.site.register(Submission)
