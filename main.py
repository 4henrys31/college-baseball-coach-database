import argparse
import json
from pathlib import Path

from .db import connect, init_db, upsert_coach
from .scraper import load_seed_csv, scrape_school
from .sheets import ensure_tabs, sync_all
from .validate import validate_rows
from .schema import COACH_COLUMNS


def run(seed_csv: str, dry_run: bool = False):
    conn = connect()
    init_db(conn)
    schools = load_seed_csv(seed_csv)
    all_rows = []
    for school in schools:
        all_rows.extend(scrape_school(school))
    for row in all_rows:
        upsert_coach(conn, row)
    conn.commit()
    validation = validate_rows(all_rows)
    if dry_run:
        Path('reports').mkdir(exist_ok=True)
        Path('reports/latest_rows.json').write_text(json.dumps(all_rows, indent=2), encoding='utf-8')
        Path('reports/latest_validation.json').write_text(json.dumps(validation, indent=2), encoding='utf-8')
        print(f'DRY RUN COMPLETE: {len(all_rows)} coach rows, {len(validation)} validation issues.')
    else:
        sync_all(all_rows, validation_rows=validation, changelog_rows=[])
        print(f'SYNC COMPLETE: {len(all_rows)} coach rows pushed to Google Sheets.')


def init_sheet():
    ensure_tabs()
    print('Google Sheet tabs are ready.')


def cli():
    parser = argparse.ArgumentParser(description='College Baseball Coach Recruiting Database')
    sub = parser.add_subparsers(dest='command', required=True)
    p_run = sub.add_parser('run')
    p_run.add_argument('--seed', default='data/seeds/schools_sample.csv')
    p_run.add_argument('--dry-run', action='store_true')
    sub.add_parser('init-sheet')
    args = parser.parse_args()
    if args.command == 'run':
        run(args.seed, args.dry_run)
    elif args.command == 'init-sheet':
        init_sheet()

if __name__ == '__main__':
    cli()
