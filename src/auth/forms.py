from peewee import IntegrityError

from auth.utils import check_name_and_password, NoMatchLoginPass
from auth.validation import Register, Login
from models import User


class RegistrationForm:
    def __init__(self, form):
        self.form = form.to_dict(flat=True)
        self.errors = []
        self.user = None

    def validate_and_write_in_bd(self) -> None:
        try:
            user_data = Register.model_validate(self.form)
            self.user = User.create(
                name=user_data.name,
                email=user_data.email,
                password=user_data.password
            )
        except NoMatchLoginPass as e: # не пашет
            self.errors.append(str(e))
        except (ValueError, IntegrityError) as e:

            for err in e.errors():
                field = err.get('loc')[0]
                message = err.get('msg')
                self.errors.append(f'{field.capitalize()}: {message}')



class LoginForm:
    def __init__(self, form):
        self.form = form.to_dict(flat=True)
        self.errors = []
        self.user_data = None
        self.user = None

    def validate(self) -> None:
        try:
            self.user_data = Login.model_validate(self.form)
            self.user = check_name_and_password(self.user_data)
        except (ValueError, User.DoesNotExist) as e:
            for err in e.errors():
                field = err.get('loc')[0]
                message = err.get('msg')
                self.errors.append(f'{field.capitalize()}: {message}')
        except NoMatchLoginPass as e:
            self.errors.append(''.join(e.args[0]))