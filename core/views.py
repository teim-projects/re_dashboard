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
from django.utils.text import slugify
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
import pandas as pd

from accounts.models import EnergyType


from django.contrib.auth.models import User


from django.db import connection
from django.utils.text import slugify
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
import pandas as pd

from accounts.models import EnergyType

from django.contrib.auth.models import User

import traceback
import pandas as pd
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib.auth.models import User
# from .models import Provider, EnergyType


import os
import pandas as pd
import traceback
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.contrib.auth.models import User


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db import connection
# from .models import Provider, EnergyType
from django.contrib.auth.models import User
import pandas as pd
import traceback
import os

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db import connection
# from .models import Provider, EnergyType
from django.contrib.auth.models import User
import pandas as pd
import traceback
import os
import re  # ✅ for cleaning column names

@login_required
def upload_files(request):
    energy_types = EnergyType.objects.all()
    providers = Provider.objects.all()

    # ✅ Fetch all existing DB tables
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        db_tables = [row[0] for row in cursor.fetchall()]

    # ✅ Build username_provider_energytype style labels
    expected_tables = []
    for table in db_tables:
        parts = table.split('_')
        if len(parts) >= 3:
            username = parts[0]
            provider_slug = '_'.join(parts[1:-1])
            energy_type_slug = parts[-1]
            if Provider.objects.filter(name__iexact=provider_slug.replace('_', ' ')).exists() and \
               EnergyType.objects.filter(name__iexact=energy_type_slug.replace('_', ' ')).exists():
                expected_tables.append({
                    'name': table,
                    'label': f"{username} - {provider_slug.replace('_', ' ').title()} - {energy_type_slug.title()}"
                })

    if request.method == 'POST':
        table_name = request.POST.get('provider', '').strip()
        data_file = request.FILES.get('data_file')

        if not table_name or not data_file:
            messages.error(request, "Both table and file are required.")
            return redirect('upload_files')

        try:
            parts = table_name.split('_')
            uploaded_by = parts[0]
            energy_type = parts[-1].replace('_', ' ').title()
        except Exception:
            messages.error(request, "Invalid table format.")
            return redirect('upload_files')

        fs = FileSystemStorage()
        filename = fs.save(data_file.name, data_file)
        file_path = fs.path(filename)

        try:
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext in ['.xls', '.xlsx', '.xlsm', '.ods', '.odt']:
                df = pd.read_excel(file_path, engine='odf' if ext in ['.ods', '.odt'] else None)
            else:
                raise Exception("Unsupported file format.")

            # ✅ Clean column names (replace spaces, dots, %, etc.)
            df.columns = [re.sub(r'\W+', '_', col.strip()).lower().strip('_') for col in df.columns]

            # ✅ Fetch table columns from DB
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                table_columns = [col[0].lower() for col in cursor.fetchall()]

            # ✅ Check for missing columns
            missing_cols = [col for col in df.columns if col not in table_columns]
            if missing_cols:
                raise Exception(f"Columns not found in table `{table_name}`: {missing_cols}")

            # ✅ Add extra fields if present
            if 'energy_type' in table_columns:
                df['energy_type'] = energy_type
            if 'uploaded_by' in table_columns:
                df['uploaded_by'] = uploaded_by

            # ✅ Insert data row by row
            rows_inserted = 0
            with connection.cursor() as cursor:
                for index, row in df.iterrows():
                    try:
                        columns = ', '.join(f"`{col}`" for col in df.columns)
                        placeholders = ', '.join(['%s'] * len(row))
                        values = list(row.values)
                        insert_sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
                        cursor.execute(insert_sql, values)
                        rows_inserted += 1
                    except Exception as row_error:
                        print(f"❌ Skipped row {index + 1}: {row_error}")

            if rows_inserted > 0:
                messages.success(request, f"✅ Uploaded {rows_inserted} rows to '{table_name}'.")
            else:
                messages.error(request, "❌ Upload failed: No rows inserted. Check file structure.")

        except Exception as e:
            print("🔥 Upload failed:\n", traceback.format_exc())
            messages.error(request, f"❌ Upload failed: {str(e)}")
        finally:
            fs.delete(filename)

        return redirect('upload_files')

    return render(request, 'upload_files.html', {
        'expected_tables': expected_tables,
        'providers': providers,
        'energy_types': energy_types,
        'staff_users': User.objects.filter(is_superuser=False),
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
    energy_types = EnergyType.objects.all()
    providers = Provider.objects.all()

    # Fetch all actual tables from DB
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        db_tables = [row[0] for row in cursor.fetchall()]

    # Match pattern: username_provider_energytype
    expected_tables = []
    for table in db_tables:
        parts = table.split('_')
        if len(parts) >= 3:
            username = parts[0]
            provider_slug = '_'.join(parts[1:-1])
            energy_type_slug = parts[-1]

            # Recheck if valid provider + energy type
            if Provider.objects.filter(name__iexact=provider_slug.replace('_', ' ')).exists() and \
               EnergyType.objects.filter(name__iexact=energy_type_slug.replace('_', ' ')).exists():
                expected_tables.append({
                    'name': table,
                    'label': f"{username} - {provider_slug.replace('_', ' ').title()} - {energy_type_slug.title()}"
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
