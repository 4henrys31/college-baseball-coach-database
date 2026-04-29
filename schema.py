COACH_COLUMNS = [
    'division','school','state','conference','coach_first_name','coach_last_name','full_name','title','role_category',
    'email','phone','athletics_website','baseball_page_url','staff_directory_url','source_url','last_verified_date',
    'data_status','notes','contacted','date_contacted','contact_method','follow_up_date','follow_up_status',
    'camp_invite_sent','clinic_invite_sent','player_interest_level','coach_response','next_action','outreach_notes','do_not_contact'
]

VALIDATION_COLUMNS = ['run_date','division','school','issue_type','issue_detail','source_url','recommended_action']
CHANGELOG_COLUMNS = ['run_date','school','division','change_type','field_changed','old_value','new_value','source_url']
TABS = ['Master Database','NCAA Division 1','NCAA Division 2','NCAA Division 3','NAIA','Junior College / Two-Year Programs','Validation Report','Annual Change Log','Missing / Needs Manual Review','Outreach Tracker']
DIVISION_TABS = {
    'NCAA Division 1': 'NCAA Division 1',
    'NCAA Division 2': 'NCAA Division 2',
    'NCAA Division 3': 'NCAA Division 3',
    'NAIA': 'NAIA',
    'NJCAA': 'Junior College / Two-Year Programs',
    'CCCAA': 'Junior College / Two-Year Programs',
    'NWAC': 'Junior College / Two-Year Programs',
    'Junior College': 'Junior College / Two-Year Programs',
    'Two-Year': 'Junior College / Two-Year Programs',
}
