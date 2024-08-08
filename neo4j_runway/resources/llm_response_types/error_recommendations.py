from pydantic import BaseModel, Field


class ErrorRecommendations(BaseModel):
    recommendations: str = Field(
        description="The recommendations provided to fix errors in a data model."
    )
