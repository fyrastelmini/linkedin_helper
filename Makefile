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
	docker run -dp 127.0.0.1:8080:8080 --mount type=volume,src=volume-db,dst=/etc/volume linkedinhelper:latest

build:
	docker volume create volume-db &&\
	docker build -t linkedinhelper:latest .

stop:
	docker ps -q --filter "ancestor=linkedinhelper:latest" | xargs -r docker stop

all: install format lint test