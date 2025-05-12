from cgitb import handler

from pydantic import BaseModel, Field, WrapValidator
from pydantic.dataclasses import dataclass
from typing import List, Optional, Any, Callable
from datetime import date

class ResumeData(BaseModel):
    """
    Pydantic model representing common fields extracted from a resume.
    """
    full_name: str|None = Field("full_name", strict=False, description="Full name of the candidate")
    email: str|None = Field("email", strict=False, description="Contact email address")
    phone: str|None = Field("phone", strict=False, description="Contact phone number")
    summary: str|None = Field("summary", strict=False, description="Professional summary or objective")
    education: List[dict]|None = Field(default_factory=list, description="List of education entries")
    languages: List[str]|List[dict]|None = Field(default_factory=list, description="List of language proficiencies")
    linkedin_url: str|None = Field("linkedin_url", strict=False, description="LinkedIn profile URL")
    skills: List[str]|List[dict]|None = Field(default_factory=list, description="List of professional skills")
    work_experience: List["WorkExperience"]|None = Field(default_factory=list, description="List of work experience entries")



class WorkExperience(BaseModel):
    """
    Pydanitc model that represents a work experience
    """
    title: str | None = Field("title", description="Job title or position")
    organization: str | None = Field("organization", description="Company or organization name")
    start_date: str | None = Field("start_date", description="Start date of employment")
    end_date: str | None = Field("end_date", description="End date of employment")
    details: Any | Any = Field(default_factory=dict, description="Additional details about the role")
