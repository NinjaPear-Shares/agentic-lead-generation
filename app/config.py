from __future__ import annotations

import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class Settings(BaseModel):
    ninjapear_api_key: str = Field(..., alias='NINJAPEAR_API_KEY')
    openrouter_api_key: str = Field(..., alias='OPENROUTER_API_KEY')
    openrouter_model: str = Field(default='anthropic/claude-sonnet-4-5', alias='OPENROUTER_MODEL')

    @classmethod
    def from_env(cls) -> 'Settings':
        load_dotenv()
        return cls(
            NINJAPEAR_API_KEY=os.environ['NINJAPEAR_API_KEY'],
            OPENROUTER_API_KEY=os.environ['OPENROUTER_API_KEY'],
            OPENROUTER_MODEL=os.environ.get('OPENROUTER_MODEL', 'anthropic/claude-sonnet-4-5'),
        )
