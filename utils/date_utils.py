from datetime import datetime, timedelta
def get_forecast_dates(start_date: str, duration: int):
    if not start_date:
        start_date = datetime.today().strftime("%Y-%m-%d")

    return [datetime.strptime(start_date, "%Y-%m-%d").date() + timedelta(days=i) for i in range(duration)]