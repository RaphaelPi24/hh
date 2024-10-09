import peewee as pw
import psycopg2

db = pw.PostgresqlDatabase('hh', host='localhost', port=5432, user='userhh', password='159')
#db1 = pw.PostgresqlDatabase('hh', host='localhost', port=5432, user='postgres', password='cor')
db.connection()
#db1.connection()

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
    skills = pw.CharField()
    average_salary = pw.IntegerField()

VacancyCard.create_table()
