init:
	pip install pipenv
	pipenv install --dev

test:
	pipenv run pytest tests
