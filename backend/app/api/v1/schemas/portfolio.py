from pydantic import BaseModel, Field
from typing import Any


class ExperienceSchema(BaseModel):
    company: str
    position: str
    start_date: str = ""
    end_date: str = ""
    description: str = ""


class EducationSchema(BaseModel):
    degree: str
    institution: str
    year: str = ""


class LinksSchema(BaseModel):
    website: str = ""
    github: str = ""
    linkedin: str = ""


class UpsertPortfolioRequest(BaseModel):
    first_name: str
    last_name: str
    title: str = Field(..., description="Professional title — used for SEO")
    summary: str = Field(..., description="Short bio — used for SEO meta description")
    skills: list[str] = []
    experiences: list[ExperienceSchema] = []
    education: list[EducationSchema] = []
    links: LinksSchema = LinksSchema()

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Kiarash",
                "last_name": "Fazli",
                "title": "Full-stack Developer",
                "summary": "Experienced developer specializing in Python and React.",
                "skills": ["Python", "FastAPI", "React", "Docker"],
                "experiences": [
                    {
                        "company": "Irancell",
                        "position": "Backend Developer",
                        "start_date": "2021-03",
                        "end_date": "2023-06",
                        "description": "Built internal microservices handling 10M daily requests.",
                    }
                ],
                "education": [
                    {"degree": "B.Sc. Computer Engineering", "institution": "Islamic Azad University, Science And Research Branch", "year": "2020"}
                ],
                "links": {
                    "website": "https://kiarash.dev",
                    "github": "https://github.com/kiarashfz",
                    "linkedin": "https://linkedin.com/in/kiarashfz",
                },
            }
        }


class UpsertPortfolioResponse(BaseModel):
    username: str
    portfolio_url: str
    chunks_ingested: int
    created: bool  # True = new portfolio, False = updated existing

class PortfolioResponse(BaseModel):
    username: str
    first_name: str
    last_name: str
    title: str
    summary: str
    profile_data: Any