from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login', views.login_view, name='login'),
    path('register-jesuit', views.register_view, name='newAccount'),
    path('<int:user_id>/edit-profile', views.editprofile_view, name='editAccount'),
    path('<int:user_id>/add-viber', views.addviber_view, name='addViber'),
    path('my-profile', views.profile_view, name='myAccount'),
    path('<int:user_id>/<str:viber_id>/delete-viber', views.deleteViber, name='removeViber'),
    path('<int:user_id>/delete-user', views.deleteUser, name='removeUser'),
    path('<int:user_id>/<str:viber_id>/update-viber', views.updateViber, name='updateViber'),
]