from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.contrib import messages
from . models import Blog,Profile
from django.db.models import Q
import random

# Create your views here.
def home(request):
    blogs = Blog.objects.all()
    return render(request,'home.html',{"blogs":blogs})

def sigin(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, "Login successfully!")
            return redirect('home')
        else:
            messages.info(request, "Invalid username or password!")
            return redirect('login')
    return render(request, 'login.html')

def sign_up(request):
    if request.method == "POST":
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already used")
            return redirect("signup")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        # Generate OTP
        otp = random.randint(100000, 999999)

        # Store data in session
        request.session['signup_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'password': password1,
            'email': email,
        }
        request.session['otp'] = otp

        # Send OTP email
        send_mail(
            subject="Your OTP for Registration",
            message=f"Your OTP is {otp}",
            from_email=None,
            recipient_list=[email],
        )

        messages.success(request, "OTP sent to your email")
        return redirect("verify_otp")

    return render(request, "signup.html")


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
    # Get only the logged-in user's blogs
    user_blogs = Blog.objects.filter(user=request.user).order_by('-id')
    total_blogs = user_blogs.count()
    data = {
        "total": total_blogs,
        "blogs": user_blogs
    }
    return render(request, "profile.html", {"data": data})

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

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST['otp']
        session_otp = request.session.get('otp')

        if session_otp and entered_otp == str(session_otp):
            data = request.session.get('signup_data')

            User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )

            # Clear session
            request.session.flush()

            messages.success(request, "Signup successful! Please login.")
            return redirect("login")

        else:
            messages.error(request, "Invalid OTP")
            return redirect("verify_otp")

    return render(request, "verify_otp.html")

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    context = {
        'blog': blog
    }
    return render(request, 'blog_detail.html', context)