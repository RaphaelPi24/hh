import time
from sched import scheduler

from flask import Flask, render_template, request, url_for, redirect

from analytics.analytic import prepare_data, PopularSkillsDiagramProcessor, get_valid_data, process_timer
from analytics.diagrams import send, SkillsSalaryDiagramBuilder
from cache import CacheSession, VacancyCache, CacheSessionPathImage
from database_queries import Model, get_comparing_skills_with_salary
from forms import Form
from images import Image
from scheduler import process_profession_data, Scheduler

app = Flask(__name__)

app.secret_key = 'AbraKadabra5'
scheduler = Scheduler()
cache_session = CacheSession()
vacancy_cache = VacancyCache()
cache_path_image = CacheSessionPathImage()


@app.route('/', methods=['GET'])
def get_base():
    return render_template('views/base_content.html')


@app.route('/admin', methods=['GET'])
def get_admin():
    # Обработка сообщений для ручного сбора
    message_manual = cache_session.get_message('input_prof_name')
    message_auto_collect = cache_session.get_message('auto_collect_vacancies')
    message_timer_for_automatic_collection = cache_session.get_message('timer_for_automatic_collection')
    message_timer_for_delete_images = cache_session.get_message('timer_for_delete_images')

    return render_template(
        'views/admin.html',
        success_message_manual_collect_vacancies=cache_session.get_message(),
        error_message_manual_collect_vacancies=message_manual,
        success_autocollection=cache_session.get_auto_collection(),
        error_profession_autocollection=message_auto_collect,
        error_timer_for_automatic_collection=message_timer_for_automatic_collection,
        error_timer_for_delete_images=message_timer_for_delete_images,
        success_delete_images=cache_session.get_delete_images()
    )


@app.route('/manual', methods=['POST'])
def manual_collect_vacancies():
    manual_collection = get_valid_data(request.form.get('input_prof_name'), 'input_prof_name', cache_session)
    if manual_collection is None:
        return redirect(url_for('get_admin'))
    process_profession_data(manual_collection)
    cache_session.set_message('manual_collection', 'Сбор успешно завершён')
    return redirect(url_for('get_admin'))


@app.route('/admin', methods=['POST'])
def collect_vacancies():
    automatic_collection = get_valid_data(request.form.get('auto_collect_vacancies'), 'auto_collect_vacancies',
                                          cache_session)
    timer_for_automatic_collection = request.form.get('timer1')
    positive_number_timer, timer_digit = process_timer(timer_for_automatic_collection, cache_session,
                                                       'timer_for_automatic_collection')
    if automatic_collection is None or timer_digit is None:
        return redirect(url_for('get_admin'))

    scheduler.start(timer_digit, process_profession_data, 'autocollection', automatic_collection)
    cache_session.set_message('start_autocollection', 'Автосбор успешно запущен')
    return redirect(url_for('get_admin'))


@app.route('/delete_images', methods=['POST'])
def process_delete_images():
    timer_for_deleting_images = request.form.get('timer2')
    positive_number_timer, timer_digit = process_timer(timer_for_deleting_images, cache_session,
                                                       'timer_for_delete_images')
    if timer_digit is None:
        return redirect(url_for('get_admin'))

    scheduler.start(timer_digit, Image.delete, params=vacancy_cache.names_cache, id='delete_images')
    cache_session.set_message('start_delete_images', 'Автоудаление картинок успешно запущено')
    scheduler.check_jobs()
    return redirect(url_for('get_admin'))


@app.route('/stop_main_collection', methods=['POST'])
def stop_main_collection():
    scheduler.stop('autocollection')
    cache_session.set_message('finish_autocollection', 'Автосбор остановлен')
    return redirect(url_for('get_admin'))


@app.route('/stop_image_cleanup', methods=['POST'])
def stop_image_cleanup():
    scheduler.stop('delete_images')
    cache_session.set_message('finish_delete_images', 'Автоудаление картинок остановлено')
    return redirect(url_for('get_admin'))


@app.route('/show_vacancies', methods=['POST'])
def get_show():
    start = time.time()
    form = request.form
    valid_form = Form(form)
    vacancy_cache.get_form(valid_form)
    model = Model(valid_form)
    data = vacancy_cache.get_json_vacancy()
    if data is None:
        data = model.get()
        vacancy_cache.add(data)
    end = time.time()
    execution_time = end - start
    # jobs передается пустой, но не пустой
    return render_template('views/vacancies_cards.html', jobs=enumerate(data, 1), time=execution_time)


@app.route('/vacancies', methods=['GET'])
def get_page_vacancies():
    return render_template('views/filter_vacancies.html')


@app.route('/analytics', methods=['GET'])
def get_analytics():
    path, profession = cache_path_image.get_last_entry()
    if path is None:
        path = Image.get_path(profession)
    return render_template('views/analytics.html', image_path=path,
                           error_message_for_popular_skills=cache_session.get_message('profession'),
                           error_message_for_skills_salary=cache_session.get_message('profession_stats'))


@app.route('/skills_salary_diagram', methods=['POST'])
def skills_salary():
    valid_profession = get_valid_data(request.form.get('profession_stats'), 'profession_stats', cache_session)
    if valid_profession is None:
        return redirect(url_for('get_analytics'))

    data_for_diagram, diagram, path = prepare_data(valid_profession, cache_path_image,
                                                   get_comparing_skills_with_salary,
                                                   SkillsSalaryDiagramBuilder)
    send(diagram, data_for_diagram, path)
    cache_path_image.save_path_image(valid_profession, path)
    return redirect(url_for('get_analytics'))


@app.route('/popular_skills_diagram', methods=['POST'])
def popular_skills():
    valid_profession = get_valid_data(request.form.get('profession'), 'profession', cache_session)
    if valid_profession is None:
        return redirect(url_for('get_analytics'))

    processor = PopularSkillsDiagramProcessor(cache_path_image)
    processor.process(valid_profession)
    return redirect(url_for('get_analytics'))


if __name__ == '__main__':
    app.run()
