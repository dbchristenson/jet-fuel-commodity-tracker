.PHONY: update install clean check runner
.DEFAULT_GOAL: runner

update: install
	uv run python app/get_current_events.py
	uv run python app/get_data.py
	uv run python app/get_news.py
	uv run python app/scrape_data.py

install: pyproject.toml
	uv sync

clean:
	rm -rf `find . -type d -name __pycache__`

runner: install update clean
	uv run streamlit run Welcome.py