from typing import Literal
from pydantic import BaseModel, Field


class NotionEntry(BaseModel):
    ID: str = Field(..., alias="ID")
    Name: str = Field(..., alias="Name")
    Status: Literal["Not started", "In progress", "Done"] = Field(..., alias="Status")
    Start_Date: str = Field(..., alias="Start Date")
    End_Date: str = Field(..., alias="End Date")
    URL: str = Field(..., alias="URL")

    def __str__(self):
        return (f"NotionEntry(ID={self.ID}, Name={self.Name}, Status={self.Status}, "
                f"Start_Date={self.Start_Date}, End_Date={self.End_Date}, URL={self.URL})")
