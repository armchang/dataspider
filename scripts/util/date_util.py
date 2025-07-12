import datetime


def date_range(start_date, end_date):
    delta = datetime.timedelta(days=1)

    while start_date <= end_date:
        yield start_date
        start_date += delta