from django.shortcuts import render

def wind_dashboard(request):
    return render(request, 'wind_dashboard.html')  # Wind Dashboard

from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.utils import ProgrammingError

@login_required
def wind_summary1(request):
    table_name = "installation_summary_lwind"
    data = {
        "capacity_by_state": [],
        "land_type_by_state": [],
        "wtg_generation": [],
        "power_sale": [],
    }
    table_exists = True  # flag for SweetAlert

    try:
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

            # Estimated generation WTG wise
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

    except ProgrammingError:
        # Table not found → just return empty tables, no error
        table_exists = False

    return render(request, "wind_summary1.html", {
        "data": data,
        "table_exists": table_exists,
        "table_name": table_name
    })

import json
from django.shortcuts import render
from django.db import connection
from django.db.utils import ProgrammingError
from django.contrib.auth.decorators import login_required

@login_required
def wind_installation_summary2(request):
    table_name = "installation_summary_wind"

    data = {
        "power_sale_labels": [],
        "power_sale_counts": [],
        "land_labels": [],
        "land_counts": [],
    }
    wtg_locations = []
    oem_breakup = []

    with connection.cursor() as cursor:
        # Power Sale
        cursor.execute(f"""
            SELECT 
                CASE 
                    WHEN power_sale_details = 'Private PPA' THEN 'Captive'
                    WHEN power_sale_details IN ('SECI', 'State Grid') THEN 'Sale FB'
                    ELSE 'Other'
                END AS category,
                COUNT(*) AS cnt
            FROM `{table_name}`
            GROUP BY category
        """)
        for row in cursor.fetchall():
            data["power_sale_labels"].append(row[0])
            data["power_sale_counts"].append(row[1])

        # Land
        cursor.execute(f"SELECT land, COUNT(*) FROM `{table_name}` GROUP BY land")
        for row in cursor.fetchall():
            data["land_labels"].append(row[0])
            data["land_counts"].append(row[1])

        # ✅ Table 1: WTG Locations
        cursor.execute(f"""
            SELECT wtg_location_no, avg_estimate_gen_kwh
            FROM `{table_name}`
            ORDER BY avg_estimate_gen_kwh DESC
            LIMIT 10
        """)
        wtg_locations = cursor.fetchall()

        # ✅ Table 2: OEM Breakup
        cursor.execute(f"""
            SELECT capacity_mw, firm, make, COUNT(*)
            FROM `{table_name}`
            GROUP BY capacity_mw, firm, make
        """)
        oem_breakup = cursor.fetchall()

    return render(request, "wind_installation_summary2.html", {
        "data": json.dumps(data),
        "wtg_locations": wtg_locations,
        "oem_breakup": oem_breakup
    })
