import peewee as pw

db = pw.PostgresqlDatabase('hh', host='localhost', port=5432, user='userhh', password='159')

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
# if __name__ == __main__
VacancyCard.create_table()
Skill.create_table()
VacancySkill.create_table()

