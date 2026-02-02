from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create 10 default employee users"

    def handle(self, *args, **kwargs):

        employees = [
            ("emp1", "Emp@12345"),
            ("emp2", "Emp@12345"),
            ("emp3", "Emp@12345"),
            ("emp4", "Emp@12345"),
            ("emp5", "Emp@12345"),
            ("emp6", "Emp@12345"),
            ("emp7", "Emp@12345"),
            ("emp8", "Emp@12345"),
            ("emp9", "Emp@12345"),
            ("emp10", "Emp@12345"),
        ]

        for username, password in employees:
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"{username} already exists")
            else:
                User.objects.create_user(username=username, password=password)
                self.stdout.write(f"Created employee: {username}")

        self.stdout.write("✅ 10 Employees Created Successfully!")
