from pydantic import BaseModel, Field


class DiscoveryResponse(BaseModel):
    response: str = Field(
        description="The response text from an LLM containing insights into the data."
    )
