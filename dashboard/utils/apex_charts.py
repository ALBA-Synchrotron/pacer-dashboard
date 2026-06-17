from django.db.models import QuerySet


def generate_apex_error_heatmap_chart_data_from_queryset(queryset: QuerySet, error_queryset: QuerySet) -> dict:
    error_counts = {
        (error_stat["month"], error_stat["message_type"]): error_stat["count"]
        for error_stat in error_queryset
    }

    data = {}

    for stat in queryset:
        msg_type = stat["message_type"]
        month_date = stat["month"]
        month = month_date.strftime("%b %Y")
        count = stat["count"]
        error_count = error_counts.get((month_date, msg_type), 0)

        if msg_type not in data:
            data[msg_type] = []

        error_rate = round((error_count / count) * 100, 3) if count else 0
        data[msg_type].append({"x": month, "y": error_rate})

    return {
        "series": [{"name": msg_type, "data": values} for msg_type, values in data.items()]
    }


def generate_apex_line_chart_data_from_queryset(queryset: QuerySet) -> dict:
    monthly_data = {}
    months_set = set()

    for stat in queryset:
        msg_type = stat["message_type"]
        month = stat["month"].strftime("%b %Y")  # Format: "Jan 2024"
        count = stat["count"]

        months_set.add(stat["month"])

        if msg_type not in monthly_data:
            monthly_data[msg_type] = {}
        monthly_data[msg_type][month] = count

    sorted_months = sorted(list(months_set))
    categories = [month.strftime("%b %Y") for month in sorted_months]

    series = []
    for msg_type, data in monthly_data.items():
        series.append({
            "name": msg_type,
            "data": [data.get(month, 0) for month in categories]
        })

    return {
        "series": series,
        "categories": categories
    }