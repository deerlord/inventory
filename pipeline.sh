flake8 application
mypy application
coverage run --concurrency gevent --include='application/*' -m pytest tests && coverage report -m
