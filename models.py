import peewee as pw

db = pw.SqliteDatabase('hh.db')


class BaseModel(pw.Model):
    id = pw.AutoField(primary_key=True)

    class Meta:
        database = db


class VacancyCard(BaseModel):
    class Meta:
        table_name = 'VacancyCard'

    name = pw.CharField()
    number: pw.IntegerField()
    name: pw.CharField()
    salary_from: pw.IntegerField()
    salary_to: pw.IntegerField()
    area: pw.CharField()
    currency: pw.CharField()
    employer: pw.CharField()
    schedule: pw.CharField()
    experience: pw.CharField()
    employment: pw.CharField()
    api_url: pw.CharField()
    url: pw.CharField()
    skills: pw.CharField()
    average_salary: pw.IntegerField()
