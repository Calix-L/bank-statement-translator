# Local development commands

.PHONY: help install test lint format check run translate clean

help:
	@echo "Bank Statement Translator - Makefile Commands"
	@echo ""
	@echo "  make install    Install dependencies"
	@echo "  make test       Run tests"
	@echo "  make lint       Run lint and type checks"
	@echo "  make format     Format code"
	@echo "  make check      Run tests and quality checks"
	@echo "  make run        Run Streamlit app"
	@echo "  make translate  Run dense PDF translation pipeline"
	@echo "  make clean      Clean temporary files"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

lint:
	flake8 .
	black --check .
	mypy .

format:
	black .

check:
	pytest tests/ -v
	flake8 .
	black --check .
	mypy .

run:
	streamlit run app.py

translate:
	python run_word_translator_pipeline.py

clean:
	cmd /c "for /d /r %i in (__pycache__) do @if exist \"%i\" rmdir /s /q \"%i\""
	cmd /c "del /s /q *.pyc *.pyo 2>nul"
	cmd /c "if exist .pytest_cache rmdir /s /q .pytest_cache"
	cmd /c "if exist .pytest_tmp rmdir /s /q .pytest_tmp"
