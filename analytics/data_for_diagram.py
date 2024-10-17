from models import VacancyCard


def get_popular_skills():
    data = (
        VacancyCard
        .select(VacancyCard.skills)
        .dicts()
    )
    popular_skills = {}
    for cart in data:
        text = cart['skills']
        if text:
            skills_list = [skill.strip() for skill in text.split(',') if len(skill) > 0]
            for skill in skills_list:
                if len(skill) > 0:
                    if skill in popular_skills:
                        popular_skills[skill] += 1
                    else:
                        popular_skills[skill] = {}
                        popular_skills[skill] = 1
    return popular_skills


def get_comparing_skills_with_salary(data: list) -> dict:
    keyskills = {}
    for cart in data:
        for skill in cart.skills:
            if skill in keyskills:
                keyskills[skill]['count'] += 1
                if cart.get('average_salary') is not None:
                    # Убедись, что список зарплат существует, затем добавь зарплату
                    if 'salary' in keyskills[skill]:
                        keyskills[skill]['salary'].append(cart['average_salary'])
                    else:
                        keyskills[skill]['salary'] = [cart['average_salary']]
            else:
                keyskills[skill] = {}
                keyskills[skill]['count'] = 1
                if cart.get('average_salary') is not None:
                    keyskills[skill]['salary'] = [cart['average_salary']]
                else:
                    keyskills[skill]['salary'] = []
    for key in keyskills:
        if len(keyskills[key]['salary']) > 0:
            keyskills[key]['salary'] = sum(keyskills[key]['salary']) // len(keyskills[key]['salary'])
    return keyskills
