import time
from sched import scheduler

from flask import Flask, render_template, request, url_for, redirect

from analytics.analytic import prepare_data, PopularSkillsDiagramProcessor, get_valid_data
from analytics.diagrams import send, SkillsSalaryDiagramBuilder
from cache import Cache, CacheSession, VacancyCache, CacheSessionPathImage
from database_queries import Model, get_comparing_skills_with_salary
from images import Image
from scheduler import process_profession_data, Scheduler
from forms import Form

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
    return render_template(
        'views/admin.html',
        message_manual_collect_vacancies=cache_session.get_manual_collection(),
        start_autocollect_vacancies=cache_session.get_auto_collection(),
        stop_autocollection=cache_session.get_auto_collection(),
        start_process_delete_images=cache_session.get_delete_images(),
        stop_delete_images=cache_session.get_delete_images()
    )


@app.route('/manual', methods=['POST'])
def manual_collect_vacancies():
    manual_collection = request.form.get('input_prof_name') or None
    if manual_collection:
        process_profession_data(manual_collection)
        cache_session.set_message('manual_collection', 'Сбор успешно завершён')
    return redirect(url_for('get_admin'))


@app.route('/admin', methods=['POST'])
def collect_vacancies():
    automatic_collection = request.form.get('auto_collect_vacancies') or None
    timer_for_automatic_collection = request.form.get('timer1') or None

    if automatic_collection:
        professions_for_autocollection = automatic_collection.split(',')
        scheduler.start(timer_for_automatic_collection, process_profession_data, 'autocollection',
                        professions_for_autocollection)
        cache_session.set_message('start_autocollection', 'Автосбор успешно запущен')
    return redirect(url_for('get_admin'))


@app.route('/delete_images', methods=['POST'])
def process_delete_images():
    timer_for_deleting_images = request.form.get('timer2') or None
    if timer_for_deleting_images:
        scheduler.start(timer_for_deleting_images, image.delete, params=Cache.names_cache, id='delete_images')
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
    return render_template('views/analytics.html', image_path=path)


@app.route('/skills_salary_diagram', methods=['POST'])
def skills_salary():
    profession = get_valid_data(request.form.get('profession_stats'))
    if profession:
        data_for_diagram, diagram, path = prepare_data(profession, cache_path_image,
                                                       get_comparing_skills_with_salary,
                                                       SkillsSalaryDiagramBuilder)
        send(diagram, data_for_diagram, path)
        cache_path_image.save_path_image(profession, path)
    return redirect(url_for('get_analytics'))


@app.route('/popular_skills_diagram', methods=['POST'])
def popular_skills():
    profession = get_valid_data(request.form.get('profession'))
    if profession is None:
        return 'Not Found', 404

    processor = PopularSkillsDiagramProcessor(cache_path_image)
    processor.process(profession)
    return redirect(url_for('get_analytics'))


if __name__ == '__main__':
    app.run()
