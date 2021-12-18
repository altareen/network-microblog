import datetime, json
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Person


class CreatePostForm(forms.Form):
    content = forms.CharField(label="Content", widget=forms.TextInput(attrs={'size':80}))

class CreateFollowForm(forms.Form):
    user_id = forms.IntegerField(label="Follow User")

class CreateUnfollowForm(forms.Form):
    user_id = forms.IntegerField(label="Unfollow User")


def index(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            current_user = request.user
            content = form.cleaned_data["content"]

            # Create the relevant database objects and save them
            p = Post(content=content, creator=current_user, timestamp=datetime.datetime.now())
            p.save()
            
            # Redirect user to the All Posts page
            return HttpResponseRedirect(reverse("index"))
        else:
            # If the form is invalid, re-render the page
            return render(request, "index.html", {
                "form": form
            })
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10) # Show 10 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "form": CreatePostForm(),
        "page_obj": page_obj
        #"posts": posts
    })


@csrf_exempt
def update(request):
    # Updating the content must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get contents of submission
    data = json.loads(request.body)
    post_id = int(data.get("post_id", ""))
    content = data.get("submission", "")
    
    # Update the content of the post corresponding to post_id
    Post.objects.filter(id=post_id).update(content=content);

    return JsonResponse({"message": "Update sent successfully."}, status=201)


@csrf_exempt
def appreciate(request):
    # Increasing the quantity of likes must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get contents of submission
    data = json.loads(request.body)
    post_id = int(data.get("post_id", ""))

    # Add the request.user to the batch of people that like this post
    post = Post.objects.get(id=post_id)
    post.likes.add(request.user)
    post.save()

    result = post.likes.count()
    return JsonResponse(result, safe=False)
    #return JsonResponse({"message": "Quantity of likes increased successfully."}, status=201)


@csrf_exempt
def depreciate(request):
    # Decreasing the quantity of likes must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get contents of submission
    data = json.loads(request.body)
    post_id = int(data.get("post_id", ""))

    # Remove request.user from the batch of people that like this post
    post = Post.objects.get(id=post_id)
    post.likes.remove(request.user)
    post.save()

    result = post.likes.count()
    return JsonResponse(result, safe=False)
    #return JsonResponse({"message": "Quantity of likes decreased successfully."}, status=201)


def profile(request, user_id):
    user = User.objects.get(id=user_id)
    posts = Post.objects.filter(creator__id=user_id).order_by('-timestamp')
    paginator = Paginator(posts, 10) # Show 10 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "user_id": user.id,
        "username": user.username,
        "followers": user.followers,
        "following": user.following.all().count(),
        "user_following": [x.user_id for x in User.objects.get(id=request.user.id).following.all()],
        "page_obj": page_obj
        #"posts": posts
    })


def follow(request):
    if request.method == "POST":
        form = CreateFollowForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data["user_id"]
            
            # Increment the quantity of the user_id's followers by one
            User.objects.filter(id=user_id).update(followers=F('followers') + 1)

            # Add the user_id to the request.user.id's batch of people that they're following            
            u = User.objects.get(id=request.user.id)
            p = Person(user_id=user_id)
            p.save()
            u.following.add(p)
            u.save()
            
            # Redirect user to the profile page
            posts = Post.objects.filter(creator__id=user_id).order_by('-timestamp')
            paginator = Paginator(posts, 10) # Show 10 contacts per page.
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            return render(request, "network/profile.html", {
                "user_id": user_id,
                "username": User.objects.get(id=user_id).username,
                "followers": User.objects.get(id=user_id).followers,
                "following": User.objects.get(id=user_id).following.all().count(),
                "user_following": [x.user_id for x in User.objects.get(id=request.user.id).following.all()],
                "page_obj": page_obj
                #"posts": Post.objects.filter(creator__id=user_id).order_by('-timestamp')
            })
        else:
            # If form is invalid, redirect user to the profile page. TODO: This section is not paginated
            return render(request, "network/profile.html", {
                "user_id": request.user.id,
                "username": request.user,
                "followers": User.objects.get(id=request.user.id).followers,
                "following": User.objects.get(id=request.user.id).following.all().count(),
                "user_following": [x.user_id for x in User.objects.get(id=request.user.id).following.all()],
                "posts": Post.objects.filter(creator__id=request.user.id).order_by('-timestamp')
            })

    # Otherwise, redirect user to the profile page. TODO: This section is not paginated
    return render(request, "network/profile.html", {
        "user_id": request.user.id,
        "username": request.user,
        "followers": User.objects.get(id=request.user.id).followers,
        "following": User.objects.get(id=request.user.id).following.all().count(),
        "user_following": [x.user_id for x in User.objects.get(id=request.user.id).following.all()],
        "posts": Post.objects.filter(creator__id=request.user.id).order_by('-timestamp')
    })


def unfollow(request):
    if request.method == "POST":
        form = CreateUnfollowForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data["user_id"]
            
            # Decrement the quantity of the user_id's followers by one
            User.objects.filter(id=user_id).update(followers=F('followers') - 1)

            # Remove the user_id from the request.user.id's batch of people that they're following            
            following = User.objects.get(id=request.user.id).following.all()
            following.get(user_id=user_id).delete()
            
            # Redirect user to the profile page
            posts = Post.objects.filter(creator__id=user_id).order_by('-timestamp')
            paginator = Paginator(posts, 10) # Show 10 contacts per page.
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            return render(request, "network/profile.html", {
                "user_id": user_id,
                "username": User.objects.get(id=user_id).username,
                "followers": User.objects.get(id=user_id).followers,
                "following": User.objects.get(id=user_id).following.all().count(),
                "user_following": [x.user_id for x in User.objects.get(id=request.user.id).following.all()],
                "page_obj": page_obj
                #"posts": Post.objects.filter(creator__id=user_id).order_by('-timestamp')
            })
        else:
            # If form is invalid, redirect user to the profile page. TODO: This section is not paginated
            return render(request, "network/profile.html", {
                "user_id": request.user.id,
                "username": request.user,
                "followers": User.objects.get(id=request.user.id).followers,
                "following": User.objects.get(id=request.user.id).following.all().count(),
                "user_following": [x.user_id for x in User.objects.get(id=request.user.id).following.all()],
                "posts": Post.objects.filter(creator__id=request.user.id).order_by('-timestamp')
            })

    # Otherwise, redirect user to the profile page. TODO: This section is not paginated
    return render(request, "network/profile.html", {
        "user_id": request.user.id,
        "username": request.user,
        "followers": User.objects.get(id=request.user.id).followers,
        "following": User.objects.get(id=request.user.id).following.all().count(),
        "user_following": [x.user_id for x in User.objects.get(id=request.user.id).following.all()],
        "posts": Post.objects.filter(creator__id=request.user.id).order_by('-timestamp')
    })


def following(request):
    user_following =  [x.user_id for x in User.objects.get(id=request.user.id).following.all()]
    posts = Post.objects.filter(creator__id__in=user_following).order_by('-timestamp')
    paginator = Paginator(posts, 10) # Show 10 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        #"posts": posts
        "page_obj": page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
