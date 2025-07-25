from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required


def index_page(request):
  return render(request, 'index.html')


@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser:
        return render(request, 'home.html')  # Admin dashboard
    else:
        return render(request, 'customer_home.html')  # Regular user dashboard
    

import pandas as pd
from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from accounts.models import EnergyType
from accounts.models import Provider  # Assuming model is in `core`
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import pandas as pd
import os

from django.contrib.auth.decorators import login_required
from accounts.models import EnergyType
from django.contrib.auth.models import User


from django.db import connection

from django.db import connection
from django.utils.text import slugify

@login_required
def upload_files(request):
    energy_types = EnergyType.objects.all()
    staff_users = User.objects.filter(is_superuser=False)
    providers = Provider.objects.all()

    # ✅ Step 1: Get all actual tables from DB
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        db_tables = [row[0] for row in cursor.fetchall()]

    # ✅ Step 2: Build only expected provider-energy_type table names
    expected_tables = []
    for provider in providers:
        for energy in energy_types:
            table_name = f"{slugify(provider.name)}_{slugify(energy.name)}"
            if table_name in db_tables:
                expected_tables.append({
                    'name': table_name,
                    'label': f"{provider.name.title()} - {energy.name.title()}"
                })

    if request.method == 'POST':
        provider = request.POST.get('provider', '').strip().lower().replace(' ', '_')
        energy_type_id = request.POST.get('energy_type')
        user_id = request.POST.get('user_id')
        data_file = request.FILES.get('data_file')

        if not (provider and energy_type_id and user_id and data_file):
            messages.error(request, "All fields are required.")
            return redirect('upload_files')

        table_name = provider  # full table name like suzlon_wind

        try:
            energy_type = EnergyType.objects.get(id=energy_type_id)
            energy_type_name = energy_type.name
        except EnergyType.DoesNotExist:
            messages.error(request, "Invalid energy type selected.")
            return redirect('upload_files')

        try:
            user = User.objects.get(id=user_id)
            uploaded_by = user.username
        except User.DoesNotExist:
            messages.error(request, "Invalid user selected.")
            return redirect('upload_files')

        fs = FileSystemStorage()
        filename = fs.save(data_file.name, data_file)
        file_path = fs.path(filename)

        try:
            df = pd.read_csv(file_path) if filename.endswith('.csv') else pd.read_excel(file_path)
            df['energy_type'] = energy_type_name
            df['uploaded_by'] = uploaded_by
            df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

            with connection.cursor() as cursor:
                for _, row in df.iterrows():
                    columns = ', '.join(f"`{col}`" for col in df.columns)
                    placeholders = ', '.join(['%s'] * len(row))
                    values = list(row.values)
                    insert_sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, values)

            messages.success(request, f"✅ Data inserted into '{table_name}'.")

        except Exception as e:
            messages.error(request, f"❌ Failed: Invalid Format ")
        finally:
            fs.delete(filename)

        return redirect('upload_files')

    return render(request, 'upload_files.html', {
        'energy_types': energy_types,
        'staff_users': staff_users,
        'providers': providers,
        'expected_tables': expected_tables,  # ✅ pass only valid ones
    })


@login_required
def modify_data(request):
  return render(request,'modify_data.html')

@login_required
def manage_user(request):
   return render(request, 'manageUsers.html')

@login_required
def client_info(request):
   return render(request, 'client_info.html')
 
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils.text import slugify
from django.contrib.auth.models import User


 

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils.text import slugify
from django.contrib.auth.models import User
from accounts.models import Provider, EnergyType  # Adjust this import as needed

