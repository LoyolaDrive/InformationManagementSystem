from django.urls import path
from . import views


app_name = 'loyola'

urlpatterns = [
    path('profiles', views.profiles_view, name='profiles'),
    path('logout/', views.log_out, name='logout'),
    path('dashboard', views.email_view, name='dashboard'),
    path('create-announcement', views.create_announcement, name='newAnnouncement'),
    path('delete-announcement/<int:announcement_id>/', views.delete_announcement, name='delete_announcement'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('add-event/', views.add_event, name='add_event'),
    path('get-events/', views.get_events, name='get_events'),
    path('event/<int:event_id>/', views.get_event_details, name='get_event_details'),
    path('event/<int:event_id>/update/', views.update_event, name='update_event'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('viber-webhook/', views.viber_webhook, name='viber_webhook'),
]
