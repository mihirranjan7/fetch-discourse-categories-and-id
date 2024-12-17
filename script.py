import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
import csv
import json

# Load environment variables
load_dotenv()

# Environment variables
DISCOURSE_URL = os.getenv("DISCOURSE_URL")
API_KEY = os.getenv("API_KEY")
API_USERNAME = os.getenv("API_USERNAME")

# Get start and end dates from the environment variables
START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")
KEYWORD = os.getenv("KEYWORD")  # Optional keyword to search topics by title

# Flags for optional features
FETCH_USER_DETAILS = os.getenv("FETCH_USER_DETAILS", "False") == "True"
FETCH_POSTS = os.getenv("FETCH_POSTS", "False") == "True"
FETCH_TOPIC_DESCRIPTION = os.getenv("FETCH_TOPIC_DESCRIPTION", "False") == "True"
FETCH_LAST_POSTED_AT = os.getenv("FETCH_LAST_POSTED_AT", "False") == "True"

# Convert to datetime objects
start_date = datetime.strptime(START_DATE, "%Y-%m-%d") if START_DATE else None
end_date = datetime.strptime(END_DATE, "%Y-%m-%d") if END_DATE else None

# Headers for API authentication
HEADERS = {
    "Api-Key": API_KEY,
    "Api-Username": API_USERNAME
}

# File paths for saving data
OUTPUT_FILE = "topics_and_categories.txt"
CSV_FILE = "topics_and_categories.csv"
JSON_FILE = "topics_and_categories.json"

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def list_all_categories():
    """
    Fetches and lists all categories from the Discourse API.
    
    Returns:
        dict: A dictionary mapping category IDs to category names.
    """
    url = f"{DISCOURSE_URL}/categories.json"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        categories = response.json()['category_list']['categories']
        category_dict = {category['id']: category['name'] for category in categories}
        logging.info(f"Fetched {len(categories)} categories.")
        return category_dict
    else:
        logging.error(f"Failed to fetch categories: {response.status_code}")
        return {}

def fetch_user_details(user_id):
    """
    Fetch user details from the Discourse API for a given user ID.
    
    Args:
        user_id (int): The ID of the user.
        
    Returns:
        dict: A dictionary with user details like username, registration date, and post count.
    """
    url = f"{DISCOURSE_URL}/users/{user_id}.json"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        user_data = response.json()['user']
        return {
            'username': user_data['username'],
            'created_at': user_data['created_at'],
            'post_count': user_data['post_count'],
        }
    else:
        logging.error(f"Failed to fetch user details for user ID {user_id}. Status code: {response.status_code}")
        return {}

