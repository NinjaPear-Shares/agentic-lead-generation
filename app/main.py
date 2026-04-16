from __future__ import annotations

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from app.config import Settings
from app.models import LeadGenResult
from app.tools.ninjapear import make_client
from app.workflows.pipeline import run_pipeline


class AgentDeps(BaseModel):
    settings: Settings


def build_agent(settings: Settings) -> Agent:
    model = OpenRouterModel(
        settings.openrouter_model,
        provider=OpenRouterProvider(api_key=settings.openrouter_api_key),
    )
    agent = Agent(
        model,
        output_type=LeadGenResult,
        deps_type=AgentDeps,
        system_prompt='Build an agentic lead generation queue using NinjaPear data and return typed results only.',
    )

    @agent.tool
    async def build_queue(ctx: RunContext[AgentDeps], seeds: list[str], target_role: str = 'Head of Revenue Operations') -> dict:
        with make_client(ctx.deps.settings.ninjapear_api_key) as api_client:
            result = run_pipeline(api_client, seeds=seeds, target_role=target_role)
        return result.model_dump()

    return agent


if __name__ == '__main__':
    settings = Settings.from_env()
    agent = build_agent(settings)
    result = agent.run_sync('Build the lead generation queue for Stripe and Shopify competitors.', deps=AgentDeps(settings=settings))
    print(result.output.model_dump_json(indent=2))
