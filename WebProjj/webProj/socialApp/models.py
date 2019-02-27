from django.db import models
from django.contrib.auth.models import User
from datetime import date



class Hobby(models.Model): #Hobby model to be used in a m2m relationship
	name = models.CharField(max_length=100)
	def __str__(self):
		return self.name

class UserProfile(User): #Inherit from User

	GENDER = (
			('M', 'Male'),
			('F', 'Female'),
		)
	gender = models.CharField(max_length=1,choices=GENDER)
	name = models.CharField(max_length=130)
	image = models.ImageField(upload_to='profile_images')
	dob = models.DateTimeField('Date of Birth')
	hobbies = models.ManyToManyField(Hobby)

	def __str__(self):
		return self.username

	def getAge(self):
		today = date.today()
		return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

	def getGender(self):
		for abbr, gender in self.GENDER:
			if self.gender == abbr:
				return gender
