from datetime import date

from notion.notion_crud import read_notion_db_entries, create_notion_db_entry, update_notion_db_entry, delete_notion_db_entry
from notion.entities.notion_entities import NotionDatabase, EntryStatus
from notion.entities.notion_entities import NotionEntry
from datetime import datetime, timedelta

def main():

    # Create a new Notion entry
    new_entry = NotionEntry(
        title="Cuddling time with Amelie",
        status=EntryStatus(Status="Not started"),
        start_date=datetime.now() + timedelta(days=1, hours=10 - datetime.now().hour),
        end_date=datetime.now() + timedelta(days=1, hours=11 - datetime.now().hour)
    )

    database = NotionDatabase(Name="Personal")

    response = create_notion_db_entry(database, new_entry)
    print(response)

    # Fetch data from Notion
    notion_database = NotionDatabase(Name="Personal")
    status_filter = EntryStatus(Status="Not started")
    filter_date = date.today() + timedelta(days=1)
    response = read_notion_db_entries(notion_database, status_filter, filter_date)
    for entry in response:
        print(entry)
        # Search for the entry with the title "This is a test"
        search_title = "Cuddling time with Amelie"
        for entry in response:
            if entry.title == search_title:
                entry_id = entry.id
                break
        else:
            print(f"No entry found with the title '{search_title}'")
            return
        entry.status = EntryStatus(Status="Done")
        entry.id = entry_id
        # Update the entry with the found id
        update_notion_db_entry(notion_database, entry)

        # Delete the entry with the found id
        delete_notion_db_entry(notion_database, entry_id)



if __name__ == "__main__":
    main()
