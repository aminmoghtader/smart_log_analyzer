
#  Smart Log Analyzer

A powerful **command-line log analysis tool** written in Python.  
Smart Log Analyzer helps developers and system administrators easily **parse**, **analyze**, and **summarize** log files from different systems.

---

## Features

- Supports both **plain text** and **JSON-based** log formats  
- Extracts and normalizes **timestamps**, **log levels**, and **messages**  
- Aggregates useful statistics:
  - Number of processed lines  
  - Total errors, warnings, malformed lines, etc.
 
-git clone https://github.com/aminmoghtader/smart_log_analyzer.git
-cd smart_log_analyzer
-pip install -r requirements.txt

-python -m analyzer.main --source "sample_logs/" --output "reports/final_report.json" --pretty
-pytest -v 

License

MIT License © 2025 Amin Moghtader
