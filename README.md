```markdown
# Discourse Topic and Category Fetcher

This script fetches topics and categories from a Discourse forum, saves the retrieved data to text, CSV, and JSON files, and optionally includes detailed user information, topic descriptions, and timestamps for posts. It supports filtering topics by date range and title keyword.

## Requirements

- Python 3.x
- Install the required Python libraries:
  ```bash
  pip install requests python-dotenv
  ```

## Setup

Before running the script, you need to configure the environment variables in a `.env` file. These variables will be used to authenticate with the Discourse API and control the behavior of the script.

### Example `.env` File:
```dotenv
DISCOURSE_URL=https://your-discourse-forum.com
API_KEY=your_api_key
API_USERNAME=your_api_username
START_DATE=2024-01-01
END_DATE=2024-12-31
KEYWORD=optional_keyword_for_filtering_topics
FETCH_USER_DETAILS=True
FETCH_POSTS=True
FETCH_TOPIC_DESCRIPTION=True
FETCH_LAST_POSTED_AT=True
```

### Environment Variables:

- **DISCOURSE_URL**: The base URL of your Discourse forum.
- **API_KEY**: The API key to authenticate requests.
- **API_USERNAME**: The username for API authentication.
- **START_DATE**: The start date for filtering topics (in `YYYY-MM-DD` format).
- **END_DATE**: The end date for filtering topics (in `YYYY-MM-DD` format).
- **KEYWORD**: A keyword to filter topics by title (optional).
- **FETCH_USER_DETAILS**: Set to `True` to fetch user details for the last poster of each topic.
- **FETCH_POSTS**: Set to `True` to fetch detailed post data.
- **FETCH_TOPIC_DESCRIPTION**: Set to `True` to include topic descriptions.
- **FETCH_LAST_POSTED_AT**: Set to `True` to include the timestamp for the last post.

## Usage

1. Place the script in a directory.
2. Ensure your `.env` file is in the same directory.
3. Run the script:
   ```bash
   script.py
   ```

The script will fetch all topics from your Discourse forum based on the specified filters and will save the results to the following files:

- **topics_and_categories.txt**: A text file containing topics and categories.
- **topics_and_categories.csv**: A CSV file with topic data.
- **topics_and_categories.json**: A JSON file with topic details.

## Features

- **List all categories**: Fetches all categories from the Discourse API.
- **Filter by date range**: Filters topics by a specified start and end date.
- **Keyword filtering**: Filters topics by a specified keyword in the title.
- **User details**: Optionally fetches user details for the last poster.
- **Topic description**: Optionally includes the topic description in the output.
- **Last posted timestamp**: Optionally includes the timestamp of the last post.

## Logging

The script uses logging to output the progress and errors. The log will be displayed in the terminal during execution.

## Files Created

- **topics_and_categories.txt**: Lists the categories and details of each topic.
- **topics_and_categories.csv**: A CSV containing topic details.
- **topics_and_categories.json**: A JSON file with detailed topic data.

## Example Output

### topics_and_categories.txt
```
### Categories ###
ID: 1, Name: General
ID: 2, Name: Support

### Topics ###
ID: 12345, Title: How to use Discourse API, Category: General, Posts: 5, Views: 100, User: johndoe, Created At: 2024-01-01
Description: This is a guide to using the Discourse API.
Last Posted At: 2024-01-02
User Details: johndoe | Registered At: 2020-05-15 | Post Count: 50

### Topics Grouped by Category ###
Category: General
Topic IDs: 12345, 12346
Total Topics: 2
```

### topics_and_categories.csv
| Topic ID | Title                  | Category | Post Count | Views | User    | Created At         | Description                     | Last Posted At    | User Details                                    |
|----------|------------------------|----------|------------|-------|---------|--------------------|----------------------------------|-------------------|-------------------------------------------------|
| 12345    | How to use Discourse API| General  | 5          | 100   | johndoe | 2024-01-01 12:34:56| This is a guide to using the API.| 2024-01-02 08:00:00| Username: johndoe, Registered At: 2020-05-15   |

### topics_and_categories.json
```json
[
  {
    "id": 12345,
    "title": "How to use Discourse API",
    "category_id": 1,
    "created_at": "2024-01-01T12:34:56.000Z",
    "posts_count": 5,
    "views_count": 100,
    "user": "johndoe",
    "description": "This is a guide to using the Discourse API.",
    "last_posted_at": "2024-01-02T08:00:00.000Z",
    "username": "johndoe",
    "created_at": "2020-05-15T10:00:00.000Z",
    "post_count": 50
  }
]
```

## License

This project is licensed under the MIT License.
```
