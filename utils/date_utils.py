from datetime import datetime, timedelta

def get_forecast_dates(start_date_str, duration_days):
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        return [(start_date + timedelta(days=i)).isoformat() for i in range(duration_days)]
    except Exception as e:
        print(f"[ERROR] Invalid date: {e}")
        return []
