import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup
import json
import time
import random
import base64

app = Flask(__name__)

# GitHub configuration
GITHUB_TOKEN = "your_github_token"  # Replace with your GitHub personal access token
GITHUB_REPO = "vacancy-updates"  # Replace with your GitHub repo name
GITHUB_USERNAME = "your_github_username"  # Replace with your GitHub username
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/"

# List of user-agent strings for rotation
USER_AGENTS = [
    "Mozilla/5.0 (iPad; CPU OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 YaBrowser/23.1.2 Mobile/15E148 Safari/605.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 YaBrowser/23.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
]

# Rotate headers by randomly picking a user-agent
def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9"
    }

# Function to scrape a specific page
def scrape_jobs(page_url):
    response = requests.get(page_url, headers=get_headers())
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    job_listings_container = soup.find("div", class_="listings-container margin-top-35")

    if not job_listings_container:
        return None

    job_links = job_listings_container.find_all("a", class_="job-listing")
    jobs = []

    for job in job_links:
        job_data = {}
        job_data["link"] = "https://vacancymail.co.zw" + job["href"]

        title = job.find("h3", class_="job-listing-title")
        job_data["title"] = title.text.strip() if title else None

        company = job.find("h4", class_="job-listing-company")
        job_data["company"] = company.text.strip() if company else None

        footer_items = job.find("div", class_="job-listing-footer").find_all("li")

        for item in footer_items:
            if "icon-material-outline-location-on" in item.i["class"]:
                job_data["location"] = item.text.strip()
            elif "icon-material-outline-access-time" in item.i["class"] and "Expires" in item.text:
                job_data["expiry_time"] = item.text.replace("Expires", "").strip()
            elif "icon-material-outline-business-center" in item.i["class"]:
                job_data["job_type"] = item.text.strip()

        # Avoid duplicate jobs based on the link
        if job_data not in jobs:
            jobs.append(job_data)

        time.sleep(random.uniform(0.5, 1.5))  # Avoid rate limiting

    return jobs

# Function to fetch existing JSON file from GitHub
def fetch_existing_file(file_path):
    url = GITHUB_API_URL + file_path
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_data = response.json()
        content = base64.b64decode(file_data["content"]).decode("utf-8")
        sha = file_data["sha"]  # GitHub requires the SHA for file updates
        return json.loads(content), sha
    return None, None

# Function to upload JSON to GitHub
def upload_to_github(file_path, file_name, content, sha=None):
    url = GITHUB_API_URL + file_path + "/" + file_name
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    # Prepare file content
    data = {
        "message": f"Update {file_name}",
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": "main"  # Replace with your branch if not main
    }
    if sha:
        data["sha"] = sha

    # Send PUT request to GitHub
    response = requests.put(url, headers=headers, json=data)
    return response.json()

# Flask route to scrape and save data
@app.route("/scrape/<page>.json", methods=["GET"])
def scrape_page(page):
    pages = {
        "page-1": "https://vacancymail.co.zw/jobs/",
        "page-2": "https://vacancymail.co.zw/jobs/?page=2",
        "page-3": "https://vacancymail.co.zw/jobs/?page=3",
        "page-4": "https://vacancymail.co.zw/jobs/?page=4",
        "page-5": "https://vacancymail.co.zw/jobs/?page=5"
    }

    if page not in pages:
        return jsonify({"error": "Page not found"}), 404

    # Scrape the page
    new_jobs = scrape_jobs(pages[page])
    if not new_jobs:
        return jsonify({"error": "Failed to scrape the page"}), 500

    # Fetch existing file from GitHub
    existing_jobs, sha = fetch_existing_file("vacancy-updates/" + page + ".json")

    # Replace existing data with new data
    updated_jobs = new_jobs

    # Save to JSON file
    file_name = f"{page}.json"
    json_content = json.dumps(updated_jobs, ensure_ascii=False, indent=4)
    response = upload_to_github("vacancy-updates", file_name, json_content, sha)

    if "content" in response:
        return jsonify({"message": f"Page {page} scraped and updated on GitHub", "github_response": response}), 200
    else:
        return jsonify({"error": "Failed to upload to GitHub", "github_response": response}), 500

if __name__ == "__main__":
    app.run(debug=True)
