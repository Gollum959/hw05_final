from datetime import datetime
from typing import Dict

from django.http import HttpRequest


def year(request: HttpRequest) -> Dict[str, int]:
    """Return curent year."""
    curent_date = datetime.now()
    return {
        'curent_year': curent_date.year
    }
