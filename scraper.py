import csv
import re
from datetime import date
from urllib.parse import urljoin

import phonenumbers
import requests
from bs4 import BeautifulSoup

from .config import settings

ROLE_PATTERNS = [
    ('Head Coach', re.compile(r'\bhead\s+coach\b', re.I)),
    ('Recruiting Coordinator', re.compile(r'\brecruit(ing)?\s+coordinator\b|\brecruiting\b', re.I)),
    ('Assistant Coach', re.compile(r'\bassistant\s+coach\b|\bassoc(iate)?\s+head\s+coach\b|\bpitching\s+coach\b|\bhitting\s+coach\b|\binfield\s+coach\b|\boutfield\s+coach\b|\bcatching\s+coach\b', re.I)),
]
EMAIL_RE = re.compile(r'[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}', re.I)


def normalize_phone(text: str) -> str:
    if not text:
        return ''
    found = []
    for match in phonenumbers.PhoneNumberMatcher(text, 'US'):
        found.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.NATIONAL))
    return found[0] if found else ''


def classify_role(title: str) -> str:
    for role, pattern in ROLE_PATTERNS:
        if pattern.search(title or ''):
            return role
    return ''


def split_name(name: str):
    clean = ' '.join((name or '').replace('\n', ' ').split())
    parts = clean.split()
    if len(parts) == 0:
        return '', '', ''
    if len(parts) == 1:
        return parts[0], '', clean
    return parts[0], parts[-1], clean


def fetch_html(url: str) -> str:
    headers = {'User-Agent': settings.user_agent}
    resp = requests.get(url, headers=headers, timeout=25)
    resp.raise_for_status()
    return resp.text


def extract_email(text: str, soup: BeautifulSoup) -> str:
    for a in soup.select('a[href^="mailto:"]'):
        email = a.get('href', '').replace('mailto:', '').split('?')[0].strip()
        if EMAIL_RE.match(email):
            return email
    match = EMAIL_RE.search(text or '')
    return match.group(0) if match else ''


def scrape_page_for_coaches(school_row: dict, url: str) -> list[dict]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, 'lxml')
    candidates = []

    # Most Sidearm/Presto/athletics sites present coaches in cards, table rows, or list items.
    selectors = ['tr', '.sidearm-staff-member', '.staff-card', '.coach-card', '.roster_coaches .person', 'li']
    seen_blocks = set()
    for selector in selectors:
        for el in soup.select(selector):
            block_text = ' '.join(el.get_text(' ', strip=True).split())
            if len(block_text) < 8 or block_text in seen_blocks:
                continue
            seen_blocks.add(block_text)
            if not any(p.search(block_text) for _, p in ROLE_PATTERNS):
                continue
            email = extract_email(block_text, BeautifulSoup(str(el), 'lxml'))
            phone = normalize_phone(block_text)
            title = ''
            for role, pattern in ROLE_PATTERNS:
                m = pattern.search(block_text)
                if m:
                    title = m.group(0).title()
                    break
            # Try name from linked coach profile or first table/card text chunk.
            name = ''
            linked = el.select_one('a[href]')
            if linked and not linked.get('href','').startswith('mailto:'):
                name = linked.get_text(' ', strip=True)
            if not name:
                name = block_text.split(title)[0].strip(' |,-') if title else block_text.split('  ')[0]
            first, last, full = split_name(name)
            role_category = classify_role(block_text)
            if not role_category or not full:
                continue
            candidates.append(build_row(school_row, first, last, full, title or role_category, role_category, email, phone, url))
    # de-dupe
    unique = {}
    for c in candidates:
        key = (c['school'], c['full_name'], c['title'], c['email'])
        unique[key] = c
    return list(unique.values())


def build_row(school, first, last, full, title, role_category, email, phone, source_url):
    status = 'Verified'
    notes = []
    if not email:
        notes.append('Missing email')
    if not phone:
        notes.append('Missing phone')
    if notes:
        status = 'Needs Review'
    return {
        'division': school.get('division',''),
        'school': school.get('school',''),
        'state': school.get('state',''),
        'conference': school.get('conference',''),
        'coach_first_name': first,
        'coach_last_name': last,
        'full_name': full,
        'title': title,
        'role_category': role_category,
        'email': email,
        'phone': phone,
        'athletics_website': school.get('athletics_website',''),
        'baseball_page_url': school.get('baseball_page_url',''),
        'staff_directory_url': school.get('staff_directory_url',''),
        'source_url': source_url,
        'last_verified_date': date.today().isoformat(),
        'data_status': status,
        'notes': '; '.join(notes),
        'contacted': '', 'date_contacted': '', 'contact_method': '', 'follow_up_date': '', 'follow_up_status': '',
        'camp_invite_sent': '', 'clinic_invite_sent': '', 'player_interest_level': '', 'coach_response': '',
        'next_action': '', 'outreach_notes': '', 'do_not_contact': ''
    }


def load_seed_csv(path: str) -> list[dict]:
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def scrape_school(school_row: dict) -> list[dict]:
    urls = [school_row.get('baseball_page_url'), school_row.get('staff_directory_url')]
    rows = []
    for url in [u for u in urls if u]:
        try:
            rows.extend(scrape_page_for_coaches(school_row, url))
        except Exception as exc:
            rows.append(build_row(school_row, '', '', '', 'SCRAPE ERROR', '', '', '', url) | {
                'data_status': 'Needs Review', 'notes': f'Scrape error: {exc}'
            })
    return rows
