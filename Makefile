.PHONY: check coding_standards test

check: coding_standards test

coding_standards:
	poetry run black src/
	poetry run flake8 --exit-zero src/
	poetry run mypy src/

test:
	poetry run pytest src/
