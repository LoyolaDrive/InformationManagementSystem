from django.shortcuts import render, redirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.cache import never_cache
from .models import EmailLevel, EmailType, Announcement, ViberContact, Event
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import requests
from .drive_utils import upload_file_to_drive

# Create your views here.
@never_cache
@login_required
def profiles_view(request):
    accounts = User.objects.all()
    contacts = ViberContact.objects.all()
    return render(request, 'system/profiles.html', {
        'accounts': accounts,
        'contacts': contacts,
    })

@login_required
def log_out(request):
    logout(request)
    request.session.flush()
    return redirect('users:login')

@login_required
def email_view(request):
    from datetime import datetime
    from django.db.models import Q
    current_date = datetime.now()
    
    # Get search parameters
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', 'all').lower()
    
    # Start with all announcements ordered by most recent first
    all_announcements = Announcement.objects.all().order_by('-created_at')
    
    # Apply search filter if provided
    if search_query:
        all_announcements = all_announcements.filter(
            Q(subject__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Apply category filter if not 'all'
    if category_filter != 'all' and category_filter in ['national', 'regional', 'global', 'local']:
        all_announcements = all_announcements.filter(
            Q(email_level__level_desc__iexact=category_filter)
        )
    
    # Set up pagination - 10 announcements per page
    page = request.GET.get('page', 1)
    paginator = Paginator(all_announcements, 8)
    
    try:
        announcements = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        announcements = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        announcements = paginator.page(paginator.num_pages)
    
    # Get important events for the current month
    important_events = Event.objects.filter(
        start_date__year=current_date.year,
        start_date__month=current_date.month,
        important=True
    ).order_by('start_date')
    
    # Get normal events for the current month
    normal_events = Event.objects.filter(
        start_date__year=current_date.year,
        start_date__month=current_date.month,
        important=False
    ).order_by('start_date')
    
    return render(request, 'system/archive.html', {
        'announcements': announcements,
        'important_events': important_events,
        'normal_events': normal_events,
        'current_month': current_date.strftime('%B %Y'),
        'search_query': search_query,
        'category_filter': category_filter
    })

@login_required
def create_announcement(request):
    if request.method == 'POST':
        email_level_id = request.POST.get('email_level')
        email_type_id = request.POST.get('email_type')
        subject = request.POST.get('emailSubject')
        raw_content = request.POST.get('emailContent')
        attachment = request.FILES.get('attachment')

        formatted_content = convert_html_to_text(raw_content)

        if email_level_id and email_type_id and subject and raw_content:
            email_level = EmailLevel.objects.get(pk=email_level_id)
            email_type = EmailType.objects.get(pk=email_type_id)
            
            # Create the announcement object
            announcement = Announcement(
                email_level=email_level,
                email_type=email_type,
                subject=subject,
                content=formatted_content
            )
            
            # Handle file attachment if provided
            if attachment:
                try:
                    file_name = attachment.name
                    file_id, file_url = upload_file_to_drive(attachment, file_name)
                    
                    if file_id and file_url:
                        announcement.file_name = file_name
                        announcement.file_url = file_url
                        announcement.drive_file_id = file_id
                        
                        # Add file info to the notification message
                        formatted_content += f"\n\nAttachment: {file_name}\nDownload: {file_url}"
                    else:
                        messages.warning(request, 'Failed to upload the attachment to Google Drive. The announcement was saved without the attachment.')
                except Exception as e:
                    messages.error(request, f'Error uploading file: {str(e)}')
            
            # Send notification and save announcement
            sendNotif(formatted_content)
            announcement.save()
            
            messages.success(request, 'Announcement created successfully!')
            return redirect('loyola:dashboard')


    email_levels = EmailLevel.objects.all()
    email_types = EmailType.objects.all()
    users = User.objects.all()
    viber_numbers = ViberContact.objects.all()

    return render(request, 'system/announcement.html', {
        'email_levels': email_levels,
        'email_types': email_types,
        'users': users,
        'vibers':viber_numbers,
    })

def get_viber_user_ids():
    viber_api_url = "https://chatapi.viber.com/pa/get_account_info"
    headers = {
        "X-Viber-Auth-Token": "547ee03c13b8e3c2-b0bd072aff139c17-1b4114e20b76e52a",
        "Content-Type": "application/json"
    }

    response = requests.post(viber_api_url, headers=headers)
    data = response.json()

    if response.status_code == 200 and "members" in data:
        user_ids = [member["id"] for member in data["members"]]
        return user_ids
    else:
        print("Error fetching Viber user IDs:", data)
        return []

def sendNotif(message):
    user_ids = get_viber_user_ids()  # Fetch user IDs dynamically

    if not user_ids:
        print("No users found to send messages.")
        return None

    viber_api_url = "https://chatapi.viber.com/pa/broadcast_message"
    headers = {
        "X-Viber-Auth-Token": "547ee03c13b8e3c2-b0bd072aff139c17-1b4114e20b76e52a",
        "Content-Type": "application/json"
    }
    
    payload = {
        "broadcast_list": user_ids,  # Use retrieved user IDs
        "min_api_version": 1,
        "sender": {
            "name": "Loyola Bot",
            "avatar": "https://example.com/avatar.jpg"
        },
        "type": "text",
        "text": message
    }

    response = requests.post(viber_api_url, json=payload, headers=headers)
    
    print("Notification Sent:", response.json())  # Debugging
    return response.status_code, response.json()

def convert_html_to_text(raw_html):
    import re
    if not raw_html:
        return '' 
    
    raw_html = raw_html.replace('&nbsp;', ' ')
    raw_html = re.sub(r'<br\s*/?>', '\n', raw_html)  # Convert <br> to \n
    text_only = strip_tags(raw_html)  # Remove remaining tags
    return text_only

#for ttesting purposes only

def set_webhook(webhook_url):
    viber_api_url = "https://chatapi.viber.com/pa/set_webhook"
    headers = {
        "X-Viber-Auth-Token": "547ee03c13b8e3c2-b0bd072aff139c17-1b4114e20b76e52a",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": webhook_url,
        "event_types": ["delivered", "seen", "failed", "subscribed", "unsubscribed", "conversation_started"]
    }
    
    response = requests.post(viber_api_url, json=payload, headers=headers)
    print("Webhook setup response:", response.json())
    return response.status_code, response.json()


@csrf_exempt
def viber_webhook(request):
    if request.method == 'POST':
        # Log the incoming request for debugging
        print("Received webhook event:", request.body)

        try:
            # Parse the JSON payload
            data = json.loads(request.body)

            # Handle different event types
            event_type = data.get("event")
            if event_type == "webhook":
                print("Validation request received from Viber API.")
            elif event_type == "message":
                print("Message received:", data.get("message"))
            elif event_type == "subscribed":
                print("User subscribed:", data.get("user"))
            elif event_type == "unsubscribed":
                print("User unsubscribed:", data.get("user"))

            # Respond to the Viber API with a 200 OK status
            return HttpResponse(status=200)

        except Exception as e:
            print("Error processing webhook event:", str(e))
            return HttpResponse(status=400)  # Bad Request

    return HttpResponse(status=405)  # Method Not Allowed for non-POST requests
def get_one_viber_user_id(index=0):
    """
    Fetches all user IDs and returns the user ID at the specified index.
    Returns None if no user IDs are found or if the index is out of range.
    """
    user_ids = get_viber_user_ids()

    if user_ids and 0 <= index < len(user_ids):
        return user_ids[index]
    else:
        print("No user ID found at the specified index.")
        return None

def send_individual_message():
    user_ids = get_one_viber_user_id()
    user = user_ids[0]
    viber_api_url = "https://chatapi.viber.com/pa/send_message"
    headers = {
        "X-Viber-Auth-Token": "YOUR_PUBLIC_ACCOUNT_TOKEN",  # Replace with your token
        "Content-Type": "application/json"
    }

    payload = {
        "receiver": user,  # Unique ID of the recipient
        "type": "text",
        "text": "testing"  # The message you want to send
    }

    response = requests.post(viber_api_url, json=payload, headers=headers)
    print("Message Sent:", response.json())
    return response.status_code, response.json()

@login_required
def delete_announcement(request, announcement_id):
    try:
        announcement = Announcement.objects.get(pk=announcement_id)
        announcement.delete()
        return redirect('loyola:dashboard')
    except Announcement.DoesNotExist:
        return redirect('loyola:dashboard')

@login_required
def calendar_view(request):
    return render(request, 'system/calendar.html')

@login_required
def add_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        important = request.POST.get('important') == 'on'
        event = Event.objects.create(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date if end_date else None,
            important=important,
            created_by=request.user
        )

        return redirect('loyola:calendar')
    return redirect('loyola:calendar')

@login_required
def get_events(request):
    events = Event.objects.all()
    event_list = [{
        'id': event.id,
        'title': event.title,
        'start': event.start_date.isoformat(),
        'end': event.end_date.isoformat() if event.end_date else None,
        'description': event.description,
        'important': event.important
    } for event in events]
    return JsonResponse(event_list, safe=False)

@login_required
def get_event_details(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
        data = {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat() if event.end_date else None,
            'created_by': event.created_by.username,
            'important': event.important
        }
        return JsonResponse(data)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

@login_required
def delete_event(request, event_id):
    if request.method == 'POST':
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def update_event(request, event_id):
    if request.method == 'POST':
        try:
            event = Event.objects.get(pk=event_id)
            event.title = request.POST.get('title')
            event.description = request.POST.get('description')
            event.start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            event.end_date = end_date if end_date else None
            event.important = request.POST.get('important') == 'on'
            event.save()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        viber = request.POST.get('viber')
        
        # Check for existing email (excluding current user)
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, f'Email {email} is already registered to another priest!')
            return redirect('loyola:edit_profile')
            
        # Check for existing viber contact (excluding current user)
        if viber and ViberContact.objects.filter(viber_id=viber).exclude(user=request.user).exists():
            messages.error(request, f'Viber contact {viber} is already registered to another priest!')
            return redirect('loyola:edit_profile')
            
        # Check for exact name match in a single row (excluding current user)
        exact_match = User.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name
        ).exclude(id=request.user.id).first()
        
        if exact_match:
            messages.error(request, f'A priest with the exact same name already exists! (Username: {exact_match.username})')
            return redirect('loyola:edit_profile')
        
        # Update user information
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        # Update or create viber contact
        ViberContact.objects.update_or_create(
            user=user,
            defaults={'viber_id': viber, 'name': f'{first_name} {last_name}'}
        )
        
        # Handle password change if requested
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                # Update session to prevent logout
                update_session_auth_hash(request, user)
                messages.success(request, 'Your profile was successfully updated!')
            else:
                messages.error(request, 'Passwords do not match!')
                
        return redirect('loyola:edit_profile')
    
    # Get all user's viber contacts
    viber_contacts = ViberContact.objects.filter(user=request.user)
        
    return render(request, 'system/edit_profile.html', {
        'user': request.user,
        'viber_contacts': viber_contacts
    })