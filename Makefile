test:
	pytest . -s -v -x
run:
	uvicorn main:app --reload --port 5005