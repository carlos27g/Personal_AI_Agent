"""
This module contains the models used for data validation inside of the Notion microservice.

Classes:
    NotionEntry: A Pydantic model representing an entry in Notion.

"""

from typing import Literal
from datetime import datetime

from pydantic import BaseModel, Field


class NotionDatabase(BaseModel):
    """
    NotionDatabase model representing a Notion database.
    Attributes:
        ID (str): The unique identifier for the Notion database.
        Name (str): The name of the Notion database.
    """

    Name: Literal["University", "Work", "Personal"] = Field(..., description="The name of the Notion database")


class EntryStatus(BaseModel):
    """
    Status model representing the status of a Notion entry.
    Attributes:
        Status (Literal["Not started", "In progress", "Done"]): The status of the Notion entry.
    """

    Status: Literal["Not started", "In progress", "Done"] = Field(..., description="The status of the Notion entry")


class NotionEntry(BaseModel):
    """
    NotionEntry model representing an entry in Notion.
    Attributes:
        id (str): The unique identifier for the Notion entry.
        name (str): The name of the Notion entry.
        status: EntryStatus (Literal["Not started", "In progress", "Done"]): The status of the Notion entry.
        start_date (date): The start date of the Notion entry.
        End_Date (date): The end date of the Notion entry.
        url (str): The URL of the Notion entry.
    Methods:
        __str__(): Returns a string representation of the NotionEntry instance.
    """

    id: str | None = Field(None, description="The unique identifier for the Notion entry")
    title: str = Field(..., description="The name of the Notion entry")
    status: EntryStatus = Field(..., description="The status of the Notion entry")
    start_date: datetime | None = Field(None, description="The start date and time of the Notion entry")
    end_date: datetime | None = Field(None, description="The end date and time of the Notion entry")
    url: str | None = Field(None, description="The URL of the Notion entry")

    def __str__(self):
        return (f"NotionEntry(ID={self.id}, Name={self.title}, Status={self.status}, "
                f"Start_Date={self.start_date}, End_Date={self.end_date}, URL={self.url})")
