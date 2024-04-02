install:
	pip install --upgrade pip &&\
		pip install pytest &&\
			pip install -r requirements.txt

test:
	python -m pytest -vv test_app.py

format:
	black *.py

lint:
	pylint --disable=R,C app.py

run:
	python app.py

build:
	docker build -t linkedinhelper:latest .
all: install format lint test