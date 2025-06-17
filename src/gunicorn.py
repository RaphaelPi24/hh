from os import environ

bind = '0.0.0.0:' + environ.get('PORT', '5000')
max_requests = 1000

workers = 2

reload = True
name = 'hh'
