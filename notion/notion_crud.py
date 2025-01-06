"""
This script contains methods for connecting with Notion and the respective databases.
Functions:
    get_notion_db_entries(notion_database: NotionDatabase, status_filter: EntryStatus, date: date):
            notion_database (NotionDatabase): The NotionDatabase object representing the database 
                                              to query.
            status_filter (EntryStatus): The status to filter entries by.
            date (date): The date to filter entries by.
    put_notion_db_entry(db_name, entry_data):
        Create a new entry in the specified Notion database.
            db_name (str): The name of the database to add the entry to. Supported values are 
                           "University", "Personal", and "Work".
            entry_data (dict): A dictionary containing the entry data with keys "Name", "Status",
                               "Start Date", and "End Date".
            dict: The response from the Notion API after creating the entry.
            """
import os

import logging
from datetime import date, datetime

from notion_client import Client, APIErrorCode, APIResponseError

from notion.entities.notion_entities import NotionEntry, EntryStatus, NotionDatabase

def read_notion_db_entries(notion_database: NotionDatabase,
                          status_filter: EntryStatus,
                          filter_date: date = None) -> list[NotionEntry]:
    """
    Retrieve entries from a specified Notion database with a given status filter.
    Args:
        db_name (str): The name of the database to query. Supported values are "University", 
                       "Personal", and "Work".
        status_filter (str): The status to filter entries by.
    Returns:
        list: A list of NotionEntry objects containing the filtered entries.
    Raises:
        ValueError: If an unsupported database name is provided or if the database is not found.
        APIResponseError: If there is an error querying the Notion API.
    """

    notion = Client(auth=os.getenv('NOTION_TOKEN'),
                    log_level=logging.DEBUG)
    if notion_database.Name == "University":
        database_id = os.getenv('UNIVERSITY_DB_ID')
    elif notion_database.Name == "Personal":
        database_id = os.getenv('PERSONAL_DB_ID')
    elif notion_database.Name == "Work":
        database_id = os.getenv('WORK_DB_ID')
    else:
        raise ValueError("Unsupported database name")

    try:
        # Query the database for entries
        filters = {
            "and": [{
            "property": "Status",
            "status": {
                "equals": status_filter.Status
            }
            }
    ]
        }

        if filter_date:
            filters["and"].append(
            {
                "property": "Date",
                "date": {
                "on_or_after": filter_date.isoformat()
                }
            }
            )

        response = notion.databases.query(
            database_id=database_id,
            filter=filters
        )

        entries = []

        # Iterate through the entries
        for entry in response['results']:
            entry_id = entry['id']  # Fetch the unique ID of the entry
            properties = entry['properties']

            # Extract fields
            name = properties['Name']['title'][0]['plain_text'] \
                if properties['Name']['title'] else "N/A"
            status = properties['Status']['status']['name'] \
                if properties['Status']['status'] else "N/A"
            start_date = properties['Date']['date']['start'] \
                if properties['Date']['date'] else "N/A"
            end_date = properties['Date']['date']['end'] \
                if properties['Date']['date'] and properties['Date']['date']['end'] else "N/A"
            url = entry['url']

            status = EntryStatus(Status=status)
            start_date = datetime.fromisoformat(start_date) if start_date != "N/A" else None
            end_date = datetime.fromisoformat(end_date) if end_date != "N/A" else None

            # Create NotionEntry and append to entries list
            notion_entry = NotionEntry(
                id=entry_id,
                title=name,
                status=status,
                start_date=start_date,
                end_date=end_date,
                url=url
            )
            entries.append(notion_entry)

        return entries

    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            raise ValueError("Database not found") from error
        logging.error("Error: %s", error)


def create_notion_db_entry(notion_database: NotionDatabase, entry_data: NotionEntry):
    """
    Create a new entry in a specified Notion database.
    Args:
        notion_database (NotionDatabase): The Notion database object containing the name of the database.
        entry_data (NotionEntry): The entry data object containing the title, status, start date, and end date.
    Returns:
        dict: The response from the Notion API containing the details of the created page.
    Raises:
        ValueError: If the database name is unsupported or if the database is not found.
        APIResponseError: If there is an error response from the Notion API.
    """

    notion = Client(auth=os.getenv('NOTION_TOKEN'), log_level=logging.DEBUG)
    if notion_database.Name == "University":
        database_id = os.getenv('UNIVERSITY_DB_ID')
    elif notion_database.Name == "Personal":
        database_id = os.getenv('PERSONAL_DB_ID')
    elif notion_database.Name == "Work":
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
                                "content": entry_data.title
                            }
                        }
                    ]
                },
                "Status": {
                    "status": {
                        "name": entry_data.status.Status
                    }
                },
                "Date": {
                    "date": {
                        "start": entry_data.start_date.isoformat(),
                        "end": entry_data.end_date.isoformat()
                    }
                }
            }
        )

        return response

    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            raise ValueError("Database not found") from error
        logging.error("Error: %s", error)


def delete_notion_db_entry(entry_id: str):
    """
    Delete an entry from a specified Notion database.
    Args:
        entry_id (str): The unique identifier of the entry to delete.
    Raises:
        ValueError: If the database name is unsupported or if the database is not found.
        APIResponseError: If there is an error response from the Notion API.
    """

    notion = Client(auth=os.getenv('NOTION_TOKEN'), log_level=logging.DEBUG)

    try:
        # Delete the entry from the database
        notion.pages.update(
            page_id=entry_id,
            archived=True
        )

    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            raise ValueError("Entry not found") from error
        logging.error("Error: %s", error)


def update_notion_db_entry(entry_data: NotionEntry):
    """
    Update an entry in a specified Notion database.
    Args:
        entry_data (NotionEntry): The entry data object containing the title, status, 
                                  start date, and end date.
    Raises:
        ValueError: If the database name is unsupported or if the database is not found.
        APIResponseError: If there is an error response from the Notion API.
    """
    if entry_data.id is None:
        raise ValueError("Entry ID cannot be None")
    notion = Client(auth=os.getenv('NOTION_TOKEN'), log_level=logging.DEBUG)

    try:
        # Update the entry in the database
        notion.pages.update(
            page_id=entry_data.id,
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": entry_data.title
                            }
                        }
                    ]
                },
                "Status": {
                    "status": {
                        "name": entry_data.status.Status
                    }
                },
                "Date": {
                    "date": {
                        "start": entry_data.start_date.isoformat(),
                        "end": entry_data.end_date.isoformat()
                    }
                }
            }
        )

    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            raise ValueError("Entry not found") from error
        logging.error("Error: %s", error)
