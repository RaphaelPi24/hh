import base64
import io

from matplotlib import pyplot as plt


class DiagramBuilder:
    xlabel: str = None
    ylabel: str = None
    title: str = None

    def __init__(self):
        self.labels = None
        self.counts = None
        self.salaries = None
        self.ax = None

    def prepare_data(self, data: dict) -> None:
        raise NotImplementedError

    def get_plot(self):
        raise NotImplementedError

    def set_labels(self):
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.title)

    def plot(self, figsize: tuple[int, int]):
        # Создание диаграммы
        self.fig, self.ax = plt.subplots(figsize=figsize)
        bars = self.get_plot()
        self.set_labels()
        plt.tight_layout()

    def to_base64(self) -> str:
        img = io.BytesIO()
        self.fig.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        return plot_url

# убрать обработку данных из диаграммы
class SkillsSalaryDiagramBuilder(DiagramBuilder):
    xlabel: str = None
    ylabel: str = None
    title: str = None

    def prepare_data(self, data: dict) -> None:
        for k in data.keys():
            if isinstance(data[k]['salary'], list):
                data[k]['salary'] = 0
        data = {k: v for k, v in data.items() if isinstance(v['salary'], (int, float)) and v['salary'] >= 0}
        # Сортировка по зарплате в порядке убывания
        data = dict(sorted(data.items(), key=lambda x: x[1]['salary'], reverse=False))

        self.labels = list(data.keys())
        self.counts = [d['count'] for d in data.values()]
        self.salaries = [d['salary'] for d in data.values()]

    def get_plot(self):
        plot = self.ax.barh(self.labels, self.counts, color='skyblue', label='Количество навыков')
        for i, (count, salary) in enumerate(zip(self.counts, self.salaries)):
            self.ax.text(count, i, f'{salary}', va='center')
        return plot


class PopularSkillDiagramBuilder(DiagramBuilder):
    def prepare_data(self, data: dict) -> None:
        sorted_data = sorted(data.items(), key=lambda x: x[1])  # Сортировка по возрастанию
        self.labels, self.values = zip(*sorted_data)

    def get_plot(self):
        plot = self.ax.barh(self.labels, self.values, color='skyblue')
        return plot


def send(diagram, data):
    diagram.prepare_data(data)
    diagram.plot((10, 30))
    return diagram.to_base64()





def create_diagramm_skills_salary(data):
    # Преобразование данных в списки
    # Фильтрация данных с ненулевой зарплатой

    for k in data.keys():
        if isinstance(data[k]['salary'], list):
            data[k]['salary'] = 0
    data = {k: v for k, v in data.items() if isinstance(v['salary'], (int, float)) and v['salary'] >= 0}
    # Сортировка по зарплате в порядке убывания
    data = dict(sorted(data.items(), key=lambda x: x[1]['salary'], reverse=False))

    labels = list(data.keys())
    counts = [d['count'] for d in data.values()]
    salaries = [d['salary'] for d in data.values()]

    # Создание диаграммы
    fig, ax1 = plt.subplots(figsize=(12, 30))

    # Столбцы по количеству
    ax1.barh(labels, counts, color='skyblue', label='Количество навыков')
    ax1.set_xlabel('Количество')
    ax1.set_ylabel('Навыки')
    ax1.set_title('Навыки и их количество')

    # Добавление данных о зарплатах
    for i, (count, salary) in enumerate(zip(counts, salaries)):
        ax1.text(count, i, f'{salary}', va='center')

    plt.tight_layout()

    # Сохранение диаграммы в изображение
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Конвертирование изображения в base64 для HTML
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return plot_url


def create_diagram_popular_skills(data):
    # Генерация диаграммы
    sorted_data = sorted(data.items(), key=lambda x: x[1])  # Сортировка по возрастанию
    # sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)  # Сортировка по убыванию

    # Разделение на метки и значения после сортировки
    labels, values = zip(*sorted_data)

    #fig, ax1 = plt.subplots(figsize=(12, 30))

    # # Столбцы по количеству
    # ax1.barh(labels, counts, color='skyblue', label='Количество навыков')
    # ax1.set_xlabel('Количество')
    # ax1.set_ylabel('Навыки')
    # ax1.set_title('Навыки и их количество')
    # labels = list(data.keys())
    # values = list(data.values())

    plt.figure(figsize=(10, 30))

    plt.barh(labels, values, color='skyblue')
    plt.xlabel('Количество')
    plt.title('Диаграмма навыков')
    plt.tight_layout()

    # Сохранение диаграммы в буфер
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return plot_url
