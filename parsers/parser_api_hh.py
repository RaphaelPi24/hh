from bs4 import BeautifulSoup
import requests


def get_json(url: str) -> BeautifulSoup:
    head = {'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=head)
    return BeautifulSoup(response.text, 'html5lib')


# print(get_json(f'https://hh.ru/oauth/authorize?response_type=code&client_id={client_id}&state={state}&'
#     f'redirect_uri={redirect_uri}'))