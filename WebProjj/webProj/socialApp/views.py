import json
import datetime as dt
import sys
from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import Http404
from .models import UserProfile, Hobby, User
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import date
from django.utils.dateparse import parse_date
from django.core.mail import send_mail
from django.core import serializers
from django.http import JsonResponse

# decorator
# Check if the user exists or not
def loggedin(view):
    def mod_view(request):
        if 'username' in request.session:
            username = request.session['username']
            try:
                user = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                raise Http404('UserProfile does not exist!')
            return view(request, user)
        else:
            return render(request, 'socialApp/errorLogin.html', {})

    return mod_view

 # view for index/, shows to the user the index page where they can select to register or login
def index(request):

    return render(request, 'socialApp/index.html',)

# loads all the specfied hobbies for registering
def hobbies(request):
    total = Hobby.objects.all()  # Querydict all the hobbies
    qdict = {
        'hobby': total
    }
    print(total)
    return render(request, "socialApp/register.html", context=qdict)

 # register view, is called by the signup page and registers the user with the information entered on the html form
def register(request):
    total = Hobby.objects.all()
    if  request.method =='POST':# Check if the request was POST
        dict = getDict(request) # getDict to return all the values just to clear up extra space
        #dict{username, name, email, hobbies, dataofBirth, gender, image,password }
        user = UserProfile(username=dict[0], name=dict[1], email=dict[2], dob=dict[4], gender=dict[5],image=dict[6])
        try:
            user.set_password(dict[7]) #UserProfile also inherits User so takes the password aspect
            user.save()
            for hobby in dict[3]:  #iterate through m2m hobby field
                hobgob, x = Hobby.objects.get_or_create(name=hobby) #Will only fail if there is a duplicate Hobby existing that is identical so testing to see
                user.hobbies.add(hobgob)
        except IntegrityError:
            return render(request, 'socialApp/register.html', {
                'error_message': "Username " + request.POST['username'] + " already exists!",
                'hobby': total
            })
        context = {
            'usernanme': request.POST['username'],
            'registration': True,
            'hobby': total
        }
        return render(request, 'socialApp/login.html', context)
    return render(request, 'socialApp/register.html', {
                'hobby': total
            })
# Login details are specfied here by firstly checking if the correct fields are given
# and then checking if the user actually exists or not or if the user made a mistake entering their  password.
# On success you will be awarded with a one year cookie
def login(request):
    if not ('username' in request.POST and 'password' in request.POST):
        return render(request,'socialApp/login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        try:
            userProfile = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return render(request,'socialApp/login.html',{
             'error_message2': "Username doesn't exist"
             })
        if userProfile.check_password(password):

            request.session['username'] = username
            request.session['password'] = password
            context = {
                'username': username,
                'loggedin': True
            }
            response = render(request, 'socialApp/homepage.html', context)
            now = dt.datetime.utcnow()
            max_age = 365 * 24 * 60 * 60  # one year
            delta = now + dt.timedelta(seconds=max_age)
            format = "%a, %d-%b-%Y %H:%M:%S GMT"
            expires = dt.datetime.strftime(delta, format)
            response.set_cookie('login', now, expires=expires)
            #set a cookie
            return response
        else:
            return render(request,'socialApp/login.html',{
             'error_message': "Incorrect password, please try again."
             })

def getDict(request):
    u = request.POST['username']
    f = request.POST['name']
    e = request.POST['email']
    g = request.POST['gender']
    h = request.POST.getlist('hobby')
    d = request.POST['dob']
    i = request.FILES.get('image',False)
    p = request.POST['password']
    dict = [u, f, e, h, d, g, i, p]  # creates an array containing all the fields

    return dict

@loggedin # Logs out user by flushing the session which basically means removing the cookies.
def logout(request, user):
    request.session.flush()
    return render(request, 'socialApp/index.html', {
        'logout': "Thanks for logging in! Hope to see you soon :)"
    })

@loggedin
def profile(request, user):#view that will allow the user to edit his profile
    user1 = UserProfile.objects.filter(username=user)  # QuerySet object
    if request.POST:
        if(request.POST['name']):
            user.name = request.POST['name']
        if(request.POST['dob']):
            user.dob = parse_date(request.POST['dob'])
        if(request.POST['gender']):
            user.gender = request.POST['gender']
        if (request.FILES.get('image')):
            user.image = request.FILES.get('image',False)
        if (request.POST['password']):
            user.set_password(request.POST['password'])
        user.hobbies.clear()  # clears hobby
        for hobby in request.POST.getlist('hobby'):
            hob, _ = Hobby.objects.get_or_create(name=hobby)
            user.hobbies.add(hob)
    total = Hobby.objects.all()  # Queryset returned to get all the hobbies
    names = user1[0].hobbies.values_list('name', flat=True)
    names = list(names) # get all hobies in list format to be used later on to iterate through
    user.save()
    user1 = UserProfile.objects.filter(username=user)
    dict = {
        'loggedin': True,
        'email': user1[0].email,
        'password': user1[0].password,
        'username': user1[0].username,
        'name': user1[0].name,
        'age': user1[0].getAge(),
        'hobby': total,
        'image': user1[0].image,
        'gender': user1[0].gender,
        'dob': user1[0].dob,
        'userhobbies': user1[0].hobbies.all(),
        'ownuserhobbies': names,
    }
    return render(request, 'socialApp/profile.html', context=dict)

@loggedin
def homepage(request, user):
    context = {
        "loggedin":True
    }
    return render(request, 'socialApp/homepage.html', context)

@loggedin
def matches(request, user):
    genders = UserProfile.GENDER #used to get the Gender values in models.py
    return render(request, 'socialApp/matches.html',{'genders': genders})

#Ajax poke calls this view in order to send an email to a user
@loggedin
def poke(request, user):
    recipitent = UserProfile.objects.get(pk=request.POST['pk'])
    send_mail(user.name, user.name + ' has poked at you! You should poke them back!', 'networkappsocial@gmail.com', [recipitent.email])
    return JsonResponse({}, safe=False)

#Ajax specfic review that is used to grab all the data to be outputted.
@loggedin
def getMatches(request, user):
    if ("gender" in request.POST and "min_age" in request.POST and "max_age" in request.POST):
        genderRequest = request.POST.get("gender")
        min_age = int(request.POST.get("min_age"))
        max_age = int(request.POST.get("max_age"))
    allUserHobbies = user.hobbies.all()
    userList =[]
    users = UserProfile.objects.all()
    for u in users:
        if u.username!=user.username:
            age = u.getAge()
            if ("gender" in request.POST):
                if (genderRequest!="both" and genderRequest != u.gender):
                    continue
                if (age < min_age or age > max_age):
                    continue
            hobbiesList = []
            similarity = 0;
            currentUserHobbies = u.hobbies.all()
            # Simple algorithm that just counts all the matching hobbies between users
            for hobby in currentUserHobbies:
                hobbiesList.append(hobby.name)
                if hobby in allUserHobbies:
                    similarity = similarity + 1
            gender = u.getGender()
            x = {
                  "name": u.name,
                  "age": age,
                  "gender": gender,
                  "email": u.email,
                  "image": u.image.url,
                  "hobbies": hobbiesList,
                  "similarity": similarity,
                  "pk": u.id
                }
            userList.append(x)
    #Sort the list by the rating to show the most compatible at the start.
    userList = sorted(userList, key = lambda i: i['similarity'], reverse=True)
    return JsonResponse(userList, safe=False)
