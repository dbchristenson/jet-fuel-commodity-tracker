# Jet Fuel Commodity Dashboard

A simple Streamlit app for analyzing Gulf-Coast Jet Fuel spot market prices against other petroleum commodities

## Maintenance
**Adding a report must be done manually.** To add a report file a pdf under resources/reports with naming template: ```jetdash_week_n_report.pdf``` where n is the current week. Inside ```current_report.py``` change the current week number to **n**.

**Historical reporting** is also done manually to reflect whether the report successfully predicted price movement for the following week. In ```historical_reports.py```, add a python dictionary entry to the ```REPORT_HISTORY``` constant variable at the top of the page.