from datetime import datetime as dt


def dt_from_month(month):
    """Converts the name of a month to a sortable datetime object.

    Only works in english countries.
    """
    return dt.strptime(month, '%B')