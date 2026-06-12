from django.http import HttpResponseForbidden

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Forbidden")

        if request.user.role != "ADMIN":
            return HttpResponseForbidden("Forbidden")

        return view_func(request, *args, **kwargs)

    return wrapper