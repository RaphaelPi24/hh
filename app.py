import base64
import time
from sched import scheduler

from flask import Flask, render_template, request, url_for, redirect, session

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
    start_autocollection = stop_autocollection = start_delete_images = stop_process_delete_images = ''
    output_for_manual_collect_vacancies = session.pop('manual_collection', None)

    # Обработка сообщений для автосбора вакансий
    if 'finish_autocollection' in session:
        session.pop('start_autocollection', None)
        stop_autocollection = session.pop('finish_autocollection')
    elif 'start_autocollection' in session:
        start_autocollection = session.get('start_autocollection')

    # Обработка сообщений для удаления изображений
    if 'finish_delete_images' in session:
        session.pop('start_delete_images', None)
        stop_process_delete_images = session.pop('finish_delete_images')
    elif 'start_delete_images' in session:
        start_delete_images = session.get('start_delete_images')

    return render_template(
        'views/admin.html',
        message_manual_collect_vacancies=output_for_manual_collect_vacancies,
        start_autocollect_vacancies=start_autocollection,
        stop_autocollection=stop_autocollection,
        start_process_delete_images=start_delete_images,
        stop_delete_images=stop_process_delete_images
    )


@app.route('/manual', methods=['POST'])
def manual_collect_vacancies():
    manual_collection = request.form.get('input_prof_name') or None
    if manual_collection:
        process_profession_data(manual_collection)
        session['manual_collection'] = 'Сбор успешно завершён'
    return redirect(url_for('get_admin'))


@app.route('/admin', methods=['POST'])
def collect_vacancies():
    automatic_collection = request.form.get('auto_collect_vacancies') or None
    timer_for_automatic_collection = request.form.get('timer1') or None

    if automatic_collection:
        professions_for_autocollection = automatic_collection.split(',')
        scheduler.start(timer_for_automatic_collection, process_profession_data, 'autocollection',
                        professions_for_autocollection)
        session['start_autocollection'] = 'Автосбор успешно запущен'
    return redirect(url_for('get_admin'))


@app.route('/delete_images', methods=['POST'])
def process_delete_images():
    timer_for_deleting_images = request.form.get('timer2') or None
    if timer_for_deleting_images:
        scheduler.start(timer_for_deleting_images, image.delete, params=Cache.names_cache, id='delete_images')
        session['start_delete_images'] = 'Автоудаление картинок успешно запущено'
        scheduler.check_jobs()
    return redirect(url_for('get_admin'))


@app.route('/stop_main_collection', methods=['POST'])
def stop_main_collection():
    scheduler.stop('autocollection')
    session['finish_autocollection'] = 'Автосбор остановлен'
    return redirect(url_for('get_admin'))


@app.route('/stop_image_cleanup', methods=['POST'])
def stop_image_cleanup():
    scheduler.stop('delete_images')
    session['finish_delete_images'] = 'Автоудаление картинок остановлено'
    return redirect(url_for('get_admin'))


@app.route('/show_vacancies', methods=['POST'])
def get_show():
    start = time.time()

    form = request.form
    valid_form = Form(form)
    cache = Cache(valid_form)
    model = Model(valid_form)
    data = cache.get()
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
    return render_template('views/analytics.html')


@app.route('/analytics', methods=['POST'])
def post_analytics():
    profession = request.form.get('profession') or None
    profession2 = request.form.get('profession_stats') or None
    data_for_diagram = diagram = None
    cache_path = cache_key = None

    if profession is not None:
        cache_key = profession
        cache_path = redis_client.get(cache_key)
        if not cache_path:
            data_for_diagram = get_popular_skills(profession)
            diagram = PopularSkillDiagramBuilder()
    elif profession2 is not None:
        cache_key = profession2
        cache_path = redis_client.get(profession2)
        if not cache_path:
            data_for_diagram = get_comparing_skills_with_salary(profession2)
            diagram = SkillsSalaryDiagramBuilder()

    if cache_path:
        if isinstance(cache_path, bytes):
            image_path = cache_path.decode('utf-8')
        else:
            # Если это уже строка, используем как есть
            image_path = cache_path

    else:
        image_code = base64.b64decode(send(diagram, data_for_diagram))
        image_path = f'static/image_diagram/{cache_key}.png'
        image.save(image_path, image_code)
        redis_client.setex(cache_key, 60, image_path)

    return render_template('views/diagram.html', image_path=image_path)


if __name__ == '__main__':
    app.run()
