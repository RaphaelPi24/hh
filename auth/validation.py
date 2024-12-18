import re

from flask_bcrypt import Bcrypt
from pydantic import BaseModel, field_validator

bcrypt = Bcrypt()


class General(BaseModel):
    name: str
    password: str

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
    def too_short_email(cls, email: str) -> str:
        if len(email) < 3:
            raise ValueError('Email must be at least 3 characters')
        return email


class Login(General):
    ...
