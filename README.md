## Internal IT Helpdesk & Asset Management System

This is a simple internal IT helpdesk and asset management system built with **Django** and **SQLite3**.

### Tech Stack

- Backend: Django
- Database: SQLite3
- Frontend: Django Templates + Bootstrap 5

### Setup Instructions

1. **Create and activate a virtual environment** (recommended).

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Apply migrations**:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create a superuser** (for initial admin access and managing groups/users):

```bash
python manage.py createsuperuser
```

5. **Run the development server**:

```bash
python manage.py runserver
```

6. **Access the app**:

- Login: `/login/`
- Employee dashboard: `/employee/dashboard/`
- IT admin dashboard: `/admin/dashboard/`

Make sure at least one user is added to the **IT Admin** group (via the Django admin site) so they can access the IT admin-only pages.

