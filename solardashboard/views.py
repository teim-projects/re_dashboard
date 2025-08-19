from django.shortcuts import render

# Create your views here.
def solar_dashboard(request):
    return render(request, 'solar_dashboard.html')  # Solar Dashboard
from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db import connection
from django.shortcuts import render
@login_required
def solar_summary1(request):
    table_name = "installation_summary_wind"
    data = {}

    with connection.cursor() as cursor:
        # Capacity by state
        cursor.execute(f"""
            SELECT state, SUM(capacity_mw) AS total_capacity
            FROM `{table_name}`
            GROUP BY state
        """)
        data["capacity_by_state"] = cursor.fetchall()

        # Land type by state
        cursor.execute(f"""
            SELECT state, land, COUNT(*) AS land_count
            FROM `{table_name}`
            GROUP BY state, land
        """)
        data["land_type_by_state"] = cursor.fetchall()

        # Estimated generation WTG wise (correct column)
        cursor.execute(f"""
            SELECT wtg_location_no, avg_estimate_gen_kwh
            FROM `{table_name}`
        """)
        data["wtg_generation"] = cursor.fetchall()

        # Power sale by state
        cursor.execute(f"""
            SELECT power_sale_details, state
            FROM `{table_name}`
        """)
        data["power_sale"] = cursor.fetchall()

    return render(request, "solar_summary1.html", {"data": data})
