.PHONY: demo events sample-events test

demo:
	python3 -m http.server 8000 --directory app

events:
	python3 -m aegisflow.event_generator --count 240 --out data/events.json

sample-events:
	python3 -m aegisflow.event_generator --count 32 --seed 17 --incident-start 12 --incident-end 18 --out data/sample_events.json

test:
	python3 -m unittest discover -s tests
