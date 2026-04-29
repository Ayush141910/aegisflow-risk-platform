.PHONY: demo events test

demo:
	python3 -m http.server 8000 --directory app

events:
	python3 -m aegisflow.event_generator --count 240 --out data/events.json

test:
	python3 -m unittest discover -s tests
