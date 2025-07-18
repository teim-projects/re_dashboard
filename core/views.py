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


@login_required
def upload_files(request):
    energy_types = EnergyType.objects.all()
    staff_users = User.objects.filter(is_superuser=False)
    providers = Provider.objects.all()

    if request.method == 'POST':
        provider = request.POST.get('provider', '').strip().lower().replace(' ', '_')
        energy_type_id = request.POST.get('energy_type')
        user_id = request.POST.get('user_id')
        data_file = request.FILES.get('data_file')

        if not (provider and energy_type_id and user_id and data_file):
            messages.error(request, "All fields are required.")
            return redirect('upload_files')

        table_name = f"{provider}_data"

        # Fetch actual names instead of IDs
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

        # Save file temporarily
        fs = FileSystemStorage()
        filename = fs.save(data_file.name, data_file)
        file_path = fs.path(filename)

        try:
            # Read uploaded file
            df = pd.read_csv(file_path) if filename.endswith('.csv') else pd.read_excel(file_path)

            # Add readable info instead of IDs
            df['energy_type'] = energy_type_name
            df['uploaded_by'] = uploaded_by

            # Clean column names (convert headers to SQL-compatible format)
            df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

            # Insert into DB
            with connection.cursor() as cursor:
                for _, row in df.iterrows():
                    columns = ', '.join(f"`{col}`" for col in df.columns)
                    placeholders = ', '.join(['%s'] * len(row))
                    values = list(row.values)

                    insert_sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, values)

            messages.success(request, f"✅ Data successfully inserted into '{table_name}'.")

        except Exception as e:
            messages.error(request, f"❌ Failed to upload data: {str(e)}")

        finally:
            fs.delete(filename)

        return redirect('upload_files')

    return render(request, 'upload_files.html', {
        'energy_types': energy_types,
        'staff_users': staff_users,
        'providers': providers,
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
 
 
 
