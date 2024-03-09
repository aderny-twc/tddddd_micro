test:
	pytest . -s -v -x
run:
	uvicorn entrypoints.main:app --reload --port 5005