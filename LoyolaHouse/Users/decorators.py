from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def superuser_required(view_func):
    """
    Decorator that checks if the user is a superuser.
    If not, redirects to the dashboard with an error message.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "You don't have permission to access this feature. Only administrators can perform this action.")
            return redirect('loyola:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def owner_or_superuser_required(view_func):
    """
    Decorator that checks if the user is either the owner of the resource or a superuser.
    For views that receive a user_id parameter.
    """
    @wraps(view_func)
    def _wrapped_view(request, user_id, *args, **kwargs):
        if not (request.user.is_superuser or request.user.id == int(user_id)):
            messages.error(request, "You can only edit your own profile unless you're an administrator.")
            return redirect('loyola:dashboard')
        return view_func(request, user_id, *args, **kwargs)
    return _wrapped_view
