import peewee as pw
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

import config

db = pw.PostgresqlDatabase(
    config.POSTGRES_DB,
    host=config.DB_HOST,
    port=config.POSTGRES_PORT,
    user=config.POSTGRES_USER,
    password=config.POSTGRES_PASSWORD,
)
db.connection()


class BaseModel(pw.Model):
    id = pw.AutoField(primary_key=True)

    class Meta:
        database = db


class VacancyCard(BaseModel):
    class Meta:
        table_name = 'VacancyCard'

    vacancy_id = pw.CharField(unique=True)
    name = pw.CharField()
    salary_from = pw.IntegerField()
    salary_to = pw.IntegerField()
    area = pw.CharField()
    currency = pw.CharField()
    employer = pw.CharField()
    schedule = pw.CharField()
    experience = pw.CharField()
    employment = pw.CharField()
    api_url = pw.CharField()
    url = pw.CharField()
    average_salary = pw.IntegerField()


class Skill(BaseModel):
    class Meta:
        table_name = 'Skill'

    name = pw.CharField(unique=True)  # Название навыка


class VacancySkill(BaseModel):
    class Meta:
        table_name = 'VacancySkill'

    vacancy = pw.ForeignKeyField(VacancyCard, backref='skills', on_delete='CASCADE')
    skill = pw.ForeignKeyField(Skill, backref='vacancies', on_delete='CASCADE')


class User(BaseModel, UserMixin):
    class Meta:
        table_name = 'user'

    name = pw.CharField(unique=True)
    email = pw.CharField(unique=True)
    password = pw.CharField()

    @classmethod
    def create(cls, **query):
        if query.get('password'):
            query['password'] = Bcrypt().generate_password_hash(query.get('password')).decode('utf-8')  # переопределить в .create
        return super().create(**query)

# if __name__ == __main__
# VacancyCard.create_table()
# Skill.create_table()
# VacancySkill.create_table()
# User.create_table()
