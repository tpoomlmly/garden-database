from datetime import datetime as dt
from werkzeug.exceptions import BadRequest


def dt_from_month(month):
    """Converts the name of a month to a sortable datetime object.

    Only works with English months.
    """
    try:
        return dt.strptime(month, '%B')
    except ValueError:
        raise  BadRequest