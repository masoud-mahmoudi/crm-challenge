from .models import User


def create_user(*, email: str, password: str, full_name: str, is_staff: bool = False) -> User:
    user = User(email=email.lower(), full_name=full_name, is_staff=is_staff, is_active=True)
    user.set_password(password)
    user.full_clean()
    user.save()
    return user


def get_or_create_user(*, email: str, password: str, full_name: str, is_staff: bool = False) -> User:
    user = User.objects.filter(email__iexact=email).first()
    if user:
        user.full_name = full_name
        user.is_staff = is_staff
        user.set_password(password)
        user.save(update_fields=["full_name", "is_staff", "password"])
        return user

    return create_user(email=email, password=password, full_name=full_name, is_staff=is_staff)
