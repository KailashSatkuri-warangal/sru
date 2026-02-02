from .utils import is_it_admin

def user_role(request):
    return {"is_admin": is_it_admin(request.user) if request.user.is_authenticated else False}
