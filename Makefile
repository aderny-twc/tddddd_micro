test:
	pytest . -s -v -x
run:
	uvicorn entrypoints.main:app --reload --port 5005
clean-pyc:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete