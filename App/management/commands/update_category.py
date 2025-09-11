from django.core.management.base import BaseCommand
import pandas as pd
from App.models import DoctorAgentList


class Command(BaseCommand):
    help = "Update category from Excel file (Sheet2)."

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help="Path to the Excel file")

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        df = pd.read_excel(excel_file, sheet_name="Sheet2")

        for _, row in df.iterrows():
            unique_id = str(row['unique_id']).strip()
            category = str(row['category']).strip()

            updated = DoctorAgentList.objects.filter(unique_id=unique_id).update(
                category=category
            )
            if updated:
                self.stdout.write(self.style.SUCCESS(f"Updated category for {unique_id}"))
            else:
                self.stdout.write(self.style.WARNING(f"Unique ID {unique_id} not found"))
