from __future__ import annotations

from collections import OrderedDict

from app.models import ProspectAccount, ProspectPerson, LeadGenResult
from app.scoring import score_account, score_person
from app.tools.ninjapear import (
    flatten_customer_response,
    get_competitors,
    get_customer_listing,
    get_employee_count,
    get_company_updates,
    find_similar_people,
    normalize_domain,
)


def dedupe_accounts(accounts: list[ProspectAccount]) -> list[ProspectAccount]:
    deduped = OrderedDict()
    for account in accounts:
        key = account.normalized_domain or account.name.lower()
        if key not in deduped:
            deduped[key] = account
        else:
            deduped[key].provenance.extend(account.provenance)
    return list(deduped.values())


def pull_competitor_customers(api_client, seeds: list[str]) -> list[ProspectAccount]:
    accounts: list[ProspectAccount] = []
    for seed in seeds:
        payload = get_customer_listing(api_client, website=seed, quality_filter=True)
        accounts.extend(flatten_customer_response(seed, payload))
    return dedupe_accounts(accounts)


def expand_competitors(api_client, seed_domains: list[str], max_depth: int = 1, account_cap: int = 50) -> list[str]:
    visited = set()
    frontier = list(seed_domains)
    discovered: list[str] = []
    depth = 0

    while frontier and depth < max_depth and len(discovered) < account_cap:
        next_frontier = []
        for website in frontier:
            if website in visited:
                continue
            visited.add(website)
            payload = get_competitors(api_client, website=website)
            data = payload.to_dict() if hasattr(payload, 'to_dict') else payload
            for item in data.get('competitors', []) or []:
                comp_website = item.get('website')
                if comp_website and comp_website not in visited and comp_website not in discovered:
                    discovered.append(comp_website)
                    next_frontier.append(comp_website)
                    if len(discovered) >= account_cap:
                        break
        frontier = next_frontier
        depth += 1

    return discovered


def build_contact_queue(api_client, accounts: list[ProspectAccount], target_role: str = 'Head of Revenue Operations') -> list[ProspectPerson]:
    people: list[ProspectPerson] = []
    for account in accounts:
        if not account.website:
            continue
        payload = find_similar_people(api_client, employer_website=account.website, role=target_role)
        data = payload.to_dict() if hasattr(payload, 'to_dict') else payload
        for item in data.get('results', []) or data.get('people', []) or []:
            people.append(
                ProspectPerson(
                    account_domain=normalize_domain(account.website) or '',
                    full_name=item.get('full_name'),
                    role=item.get('role'),
                    work_email=item.get('work_email'),
                    x_handle=item.get('x_handle'),
                )
            )
    return people


def run_pipeline(api_client, seeds: list[str], target_role: str = 'Head of Revenue Operations') -> LeadGenResult:
    accounts = pull_competitor_customers(api_client, seeds)

    competitor_domains = expand_competitors(api_client, seeds, max_depth=1)
    for comp in competitor_domains[:5]:
        comp_payload = get_customer_listing(api_client, website=comp, quality_filter=True)
        accounts.extend(flatten_customer_response(comp, comp_payload))
    accounts = dedupe_accounts(accounts)

    top_accounts = accounts[:10]
    people = build_contact_queue(api_client, top_accounts, target_role=target_role)

    account_domains_with_people = {p.account_domain for p in people}
    for account in accounts:
        employee_payload = get_employee_count(api_client, website=account.website) if account.website else {}
        update_payload = get_company_updates(api_client, website=account.website) if account.website else {}
        employee_data = employee_payload.to_dict() if hasattr(employee_payload, 'to_dict') else employee_payload
        update_data = update_payload.to_dict() if hasattr(update_payload, 'to_dict') else update_payload
        employee_count = employee_data.get('employee_count') or employee_data.get('count')
        recent_updates = len(update_data.get('updates', []) or [])
        role_match = (account.normalized_domain or '') in account_domains_with_people
        account.score = score_account(
            is_competitor_customer=account.relationship_type == 'customer',
            employee_count=employee_count,
            recent_updates=recent_updates,
            role_match=role_match,
        )

    accounts.sort(key=lambda a: a.score, reverse=True)
    account_lookup = {a.normalized_domain: a for a in accounts if a.normalized_domain}
    for person in people:
        linked_account = account_lookup.get(person.account_domain)
        if linked_account:
            person.score = score_person(person, linked_account)
    people.sort(key=lambda p: p.score, reverse=True)

    summary = f'Found {len(accounts)} candidate accounts and {len(people)} likely buyer profiles from {len(seeds)} seed competitors.'
    return LeadGenResult(accounts=accounts[:25], people=people[:25], summary=summary)
