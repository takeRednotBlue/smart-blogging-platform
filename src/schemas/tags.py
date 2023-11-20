from pydantic import BaseModel, ConfigDict


class TagModel(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str

    model_config: ConfigDict = ConfigDict(from_attributes=True)




