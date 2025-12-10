from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from . models import Blog,Profile
from django.db.models import Q

# Create your views here.
def home(request):
    blogs = Blog.objects.all()
    return render(request,'home.html',{"blogs":blogs})

def sigin(request):
    if request.method == "POST":
        username = request.POST['name']
        password = request.POST['password']
        user = authenticate(request,username = username,password = password)
        if user:
            login(request,user)
            messages.info(request,"Login successfully!")
            return redirect('home')
        else:
            messages.info(request,"Invalid username or password!")
            return redirect('login')
    return render(request,'login.html')

def sign_up(request):
    if request.method == "POST":
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        password1 = request.POST['password1']
        password = request.POST['password2']
        email = request.POST['email']
        if User.objects.filter(username=username).exists():
            messages.info(request,"username already exist")
            return redirect("signup")

        elif User.objects.filter(email=email).exists():
            messages.info(request,"Email already used")
            return redirect("signup")

        if password1 == password :
            if password:
                User.objects.create_user(
                    username = username,
                    password = password,
                    first_name = first_name,
                    last_name = last_name,
                    email = email
                )
                if request.user:
                    return redirect('home')
                return redirect('login')
            return render(request,'sigup.html')

    return render(request,'sigup.html')

@login_required
def add_blog(request):
    if request.method =="POST":
        name = request.POST["name"]
        messeage = request.POST["messeage"]
        image = request.FILES.get('image')

        blog = Blog(
            user = request.user,
            name =name,
            image = image,
            messeage =messeage
        )
        blog.save()
        return redirect('gallery')

    return render(request,'blog.html')

@login_required
def gallery(request):
    blogs = Blog.objects.all()
    return render(request,"gallery.html",{'blogs':blogs})

@login_required
def user_logout(request):
    logout(request)

    return redirect("home")

@login_required
def edit(request,id):
    blog = Blog.objects.filter(id = id).first()
    if request.method =="POST":
        name = request.POST["name"]
        messeage = request.POST["messeage"]
        image = request.FILES.get('image')

        if image:
            blog.image = image
        blog.name = name
        blog.messeage = messeage
        blog.save()
        return redirect('gallery')
    
    return render(request,'edit.html',{"blog":blog})

@login_required
def delete(request,id):
    blog = Blog.objects.filter(id = id).first()
    blog.delete()

    return redirect('gallery')

@login_required
def profile(request):
    user = request.user
    blogs = Blog.objects.all()
    total_blogs = 0;
    for blogs in blogs:
        if request.user == blogs.user:
            total_blogs = total_blogs +1
    data = {"total":total_blogs,
            }
    
    return render(request,"profile.html",{"data":data})

def forget(request):
    if request.method == "POST":
        email = request.POST["email"]
        if User.objects.filter(email = email).exists():
            print("user exists")
    return render(request,"forget.html")

def search(request):
    quary = request.GET.get("search","")
    results = Blog.objects.filter(Q(name__icontains = quary) | Q(user__username__icontains = quary))
    if results:
         messages.info(request,"Searched Blog")
    else:
        messages.info(request,"No result found")
    return render(request,"search.html",{"results":results})

def edit_profile(request,id):
    user = User.objects.filter(id=id).first()
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    if request.method == "POST":
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            dob = request.POST.get('birthday')
            image = request.FILES.get('profile_image')  # Corrected: request.FILES, not request.FILE

            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email

            # Update profile fields
            profile = user.profile
            profile.dob = dob
            if image:
                profile.profile_image = image

            user.save()
            profile.save()  # Save profile explicitly

            return redirect('profile')
    return render(request,"edit_profile.html",{"user":user})