def fetch_all_topics(start_date=None, end_date=None, keyword=None, page_size=30):
    """
    Fetches all topics from the Discourse API, with optional filters (date range, keyword).
    
    Args:
        start_date (str): Optional start date in 'YYYY-MM-DD' format.
        end_date (str): Optional end date in 'YYYY-MM-DD' format.
        keyword (str): Optional keyword to filter topics by title.
        page_size (int): Number of topics to fetch per page.
        
    Returns:
        list: A list of topics with their IDs, titles, category IDs, and post count.
    """
    topics = []
    page = 0

    while True:
        url = f"{DISCOURSE_URL}/latest.json"
        params = {"page": page, "per_page": page_size}
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            logging.error(f"Failed to fetch topics. Status Code: {response.status_code}")
            break

        data = response.json()
        topic_list = data.get("topic_list", {}).get("topics", [])

        if not topic_list:
            break  # No more topics to fetch

        for topic in topic_list:
            # Apply filters
            topic_created_at = datetime.strptime(topic["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if start_date and topic_created_at < start_date:
                continue
            if end_date and topic_created_at > end_date:
                continue
            if keyword and keyword.lower() not in topic["title"].lower():
                continue

            topic_details = {
                "id": topic["id"],
                "title": topic["title"],
                "category_id": topic.get("category_id", "Unknown"),
                "created_at": topic_created_at,
                "posts_count": topic["posts_count"],
                "views_count": topic.get("views_count", 0),
                "user": topic.get("last_poster_username", "Unknown")  # Use .get() to avoid KeyError
            }

            # Optionally fetch more data
            if FETCH_USER_DETAILS and topic.get("last_poster_user_id"):
                user_details = fetch_user_details(topic["last_poster_user_id"])
                topic_details.update(user_details)
            
            if FETCH_TOPIC_DESCRIPTION and 'description' in topic:
                topic_details["description"] = topic["description"]
            
            if FETCH_LAST_POSTED_AT and 'last_posted_at' in topic:
                topic_details["last_posted_at"] = topic["last_posted_at"]

            topics.append(topic_details)

        logging.info(f"Fetched page {page + 1}, Topics: {len(topic_list)}")
        page += 1

    return topics


def save_topics_and_categories(topics, categories):
    """
    Saves topics and categories to text, CSV, and JSON files.

    Args:
        topics (list): List of topics with IDs, titles, and category IDs.
        categories (dict): Dictionary of category IDs and their names.
    """
    # Group topics by category
    grouped_topics = {}
    category_count = {category: 0 for category in categories.values()}

    for topic in topics:
        category_name = categories.get(topic["category_id"], "Unknown Category")
        if category_name not in grouped_topics:
            grouped_topics[category_name] = []
        grouped_topics[category_name].append(topic["id"])
        category_count[category_name] += 1

    # Write to text file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("### Categories ###\n")
        for category_id, category_name in categories.items():
            file.write(f"ID: {category_id}, Name: {category_name}\n")

        file.write("\n### Topics ###\n")
        for topic in topics:
            category_name = categories.get(topic["category_id"], "Unknown Category")
            file.write(f"ID: {topic['id']}, Title: {topic['title']}, Category: {category_name}, Posts: {topic['posts_count']}, Views: {topic['views_count']}, User: {topic['user']}, Created At: {topic['created_at']}\n")
            if 'description' in topic:
                file.write(f"Description: {topic['description']}\n")
            if 'last_posted_at' in topic:
                file.write(f"Last Posted At: {topic['last_posted_at']}\n")
            if FETCH_USER_DETAILS:
                file.write(f"User Details: {topic.get('username', 'N/A')} | Registered At: {topic.get('created_at', 'N/A')} | Post Count: {topic.get('post_count', 'N/A')}\n")
            file.write("\n")

        file.write("\n### Topics Grouped by Category ###\n")
        for category_name, topic_ids in grouped_topics.items():
            file.write(f"Category: {category_name}\n")
            file.write(f"Topic IDs: {', '.join(map(str, topic_ids))}\n")
            file.write(f"Total Topics: {category_count[category_name]}\n\n")

    logging.info(f"Topics and categories saved to {OUTPUT_FILE}")

    # Save to CSV file
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Topic ID', 'Title', 'Category', 'Post Count', 'Views', 'User', 'Created At', 'Description', 'Last Posted At', 'User Details']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for topic in topics:
            category_name = categories.get(topic["category_id"], "Unknown Category")
            row = {
                'Topic ID': topic['id'],
                'Title': topic['title'],
                'Category': category_name,
                'Post Count': topic['posts_count'],
                'Views': topic['views_count'],
                'User': topic['user'],
                'Created At': topic['created_at'],
                'Description': topic.get("description", "N/A"),
                'Last Posted At': topic.get("last_posted_at", "N/A"),
                'User Details': f"Username: {topic.get('username', 'N/A')}, Registered At: {topic.get('created_at', 'N/A')}, Posts: {topic.get('post_count', 'N/A')}"
            }
            writer.writerow(row)

    logging.info(f"Topics and categories saved to {CSV_FILE}")

    # Save to JSON file
    with open(JSON_FILE, mode='w', encoding='utf-8') as jsonfile:
        json.dump(topics, jsonfile, default=str, indent=4)

    logging.info(f"Topics and categories saved to {JSON_FILE}")

# Main execution
if __name__ == "__main__":
    # Fetch categories
    categories = list_all_categories()

    # Fetch topics
    topics = fetch_all_topics(start_date=start_date, end_date=end_date, keyword=KEYWORD)

    # Save topics and categories to text, CSV, and JSON files
    if topics and categories:
        save_topics_and_categories(topics, categories)
    else:
        logging.error("Failed to fetch topics or categories.")
