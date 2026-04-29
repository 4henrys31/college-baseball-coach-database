from datetime import date
from .schema import VALIDATION_COLUMNS


def validate_rows(rows: list[dict]) -> list[dict]:
    issues = []
    for r in rows:
        base = {
            'run_date': date.today().isoformat(),
            'division': r.get('division',''),
            'school': r.get('school',''),
            'source_url': r.get('source_url',''),
        }
        if not r.get('full_name'):
            issues.append(base | {'issue_type': 'Missing Coach Name', 'issue_detail': 'No coach name parsed from source.', 'recommended_action': 'Manual review of baseball staff page.'})
        if not r.get('email'):
            issues.append(base | {'issue_type': 'Missing Email', 'issue_detail': f"{r.get('full_name','Unknown coach')} has no public email found.", 'recommended_action': 'Check official staff directory or coach bio page.'})
        if not r.get('phone'):
            issues.append(base | {'issue_type': 'Missing Phone', 'issue_detail': f"{r.get('full_name','Unknown coach')} has no public phone found.", 'recommended_action': 'Check staff directory or athletics department contact page.'})
        if r.get('data_status') == 'Needs Review':
            issues.append(base | {'issue_type': 'Needs Review', 'issue_detail': r.get('notes',''), 'recommended_action': 'Verify directly from official athletics website.'})
    return issues
