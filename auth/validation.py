import re

import bcrypt

from pydantic import BaseModel, field_validator

from models import User as UserModel
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class General(BaseModel):
    name: str
    password: str

    @field_validator('name', mode='before')
    @classmethod
    def ensure_str(cls, name):
        if isinstance(name, list):
            return name[0]
        return name

    @field_validator('password', mode='before')
    @classmethod
    def ensure_str(cls, password):
        if isinstance(password, list):
            return password[0]
        return password

    @field_validator('password')
    @classmethod
    def password_min_len(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters')
        return password

    @field_validator('password')
    @classmethod
    def password_max_len(cls, password: str) -> str:
        if len(password) > 16:
            raise ValueError('Password must be less than 16 characters')
        return password

    @field_validator('password')
    @classmethod
    def password_digital(cls, password: str) -> str:
        reg = r'\d'
        if re.search(reg, password) is None:
            raise ValueError('Password must contain at least one number')
        return password

    @field_validator('password')
    @classmethod
    def password_letters(cls, password: str) -> str:
        reg = r'[A-Za-z]'
        if re.search(reg, password) is None:
            raise ValueError('Password must contain at least one letter')
        return password


class Register(General):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, email: str) -> str:
        if '@' not in email:
            raise ValueError('Email must contain @')
        return email

    @field_validator('email')
    @classmethod
    def exists_email(cls, email: str) -> str:
        email_exists = UserModel.select().where(UserModel.email == email).exists()
        if email_exists:
            raise ValueError('Email already exists')
        return email

    @field_validator('email')
    @classmethod
    def too_short_email(cls, email: str) -> str:
        if len(email) < 3:
            raise ValueError('Email must be at least 3 characters')
        return email

    @field_validator('name')
    @classmethod
    def exists_name(cls, name: str) -> str:
        name_exists = UserModel.select().where(UserModel.name == name).exists()
        if name_exists:
            raise ValueError(f'Name {name} already exists')
        return name


class Login(General):

    @field_validator('name')
    @classmethod
    def exists_name(cls, name: str) -> str:
        name_exists = UserModel.select().where(UserModel.name == name).exists()
        if not name_exists:
            raise ValueError(f'Name {name} is not exists')
        return name

    @field_validator('password', mode='after')
    @classmethod
    def check_name_and_password(cls, password: str, info: str) -> str:

        name = info.data.get('name')
        try:
            user = UserModel.get(UserModel.name == name)
        except UserModel.DoesNotExist:
            raise ValueError(f'User with name "{name}" not found.')

        if not bcrypt.check_password_hash(user.password, password):
            raise ValueError('Invalid password.')
        return password