@login_required
def modify_data(request):
    users = User.objects.filter(is_superuser=False)
    providers = Provider.objects.all()
    energy_types = EnergyType.objects.all()

    # Get all real tables in DB
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        db_tables = [row[0] for row in cursor.fetchall()]

    # Only show tables that were created using Add Provider logic
    expected_tables = []
    for provider in providers:
        for energy in energy_types:
            table_name = f"{slugify(provider.name)}_{slugify(energy.name)}"
            if table_name in db_tables:
                expected_tables.append({
                    'name': table_name,
                    'label': f"{provider.name.title()} - {energy.name.title()}"
                })

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        table_name = request.POST.get("table_name")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not all([user_id, table_name, start_date, end_date]):
            messages.error(request, "❌ All fields are required.")
            return redirect("modify_data")

        try:
            with connection.cursor() as cursor:
                delete_sql = f"""
                    DELETE FROM `{table_name}`
                    WHERE uploaded_by = (
                        SELECT username FROM auth_user WHERE id = %s
                    )
                    AND date BETWEEN %s AND %s
                """
                cursor.execute(delete_sql, [user_id, start_date, end_date])
            messages.success(request, "✅ Data deleted successfully.")
        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
        return redirect("modify_data")

    return render(request, "modify_data.html", {
        "users": users,
        "expected_tables": expected_tables
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import connection
import pandas as pd


from django.utils.text import slugify
from accounts.models import UserProfile  # already linked to User
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.utils.text import slugify
from django.contrib.auth.models import User

import pandas as pd

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.contrib.auth.models import User
from accounts.models import EnergyType  # make sure this import is correct

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from django.db import connection
import pandas as pd

from django.contrib.auth.models import User
from accounts.models import EnergyType


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from django.db import connection
import pandas as pd
from django.contrib.auth.models import User
from accounts.models import EnergyType

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from django.db import connection
import pandas as pd
from accounts.models import EnergyType

@login_required
def upload_installation_summary(request):
    energy_types = EnergyType.objects.all()

    if request.method == 'POST':
        energy_type_id = request.POST.get('energy_type')
        file = request.FILES.get('file')

        if not energy_type_id or not file:
            messages.error(request, "All fields are required.")
            return redirect('upload_installation_summary')

        try:
            energy_type = EnergyType.objects.get(id=energy_type_id)
        except EnergyType.DoesNotExist:
            messages.error(request, "Invalid energy type.")
            return redirect('upload_installation_summary')

        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        try:
            # Read only the headers (ignore data rows)
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=0)
            else:
                df = pd.read_excel(file_path, nrows=0)

            # Normalize headers
            user_columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

            # Prepend 'customer' (from request.user) and 'energy_type'
            final_columns = ['customer', 'energy_type'] + user_columns

            # Table name based on energy type
            table_name = f"installation_summary_{slugify(energy_type.name)}"

            with connection.cursor() as cursor:
                columns_sql = ", ".join([f"`{col}` TEXT" for col in final_columns])
                cursor.execute(f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_sql})")

            messages.success(request, f"✅ Structure created successfully for table `{table_name}`.")

        except Exception as e:
            messages.error(request, f"❌ Upload failed: {str(e)}")

        finally:
            fs.delete(filename)

        return redirect('upload_installation_summary')

    return render(request, 'upload_installation_summary.html', {
        'energy_types': energy_types,
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from django.db import connection
import pandas as pd

from django.contrib.auth.models import User
from accounts.models import EnergyType


@login_required
def upload_installation_data(request):
    customers = User.objects.filter(is_superuser=False)
    energy_types = EnergyType.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        energy_type_id = request.POST.get('energy_type')
        file = request.FILES.get('file')

        if not user_id or not energy_type_id or not file:
            messages.error(request, "All fields are required.")
            return redirect('upload_installation_data')

        try:
            user = User.objects.get(id=user_id)
            energy_type = EnergyType.objects.get(id=energy_type_id)
        except (User.DoesNotExist, EnergyType.DoesNotExist):
            messages.error(request, "Invalid user or energy type.")
            return redirect('upload_installation_data')

        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Add metadata
            df['uploaded_by'] = request.user.username
            df['customer'] = user.username
            df['energy_type'] = energy_type.name
            df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

            table_name = f"installation_summary_{slugify(energy_type.name)}"

            # Fetch table columns from database
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                db_columns = [row[0] for row in cursor.fetchall()]

            # Validate that uploaded columns match existing table
            missing_cols = set(db_columns) - set(df.columns)
            if missing_cols:
                messages.error(request, f"Uploaded file is missing columns: {', '.join(missing_cols)}")
                return redirect('upload_installation_data')

            # Reorder columns to match DB order
            df = df[db_columns]

            with connection.cursor() as cursor:
                for _, row in df.iterrows():
                    columns = ", ".join(f"`{col}`" for col in df.columns)
                    placeholders = ", ".join(["%s"] * len(row))
                    values = list(row.values)
                    cursor.execute(f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})", values)

            messages.success(request, f"✅ Data uploaded successfully into `{table_name}`.")
        except Exception as e:
            messages.error(request, f"❌ Upload failed: {str(e)}")
        finally:
            fs.delete(filename)

        return redirect('upload_installation_data')

    return render(request, 'upload_installation_data.html', {
        'customers': customers,
        'energy_types': energy_types,
    })





 

from django.http import HttpResponse
from django.utils.text import slugify
from django.db import connection
import pandas as pd
import io

@login_required
def download_template(request):
    energy_type_id = request.GET.get('energy_type')

    if not energy_type_id:
        return HttpResponse("Energy Type is required.", status=400)

    try:
        energy_type = EnergyType.objects.get(id=energy_type_id)
    except EnergyType.DoesNotExist:
        return HttpResponse("Invalid energy type.", status=400)

    table_name = f"installation_summary_{slugify(energy_type.name)}"

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
            columns = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        return HttpResponse(f"Error reading table structure: {str(e)}", status=500)

    # Remove system columns
    exclude_columns = {'customer', 'energy_type'}
    filtered_columns = [col for col in columns if col not in exclude_columns]

    # Create empty DataFrame with just user-uploaded columns
    df = pd.DataFrame(columns=filtered_columns)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{table_name}_template.xlsx"'
    return response
