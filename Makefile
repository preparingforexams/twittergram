.PHONY: check nice test

check: nice test

nice:
	poetry run black src/
	poetry run mypy src/ --exclude src/tests

test:
	poetry run pytest src/
