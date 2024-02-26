from pydantic import BaseModel
from typing import Annotated, Union

class Booking(BaseModel):
    flight_code: str
    name: str
    phone: str
    email: str

class Ticket(BaseModel):
    booking_id: str
    name: str
    phone: str
    email: str