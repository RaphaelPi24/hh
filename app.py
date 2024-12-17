import time
from sched import scheduler

from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager

from auth.views import bp as auth_bp
from analytics.analytic import prepare_data, PopularSkillsDiagramProcessor, SalaryDiagramProcessor
from analytics.diagrams import send, SkillsSalaryDiagramBuilder
from cache import CacheSession, VacancyCache, CacheSessionPathImage
from database_queries import Model, get_comparing_skills_with_salary
from forms import VacanciesForm, AdminForm, AnalyticsForm
from images import Image
from log import logger
from parsers.main import process_profession_data
from scheduler import Scheduler

app = Flask(__name__)

app.secret_key = 'AbraKadabra5'
scheduler = Scheduler()
cache_session = CacheSession()
vacancy_cache = VacancyCache()
cache_path_image = CacheSessionPathImage()

login_manager = LoginManager()
login_manager.login_view = 'auth.login_get'
login_manager.init_app(app)

users = {}


@login_manager.user_loader
def load_user(user_id):
    user = connection.hgetall(f'user:{user_id}')
    if user is None or len(user) == 0:
        user_instance = User.get(user_id)
        user_dict = model_to_dict(user_instance)
        # Преобразование значений словаря в строки для совместимости с Redis
        user_str_dict = {key: str(value) for key, value in user_dict.items()}
        connection.hset(f'user:{user_id}', mapping=user_str_dict)
        logger.info('Пользователь создан в кэше')
    else:
        # Преобразование ключей и значений обратно из байтов в строки
        user = {key.decode('utf-8'): value.decode('utf-8') for key, value in user.items()}
        user_instance = User(**user)
        logger.info('Пользователь извлечён из кэша')
    return user_instance


app.register_blueprint(auth_bp)


@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)


@app.route('/', methods=['GET'])
def get_base():
    logger.info("Приложение запущено!")
    return render_template('views/base_content.html')


@app.route('/admin', methods=['GET'])
def get_admin():
    return render_template(
        'views/admin.html',
        success_autocollection='Автосбор успешно запущен' if cache_session.schedule_run.get('autocollecion') else '',
        success_delete_images='Удаление картинок успешно запущено' if cache_session.schedule_run.get(
            'delete_images') else ''
    )


@app.route('/manual', methods=['POST'])
def manual_collect_vacancies():
    form = AdminForm(request.form)
    valid_profession = form.validate_manual_parser()
    if form.errors:
        return render_template('views/admin.html', error_message_manual_collect_vacancies=form.errors)

    process_profession_data(valid_profession)  # rq :(
    return render_template('views/admin.html', success_message_manual_collect_vacancies='Сбор успешно завершён')


@app.route('/admin', methods=['POST'])
def collect_vacancies():
    form = AdminForm(request.form)
    valid_professions, valid_timer = form.validate_auto_parser()
    if form.errors:
        return render_template('views/admin.html', error_autocollection=form.errors)

    scheduler.start(valid_timer, process_profession_data, 'autocollection', valid_professions)
    cache_session.schedule_run['autocollecion'] = True
    return redirect(url_for('get_admin'))


@app.route('/delete_images', methods=['POST'])
def process_delete_images():
    form = AdminForm(request.form)
    timer_digit = form.validate_params_for_del_image()
    if form.errors:
        return render_template('views/admin.html', error_timer_for_delete_images=form.errors)

    scheduler.start(timer_digit, Image.delete, params=vacancy_cache.names_cache, id='delete_images')
    cache_session.schedule_run['delete_images'] = True
    scheduler.check_jobs()
    return redirect(url_for('get_admin'))


@app.route('/stop_main_collection', methods=['POST'])
def stop_main_collection():
    scheduler.stop('autocollection')
    cache_session.schedule_run['autocollecion'] = False
    return render_template('views/admin.html', success_autocollection='Автосбор профессий прекращён')


@app.route('/stop_image_cleanup', methods=['POST'])
def stop_image_cleanup():
    scheduler.stop('delete_images')
    cache_session.schedule_run['delete_images'] = False
    return render_template('views/admin.html', success_delete_images='Автоудаление картинок остановлено')


@app.route('/show_vacancies', methods=['POST'])
def get_show():
    start = time.time()
    form = request.form
    valid_form = VacanciesForm(form)
    vacancy_cache.get_form(valid_form)
    model = Model(valid_form)
    data = vacancy_cache.get_json_vacancy()
    if data is None:
        data = model.get()
        vacancy_cache.add(data)
    end = time.time()
    execution_time = end - start
    return render_template('views/vacancies_cards.html', jobs=data, time=execution_time)


@app.route('/vacancies', methods=['GET'])
def get_page_vacancies():
    return render_template('views/filter_vacancies.html')


@app.route('/analytics', methods=['GET'])
def get_analytics():
    return render_template('views/analytics.html')


@app.route('/skills_salary_diagram', methods=['POST'])
def skills_salary():
    form = AnalyticsForm(request.form)
    valid_profession = form.validate_skill_salary()
    if form.errors is None:
        return render_template('views/analytics.html', error_message_for_skills_salary=form.errors)

    data_for_diagram, diagram, path = prepare_data(valid_profession, cache_path_image,
                                                   get_comparing_skills_with_salary,
                                                   SkillsSalaryDiagramBuilder)
    send(diagram, data_for_diagram, path)
    cache_path_image.save_path_image(valid_profession, path)
    processor = SalaryDiagramProcessor(cache_path_image)
    path = processor.process(valid_profession)
    return render_template('views/analytics.html', image_path=path)


@app.route('/popular_skills_diagram', methods=['POST'])
def popular_skills():
    form = AnalyticsForm(request.form)
    valid_profession = form.validate_popular_skill()
    if form.errors is None:
        return render_template('views/analytics.html', error_message_for_popular_skills=form.errors)

    processor = PopularSkillsDiagramProcessor(cache_path_image)
    path = processor.process(valid_profession)
    return render_template('views/analytics.html', image_path=path)


if __name__ == '__main__':
    app.run()
