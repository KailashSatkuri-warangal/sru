from django.contrib.auth.models import User


def is_it_admin(user: User) -> bool:
    """
    Check if a user is an IT Admin.

    Uses is_staff OR membership in the 'IT Admin' group.
    """
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return user.groups.filter(name="IT Admin").exists()

