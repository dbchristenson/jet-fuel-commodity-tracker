.PHONY: update install clean check runner
.DEFAULT_GOAL: runner

update: install
	get_data
	get_news
	scrape_data
	get_current_events

get_current_events:
	uv run python app/get_current_events.py

get_data:
	uv run python app/get_data.py

get_news:
	uv run python app/get_news.py

scrape_data:
	uv run python app/scrape_data.py

install: pyproject.toml
	uv sync

clean:
	rm -rf `find . -type d -name __pycache__`

runner: install update clean
	uv run streamlit run Welcome.py