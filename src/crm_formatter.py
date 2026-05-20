CRM_MAP = {
    'hubspot': {
        'headers': ['Company Name', 'Phone', 'Website', 'Email', 'Address', 'Category', 'Rating', 'Review Count'],
        'row': lambda d: ','.join(
            f'"{str(v).replace(chr(34), chr(34)+chr(34))}"'
            for v in [
                d.get('title', ''),
                d.get('phone', ''),
                d.get('website', ''),
                '; '.join(d.get('emails', []) or []),
                d.get('address', ''),
                d.get('categoryName', ''),
                d.get('totalScore', ''),
                d.get('reviewsCount', 0),
            ]
        ),
    },
    'salesforce': {
        'headers': ['Name', 'Phone', 'Website', 'Email', 'BillingStreet', 'Type', 'Rating', 'NumberOfEmployees'],
        'row': lambda d: ','.join(
            f'"{str(v).replace(chr(34), chr(34)+chr(34))}"'
            for v in [
                d.get('title', ''),
                d.get('phone', ''),
                d.get('website', ''),
                '; '.join(d.get('emails', []) or []),
                d.get('address', ''),
                d.get('categoryName', ''),
                d.get('totalScore', ''),
                '',
            ]
        ),
    },
    'pipedrive': {
        'headers': ['Title', 'Phone', 'Web', 'Email', 'Address', 'Category', 'Timezone', 'Lead Value'],
        'row': lambda d: ','.join(
            f'"{str(v).replace(chr(34), chr(34)+chr(34))}"'
            for v in [
                d.get('title', ''),
                d.get('phone', ''),
                d.get('website', ''),
                '; '.join(d.get('emails', []) or []),
                d.get('address', ''),
                d.get('categoryName', ''),
                '',
                '',
            ]
        ),
    },
}


def format_crm_row(data: dict, crm_format: str) -> tuple[str, str]:
    if not crm_format or crm_format == 'none':
        return ('', '')
    fmt = CRM_MAP.get(crm_format)
    if not fmt:
        return ('', '')
    return (fmt['headers'], fmt['row'](data))
