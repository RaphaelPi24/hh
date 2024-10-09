import asyncio

from flask import Flask, render_template, request, url_for, redirect
from peewee import IntegrityError, OperationalError

from models import VacancyCard
from parsers.easy_parser import get_data, get_average_salary, get_keyskills, to_bd
from analytics.data_for_diagram import get_popular_skills
from analytics.diagrams import create_diagramm_skills_salary, PopularSkillDiagramBuilder, send

app = Flask(__name__)

#q = {'1С: Предприятие 8': 7, 'Работа с большим объемом информации': 2, '1С программирование': 17, 'Асинхронное программирование': 1, 'Веб-программирование': 5, 'Работа в команде': 3, 'MS SQL': 6, 'C#': 8, 'MS SQL Server': 2, 'MS Visual Studio': 3, 'Visual Studio C#': 1, 'Wonderware': 1, 'Transact-SQL': 1, 'SSRS': 1, 'C/C++': 2, 'С#': 1, '.NET Framework': 2, 'Win32 Api': 1, 'программирование': 1, 'объектно-ориентированное программирование': 1, 'ООП': 8, 'Базы данных': 6, 'SQL': 16, '.NET Core': 2, 'ASP.NET Core': 1, 'Docker': 6, 'Kubernetes': 1, 'Инженерные системы': 1, 'Автоматизация технологических процессов': 1, 'Электрические системы и слаботочные системы': 1, 'Автоматизация производства': 1, 'Монтаж оборудования': 1, 'Инжиниринг': 1, 'Электромонтажные работы': 1, 'Автоматизация': 3, 'knx': 1, 'Ответственность': 1, 'Желание работать': 1, 'Исполнительность': 1, 'JavaScript': 15, 'Java': 7, 'HTML5': 4, 'CSS': 7, 'ASP.NET': 3, 'HTML': 6, 'Верстка сайтов': 2, '1С': 5, 'Ruby': 1, 'Системное мышление': 2, 'C++': 7, 'Python': 7, 'Информационные технологии': 1, 'Сетевые протоколы': 1, 'Распределенные системы': 1, 'Git': 13, '1С: Розница': 1, '1С: Управление Торговлей': 5, 'Подключение торгового оборудования к 1С': 1, 'Обучение и развитие': 4, '1С: Предприятие': 4, 'Управление командой': 1, 'Ведение переговоров': 1, 'Бизнес-планирование': 1, 'Системный подход': 1, 'Моделирование бизнес процессов': 1, 'Аналитика': 1, '1С: Бухгалтерия': 2, 'Обучение персонала': 1, 'Постановка задач разработчикам': 1, 'Разработка технических заданий': 1, 'Управленческие навыки': 1, 'Основы программирования': 1, 'Пользователь ПК': 2, 'Умение работать в команде': 2, 'Node.js': 3, 'Prisma': 1, 'Procreate': 1, 'Создание конфигурации 1С': 3, '1C: ERP': 2, '1С: Комплексная автоматизация': 1, '1С: CRM ПРОФ': 1, '1C: Бухгалтерия': 2, 'MySQL': 7, 'Wordpress': 1, 'PHP': 7, 'Laravel': 2, 'GitHub': 3, 'jQuery': 4, 'CSS3': 2, 'Bootstrap': 2, 'Рефакторинг кода': 1, 'Angular': 2, 'JSON API': 2, 'HTTPS': 1, 'REST API': 3, 'Адаптивная верстка': 1, 'Битрикс24': 3, '1С-Битрикс': 4, 'Разработка': 1, '1С: Логистика': 1, 'Qt': 2, 'Разработка ПО': 4, 'C': 1, 'Алгоритмы и структуры данных': 1, 'Обновление конфигурации 1С': 3, 'Серверное оборудование': 1, 'Автоматизация процессов': 1, 'Hibernate ORM': 1, 'ORACLE': 2, 'PostgreSQL': 8, 'Spring Framework': 2, 'Java Core': 1, 'SVN': 1, 'Cистемы управления базами данных': 1, 'АСУ ТП': 1, 'ePLAN': 1, 'CODESYS': 1, 'FBD': 1, 'Проектирование инженерных систем': 1, 'Пуско-наладочные работы': 1, 'ОВЕН': 1, 'Segnetics': 1, 'Zentec': 1, 'Проектная документация': 1, 'SCADA': 1, 'Системная интеграция': 1, 'Metatrader4/5': 1, 'cTrader': 1, 'Биржевые шлюзы': 1, 'FastAPI': 2, 'Jira': 1, 'YouTrack': 1, 'Allure': 1, 'Docker-compose': 1, 'TypeScript': 3, 'Оптимизация кода': 4, 'React': 3, 'API Key': 1, 'API': 2, '1С: Зарплата и управление персоналом': 2, '1С: Бухгалтерия предприятия': 1, 'Умение верстать сайты': 1, 'Adobe Photoshop': 1, 'Joomla CMS': 1, 'CMS Bitrix': 1, 'SOAP': 1, 'Разработка CMS': 1, 'Кроссбраузерная верстка': 1, 'Битрикс': 1, 'Java Script': 2, 'Linux': 5, 'HTML-верстка': 1, 'Линейное программирование': 1, 'Bitrix': 1, 'Английский — A1 — Начальный': 1, 'Backend': 2, 'Smarty': 1, 'PHP7': 1, 'PHP8': 1, 'phpMyAdmin': 1, 'Работа с людьми': 2, 'Консультирование': 1, 'Техническая поддержка': 1, 'Проведение презентаций': 1, 'Лазерная техника': 1, 'Металлообработка': 1, 'Windows Forms': 1, '.NET': 1, 'EtherCAT': 1, 'ModBus': 1, 'Управление временем': 1, 'Мобильность': 1, 'Деловая коммуникация': 2, 'SPA': 1, 'Oracle Pl/SQL': 1, 'Консультирование пользователей': 1, 'XML': 2, 'TensorFlow': 1, 'PyTorch': 1, 'Keras': 1, 'Delphi': 2, 'Работа с базами данных': 2, 'StimulSoft': 1, '1C: Предприятие': 2, 'Pascal': 1, 'Turbo Pascal': 1, 'Borland Delphi': 1, 'MS Excel': 1, 'MS Word': 1, 'MS Outlook': 1, 'Грамотная речь': 1, 'Django Framework': 1, 'Symfony': 1, 'Xilinx Zynq': 1, 'STM32': 1, 'PetaLinux': 1, 'DevOps': 1, 'Power BI': 1, 'Профессиональные знания платформы 1С': 1, 'Опыт работы с автоматизацией бухгалтерского учета': 1, 'Умение работать в команде, целеустремленность, работа на результат': 1, 'Android': 1, 'VueJS': 2, 'Vue': 1, 'Быстро учусь': 1, 'Дружелюбность': 1, 'Высокая энергичность и инициативность': 1, '1С: Управление предприятием': 1, 'ERP-системы на базе 1С': 1, 'Системный анализ': 1, 'Go': 1, 'Golang': 1, 'Bash': 1, 'Математическое программирование': 1, 'Алгоритмы': 1, 'Анализ данных': 1, 'Аналитическое мышление': 2, 'TeamCity': 1, 'Frontend': 1, 'Мотивация': 1, 'Ориентация на результат': 1, 'программист': 1, 'алгоритмы': 1, 'Внимательность': 1, 'Сосредоточенность': 1, '1С: Документооборот': 1, 'База данных: Oracle': 1, 'СУБД': 1, 'Аналитический склад ума': 1, 'MQTT': 1}


@app.route('/', methods=['GET'])
def get_base():  # put application's code here
    return render_template('views/base.html')

@app.route('/', methods=['POST'])
def post_base():
    try:
        search_query = request.form['user-input']
    except KeyError:
        print('ошибка: текст в запросе нет')
    print(search_query)
    return redirect(url_for('get_show', query=search_query))



@app.route('/show', methods=['GET', 'POST'])
def get_show():
    search_query = request.args.get('query')

    vacancy_data = asyncio.run(get_data(search_query))
    print('Первичные данные собраны')
    vacancy_data_have_average_salary = get_average_salary(vacancy_data)
    print('Собраные данные вакансий со средними зарплатами')
    full_vacancy_data = get_keyskills(vacancy_data_have_average_salary)
    print('Собраны полные данные')
    to_bd(full_vacancy_data)
    data_for_diagram = get_popular_skills()
    #print(full_vacancy_data)
    diagram = PopularSkillDiagramBuilder()
    image = send(diagram, data_for_diagram)

    #jobs=vacancy_data_have_average_salary,
    return render_template('views/vacancy_list.html', search_query=search_query,  image=image)

if __name__ == '__main__':
    app.run()
