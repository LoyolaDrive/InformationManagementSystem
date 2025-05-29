from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import roles, UserRole
from django.contrib.auth.models import User
from LoyolaSystem.models import ViberContact
from .decorators import superuser_required, owner_or_superuser_required

# Create your views here.
@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('loyola:dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('loyola:dashboard')
        else:
            messages.error(request, "Wrong Username and Password. Try Again...")
            return redirect('users:login')

    return render(request, 'users/login.html')

@never_cache
@login_required
@superuser_required
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')

        if password != password1:
            messages.error(request, "Password Mismatch")
            return redirect('users:newAccount')
        
        first_name = request.POST.get('FName')
        last_name = request.POST.get('LName')
        contact = request.POST.get('contact')
        role = request.POST.get('role')

        selected_role = roles.objects.get(role_id=role)
        
        if not User.objects.filter(username=username).exists():
            is_superuser = False
            is_staff = False
            is_active = True

            if selected_role.role_desc.lower() == 'admin':
                is_superuser = True
                is_staff = True
            elif selected_role.role_desc.lower() == 'regular':
                is_active = True

            user = User.objects.create_user(
                username = username,
                password = password,
                first_name = first_name,
                last_name = last_name,
                email = username,
                is_superuser = is_superuser,
                is_staff = is_staff,
                is_active = is_active
            )
            user.save()

            ViberContact.objects.create(
                user = user,
                name = f"{first_name} {last_name}",
                viber_id = contact
            )

            UserRole.objects.create(
                user = user,
                role_id = role
            )
        
            messages.success(request, 'New Jesuit has been registered to Loyola System')
            return redirect('loyola:profiles')
        
        else:
            messages.error(request,'Jesuit has already been registered')
            return redirect('users:newAccount')

    Roles = roles.objects.all()
    return render(request, 'users/register.html', {
        'roles': Roles,
    })

@never_cache
@login_required
@owner_or_superuser_required
def editprofile_view(request, user_id):
    user = User.objects.get(id=user_id)
    currentrole = UserRole.objects.get(user=user_id)


    if request.method == "POST" and request.POST.get('_method') == 'PATCH':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        
        # Check for existing email (excluding current user)
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, f'Email {email} is already registered to another priest!')
            return redirect('users:editAccount', user_id=user_id)
        
        # Check for exact name match in a single row (excluding current user)
        exact_match = User.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name
        ).exclude(id=user.id).first()
        
        if exact_match:
            messages.error(request, f'A priest with the exact same name already exists! (Username: {exact_match.username})')
            return redirect('users:editAccount', user_id=user_id)
            
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        currentrole.role_id = role
        currentrole.save()

        selected_role = roles.objects.get(role_id=role)

        user.is_superuser = False
        user.is_staff = False
        user.is_active = True
        
        if selected_role.role_desc.lower() == "admin":
            user.is_superuser = True
            user.is_staff = True 
        elif selected_role.role_desc.lower() == "regular":
            user.is_active = True

        user.save()

        return redirect('loyola:profiles')

    contacts = ViberContact.objects.filter(user=user)
    Roles = roles.objects.all()
    return render(request, 'users/editprofile.html', {
            'user': user, 
            'contacts': contacts,
            'roles': Roles,
            'currentrole': currentrole
        })

@never_cache
@login_required
@owner_or_superuser_required
def addviber_view(request, user_id):
    if request.method == 'POST':

        user = User.objects.get(id=user_id)
        name = f"{user.first_name} {user.last_name}",
        viber_id = request.POST.get('contact')

        ViberContact.objects.create(
            user = user,
            name = name,
            viber_id = viber_id
        )
    viber= ViberContact.objects.filter(user=user_id)
    return render(request, 'users/addviber.html',{'viber': viber,})

def profile_view(request):
    return render(request, 'users/myprofile.html')

@never_cache
@login_required
@owner_or_superuser_required
def deleteViber(request, user_id, viber_id):
    ViberContact.objects.filter(viber_id=viber_id).delete()
    messages.success(request, "Viber contact deleted successfully.")

    return redirect('users:addViber', user_id=user_id)

@never_cache
@login_required
@superuser_required
def deleteUser(request, user_id):
    User.objects.filter(id=user_id).delete()
    messages.success(request, "Jesuit Account deleted successfully.")

    return redirect('loyola:profiles')

@never_cache
@login_required
@owner_or_superuser_required
def updateViber(request, user_id, viber_id):
    if request.method == 'POST':
        viber_contact = ViberContact.objects.get(viber_id=viber_id)
        new_viber_id = request.POST.get('viber_id')
        viber_contact.viber_id = new_viber_id
        viber_contact.save()
        messages.success(request, "Viber contact updated successfully.")
    
    return redirect('users:addViber', user_id=user_id)
