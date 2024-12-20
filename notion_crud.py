import os
from notion_client import Client # pylint:disable=import-error

def get_notion_db_entries(db_name, status_filter):

    notion = Client(auth=os.getenv('NOTION_TOKEN'))
    if db_name == "University":
        database_id = os.getenv('UNIVERSITY_DB_ID')
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

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
