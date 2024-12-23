import os
import logging

from notion_client import Client, APIErrorCode, APIResponseError

from notion.entity_models import NotionEntry

def get_notion_db_entries(db_name, status_filter):
    """
    Retrieve entries from a specified Notion database with a given status filter.
    Args:
        db_name (str): The name of the database to query. Supported values are "University", "Personal", and "Work".
        status_filter (str): The status to filter entries by.
    Returns:
        list: A list of NotionEntry objects containing the filtered entries.
    Raises:
        ValueError: If an unsupported database name is provided or if the database is not found.
        APIResponseError: If there is an error querying the Notion API.
    """

    notion = Client(auth=os.getenv('NOTION_TOKEN'),
                    log_level=logging.DEBUG)
    if db_name == "University":
        database_id = os.getenv('UNIVERSITY_DB_ID')
    elif db_name == "Personal":
        database_id = os.getenv('PERSONAL_DB_ID')
    elif db_name == "Work":
        database_id = os.getenv('WORK_DB_ID')
    else:
        raise ValueError("Unsupported database name")

    try:
        # Query the database for entries
        response = notion.databases.query(database_id=database_id)

        entries = []

        # Iterate through the entries
        for entry in response['results']:
            entry_id = entry['id']  # Fetch the unique ID of the entry
            properties = entry['properties']
            
            # Extract fields
            name = properties['Name']['title'][0]['plain_text'] if properties['Name']['title'] else "N/A"
            status = properties['Status']['status']['name'] if properties['Status']['status'] else "N/A"
            date_start = properties['Date']['date']['start'] if properties['Date']['date'] else "N/A"
            date_end = properties['Date']['date']['end'] if properties['Date']['date'] and properties['Date']['date']['end'] else "N/A"
            url = entry['url']
            
            # Append to entries list if status matches the filter
            if status == status_filter:
                entries.append({
                    "ID": entry_id,
                    "Name": name,
                    "Status": status,
                    "Start Date": date_start,
                    "End Date": date_end,
                    "URL": url
                })

        return entries

    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            raise ValueError("Database not found") from error
        logging.error("Error: %s", error)


def put_notion_db_entry(db_name, entry_data):

    notion = Client(auth=os.getenv('NOTION_TOKEN'), log_level=logging.DEBUG)
    if db_name == "University":
        database_id = os.getenv('UNIVERSITY_DB_ID')
    elif db_name == "Personal":
        database_id = os.getenv('PERSONAL_DB_ID')
    elif db_name == "Work":
        database_id = os.getenv('WORK_DB_ID')
    else:
        raise ValueError("Unsupported database name")

    try:
        # Create a new entry in the database
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": entry_data["Name"]
                            }
                        }
                    ]
                },
                "Status": {
                    "select": {
                        "name": entry_data["Status"]
                    }
                },
                "Date": {
                    "date": {
                        "start": entry_data["Start Date"],
                        "end": entry_data["End Date"]
                    }
                }
            }
        )

        return response

    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            raise ValueError("Database not found") from error
        logging.error(f"Error: {error}")
