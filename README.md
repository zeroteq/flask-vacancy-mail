# Vacancy Updates

A web scraper and API service that automatically collects and updates job listings from VacancyMail Zimbabwe, storing them in a GitHub repository for easy access and tracking.

## Overview

This project provides a Flask-based web service that scrapes job listings from [VacancyMail Zimbabwe](https://vacancymail.co.zw/jobs/), transforms the data into a structured JSON format, and pushes updates to a GitHub repository. It helps job seekers stay updated with the latest job opportunities in Zimbabwe without having to manually check the website.

## Features

- Scrapes job listings from multiple pages of VacancyMail
- Extracts detailed job information (title, company, location, expiry date, job type)
- Stores data in structured JSON format
- Updates GitHub repository automatically
- Provides simple API endpoints to trigger scraping
- Implements user-agent rotation to avoid rate limiting

## Requirements

- Python 3.7+
- Flask
- BeautifulSoup4
- Requests
- GitHub Personal Access Token with repo permissions

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your_github_username/vacancy-updates.git
cd vacancy-updates
```

2. Install dependencies:
```bash
pip install flask beautifulsoup4 requests
```

3. Configure the application by updating these variables in the script:
```python
# Replace with your GitHub credentials
GITHUB_TOKEN = "your_github_token"  
GITHUB_REPO = "vacancy-updates"  
GITHUB_USERNAME = "your_github_username"  
```

## Usage

### Running the Application

Run the Flask application:
```bash
python app.py
```

The server will start on http://127.0.0.1:5000/ by default.

### API Endpoints

The application provides the following API endpoint:

- **GET /scrape/{page}.json**: Scrapes the specified page and updates the corresponding JSON file in the GitHub repository.
  - `page` can be: page-1, page-2, page-3, page-4, page-5

Example:
```
http://127.0.0.1:5000/scrape/page-1.json
```

### GitHub Repository Structure

After running the scraper, your GitHub repository will contain JSON files with the following structure:

```
vacancy-updates/
├── page-1.json
├── page-2.json
├── page-3.json
├── page-4.json
└── page-5.json
```

Each JSON file contains an array of job objects with the following structure:

```json
[
    {
        "link": "https://vacancymail.co.zw/job/1234",
        "title": "Software Engineer",
        "company": "Tech Company",
        "location": "Harare",
        "expiry_time": "11 Apr 2025",
        "job_type": "Full Time"
    },
    ...
]
```

## Automation

To automate the scraping process, you can set up a cron job or use GitHub Actions to periodically call the API endpoints.

### Example GitHub Actions Workflow

Create a file `.github/workflows/scrape.yml` in your repository:

```yaml
name: Scrape Job Listings

on:
  schedule:
    - cron: '0 */12 * * *'  # Run every 12 hours
  workflow_dispatch:  # Allow manual triggering

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Scrape Page 1
        run: curl -X GET "https://your-deployed-app.com/scrape/page-1.json"
      - name: Scrape Page 2
        run: curl -X GET "https://your-deployed-app.com/scrape/page-2.json"
      - name: Scrape Page 3
        run: curl -X GET "https://your-deployed-app.com/scrape/page-3.json"
      - name: Scrape Page 4
        run: curl -X GET "https://your-deployed-app.com/scrape/page-4.json"
      - name: Scrape Page 5
        run: curl -X GET "https://your-deployed-app.com/scrape/page-5.json"
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is meant for personal use and educational purposes only. Please respect VacancyMail's terms of service and robots.txt when using this scraper. The maintainers of this project are not responsible for any misuse or violation of terms.
