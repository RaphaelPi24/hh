from auth.validation import bcrypt
from models import User as UserModel


def check_name_and_password(user_data) -> str:  # не пихать в pydantic бд запросы, pydantic - тупо проверяльщик
    name = user_data.name
    password = user_data.password
    try:
        user = UserModel.get(UserModel.name == name)
    except UserModel.DoesNotExist:
        raise ValueError(f'User with name "{name}" not found.')
    if not bcrypt.check_password_hash(user.password, password):
        raise ValueError('Invalid password.')
    return user
