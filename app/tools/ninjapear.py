from __future__ import annotations

from urllib.parse import urlparse, parse_qs
import ninjapear

from app.models import ProspectAccount, ProspectPerson, CompanyUpdate


def make_client(api_key: str):
    configuration = ninjapear.Configuration(host='https://nubela.co', access_token=api_key)
    return ninjapear.ApiClient(configuration)


def normalize_domain(url: str | None) -> str | None:
    if not url:
        return None
    return urlparse(url).netloc.replace('www.', '')


def get_customer_listing(api_client, website: str, cursor: str | None = None, page_size: int = 200, quality_filter: bool = True):
    api = ninjapear.CustomerAPIApi(api_client)
    return api.get_customer_listing(website=website, cursor=cursor, page_size=page_size, quality_filter=quality_filter)


def paginate_customer_listing(api_client, website: str, page_size: int = 200, quality_filter: bool = True):
    cursor = None
    while True:
        response = get_customer_listing(api_client, website=website, cursor=cursor, page_size=page_size, quality_filter=quality_filter)
        yield response
        data = response.to_dict() if hasattr(response, 'to_dict') else response
        next_page = data.get('next_page')
        if not next_page:
            break
        cursor_values = parse_qs(urlparse(next_page).query).get('cursor', [])
        cursor = cursor_values[0] if cursor_values else None
        if not cursor:
            break


def flatten_customer_response(source_company: str, payload) -> list[ProspectAccount]:
    rows: list[ProspectAccount] = []
    data = payload.to_dict() if hasattr(payload, 'to_dict') else payload
    for key, relationship_type in {
        'customers': 'customer',
        'investors': 'investor',
        'partner_platforms': 'partner_platform',
    }.items():
        for item in data.get(key, []) or []:
            rows.append(
                ProspectAccount(
                    source_company=source_company,
                    relationship_type=relationship_type,
                    name=item.get('name', 'Unknown'),
                    website=item.get('website'),
                    normalized_domain=normalize_domain(item.get('website')),
                    description=item.get('description'),
                    specialties=item.get('specialties') or [],
                    x_profile=item.get('x_profile'),
                    provenance=[source_company],
                )
            )
    return rows


def get_competitors(api_client, website: str, cursor: str | None = None, page_size: int = 50):
    api = ninjapear.CompetitorAPIApi(api_client)
    return api.get_competitor_listing(website=website, cursor=cursor, page_size=page_size)


def get_company_details(api_client, website: str):
    api = ninjapear.CompanyAPIApi(api_client)
    return api.get_company_details(website=website)


def get_employee_count(api_client, website: str):
    api = ninjapear.CompanyAPIApi(api_client)
    return api.get_employee_count(website=website)


def get_company_updates(api_client, website: str):
    api = ninjapear.CompanyAPIApi(api_client)
    return api.get_company_updates(website=website)


def get_company_funding(api_client, website: str):
    api = ninjapear.CompanyAPIApi(api_client)
    return api.get_company_funding(website=website)


def get_person_profile(api_client, work_email: str | None = None, employer_website: str | None = None, role: str | None = None, first_name: str | None = None, last_name: str | None = None):
    api = ninjapear.EmployeeAPIApi(api_client)
    return api.get_employee_profile(work_email=work_email, employer_website=employer_website, role=role, first_name=first_name, last_name=last_name)


def find_similar_people(api_client, employer_website: str, role: str):
    api = ninjapear.EmployeeAPIApi(api_client)
    return api.get_similar_people(employer_website=employer_website, role=role)


def create_monitor_feed(api_client, websites: list[str], frequency: str = 'daily'):
    api = ninjapear.CompanyAPIApi(api_client)
    return api.create_monitor_feed({'targets': websites, 'frequency': frequency})
