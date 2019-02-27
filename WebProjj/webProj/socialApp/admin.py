from django.contrib import admin

from .models import UserProfile, Hobby
# Makes sure not to create a user in admin without a proper interface
class UserProfileAdmin(admin.ModelAdmin):
    fields = ('username','email','password','image','name', 'gender','dob','hobbies')


admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(Hobby)
