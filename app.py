import base64
import time
from sched import scheduler

from flask import Flask, render_template, request, url_for, redirect

from analytics.analytic import get_valid_data, prepare_data
from analytics.data_for_diagram import get_popular_skills, get_comparing_skills_with_salary
from analytics.diagrams import PopularSkillDiagramBuilder, send, SkillsSalaryDiagramBuilder
from images import Image
from scheduler import process_profession_data, Scheduler
from vacancy_service import Form, Cache, Model

app = Flask(__name__)

app.secret_key = 'AbraKadabra5'
scheduler = Scheduler()
image = Image()
cache = Cache()


@app.route('/', methods=['GET'])
def get_base():
    return render_template('views/base_content.html')


@app.route('/admin', methods=['GET'])
def get_admin():
    # Обработка сообщений для ручного сбора
    return render_template(
        'views/admin.html',
        message_manual_collect_vacancies=cache.get_manual_collection(),
        start_autocollect_vacancies=cache.get_auto_collection(),
        stop_autocollection=cache.get_auto_collection(),
        start_process_delete_images=cache.get_delete_images(),
        stop_delete_images=cache.get_delete_images()
    )


@app.route('/manual', methods=['POST'])
def manual_collect_vacancies():
    manual_collection = request.form.get('input_prof_name') or None
    if manual_collection:
        process_profession_data(manual_collection)
        cache.set_message('manual_collection', 'Сбор успешно завершён')
    return redirect(url_for('get_admin'))


@app.route('/admin', methods=['POST'])
def collect_vacancies():
    automatic_collection = request.form.get('auto_collect_vacancies') or None
    timer_for_automatic_collection = request.form.get('timer1') or None

    if automatic_collection:
        professions_for_autocollection = automatic_collection.split(',')
        scheduler.start(timer_for_automatic_collection, process_profession_data, 'autocollection',
                        professions_for_autocollection)
        cache.set_message('start_autocollection', 'Автосбор успешно запущен')
    return redirect(url_for('get_admin'))


@app.route('/delete_images', methods=['POST'])
def process_delete_images():
    timer_for_deleting_images = request.form.get('timer2') or None
    if timer_for_deleting_images:
        scheduler.start(timer_for_deleting_images, image.delete, params=Cache.names_cache, id='delete_images')
        cache.set_message('start_delete_images', 'Автоудаление картинок успешно запущено')
        scheduler.check_jobs()
    return redirect(url_for('get_admin'))


@app.route('/stop_main_collection', methods=['POST'])
def stop_main_collection():
    scheduler.stop('autocollection')
    cache.set_message('finish_autocollection', 'Автосбор остановлен')
    return redirect(url_for('get_admin'))


@app.route('/stop_image_cleanup', methods=['POST'])
def stop_image_cleanup():
    scheduler.stop('delete_images')
    cache.set_message('finish_delete_images', 'Автоудаление картинок остановлено')
    return redirect(url_for('get_admin'))


@app.route('/show_vacancies', methods=['POST'])
def get_show():
    start = time.time()

    form = request.form
    valid_form = Form(form)
    cache.get_form(valid_form)
    model = Model(valid_form)
    data = cache.get_json_vacancy()
    if data is None:
        data = model.get()
        cache.add(data)
    end = time.time()
    execution_time = end - start
    # jobs передается пустой, но не пустой
    return render_template('views/vacancies_cards.html', jobs=enumerate(data, 1), time=execution_time)


@app.route('/vacancies', methods=['GET'])
def get_page_vacancies():
    return render_template('views/filter_vacancies.html')


@app.route('/analytics', methods=['GET'])
def get_analytics():
    return render_template('views/analytics.html', image_path=cache.get_last_entry())


@app.route('/skills_salary_diagram', methods=['POST'])
def skills_salary():
    profession = get_valid_data(request.form.get('profession_stats'))
    if profession:
        data_for_diagram, diagram, path = prepare_data(profession, cache,
                                                                        get_comparing_skills_with_salary,
                                                                        SkillsSalaryDiagramBuilder)
        send(diagram, data_for_diagram, path)
        cache.save_path_image(profession, path)  # маг число, запрятать в cache?
    return redirect(url_for('get_analytics'))


@app.route('/popular_skills_diagram', methods=['POST'])
def popular_skills():
    profession = get_valid_data(request.form.get('profession'))
    if profession:
        data_for_diagram, diagram, path = prepare_data(profession, cache, get_popular_skills,
                                                                        PopularSkillDiagramBuilder)
        send(diagram, data_for_diagram, path)
        cache.save_path_image(profession , path) # маг число, запрятать в cache?
    return redirect(url_for('get_analytics'))
#print()

if __name__ == '__main__':
    app.run()
