from datetime import datetime
from pydantic import BaseModel, EmailStr,ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    timezone: str | None = "Europe/Paris"

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class EventBase(BaseModel):
    title: str
    description: str | None = None
    start_datetime: datetime
    end_datetime: datetime
    all_day: bool = False
    location: str | None = None
    rrule: str | None = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    all_day: bool | None = None
    location: str | None = None
    rrule: str | None = None
    status: str | None = None

class EventRead(EventBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
