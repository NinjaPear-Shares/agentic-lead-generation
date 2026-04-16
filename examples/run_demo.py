from __future__ import annotations

from app.config import Settings
from app.tools.ninjapear import make_client
from app.workflows.pipeline import run_pipeline


def main():
    settings = Settings.from_env()
    with make_client(settings.ninjapear_api_key) as api_client:
        result = run_pipeline(
            api_client,
            seeds=['https://stripe.com', 'https://shopify.com'],
            target_role='Head of Revenue Operations',
        )
    print(result.model_dump_json(indent=2))


if __name__ == '__main__':
    main()
