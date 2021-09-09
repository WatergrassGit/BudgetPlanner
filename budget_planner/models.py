import os
import json
from decimal import Decimal
from pathlib import Path


class ProjectModel:
    """A class for interacting with external files."""

    def __init__(self):
        self.templates_path = Path("budget_planner", "templates")

        self.initiate_template_directory()

        # initiate template dict
        self.template_data = {}
        self.get_template_data()

    def get_template_data(self):
        """
        Method to extract template data from a file. If bad data is given it will either revert to previous
        template with an error or create new default / empty template if no previous template was loaded.
        """

        self.template_data = {
            'income_categories': ['Other'],  # list of strings
            # list of dictionaries with category name and category budget
            'expense_categories': [{'Miscellaneous': Decimal('0.00')}],
            # list of dictionaries with name / hourly_pay / hours
            'job_list': [{'name': 'Main', 'hourly_pay': Decimal('15.00'), 'hours': Decimal('120.00')}],
            # transaction list contains dictionaries with date / location / category / payment / deposit
            'transaction_list': [
                {
                    'date': '1970-01-01',
                    'location': 'Home',
                    'category': 'Miscellaneous',
                    'payment': Decimal('100.00'),
                    'deposit': Decimal('0.00')
                }
            ]
        }
        # filepath = Path(self.templates_path, "template.json")
        return self.template_data

    def initiate_template_directory(self):
        """Ensures template directory exists. If not it creates a new directory."""

        try:
            os.mkdir(self.templates_path)
        except FileExistsError:
            pass

    def save_template_as(self):
        """Save current budget as a template."""

        # note: this version needs to add feature to name template
        filepath = Path(self.templates_path, "template.json")
        data = {'hello': '5'}
        self.initiate_template_directory()
        with open(filepath, mode='w') as json_file:
            json.dump(data, json_file)
        # print(template_name)
