setup:
	python -m pip install -r requirements.txt
	python -m pip install -r requirements_dev.txt
lint:
	python -m flake8 --config tox.ini
format:
	black .
test:
	python -m pytest
coverage:
	python -m coverage erase
	python -m coverage run -a -m pytest
	python -m coverage report || true
	python -m coverage html
typecheck:
	python -m mypy . --ignore-missing-imports --no-incremental
run:
	python -m app.run --input data/LSE_input.csv
