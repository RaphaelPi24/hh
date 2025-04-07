from peewee import *
from datetime import datetime
from models import db, VacancyCard, Skill, VacancySkill, User


class MigrationHistory(Model):
    version = CharField(unique=True)
    applied_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'migration_history'


def init_migration_table():
    with db:
        if 'migration_history' not in db.get_tables():
            db.create_tables([MigrationHistory])


def apply_migration(version, operations):
    with db.atomic():
        if MigrationHistory.select().where(MigrationHistory.version == version).exists():
            print(f'Migration {version} already applied')
            return False

        print(f'Applying {version}')
        for op in operations:
            try:
                op()
            except Exception as e:
                print(f'Error in operation: {e}')
                raise

        MigrationHistory.create(version=version)
        return True


MIGRATIONS = {
    '001_initial_tables': [
        lambda: VacancyCard.create_table(safe=True),
        lambda: Skill.create_table(safe=True),
        lambda: VacancySkill.create_table(safe=True),
        lambda: User.create_table(safe=True),
    ],
    '002_add_indexes': [
        lambda: db.execute_sql('CREATE INDEX IF NOT EXISTS idx_vacancy_skill_vacancy ON \"VacancySkill\"(vacancy_id)'),
        lambda: db.execute_sql('CREATE INDEX IF NOT EXISTS idx_vacancy_skill_skill ON \"VacancySkill\"(skill_id)'),
    ]
}


def run_migrations():
    init_migration_table()

    for version, operations in sorted(MIGRATIONS.items()):
        if not MigrationHistory.select().where(MigrationHistory.version == version).exists():
            print(f'Running migration: {version}')
            apply_migration(version, operations)