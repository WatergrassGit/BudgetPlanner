import os
import json
import pandas as pd
from decimal import Decimal
from pathlib import Path


class ProjectModel:
    """A class for interacting with external files."""

    def __init__(self, master, callbacks):
        self.master = master
        self.callbacks = callbacks

        self.templates_path = Path("budget_planner", "templates")
        self.budgets_path = Path("budget_planner", "budgets")
        self.budget_data_path = Path("budget_planner", "budget_data")

        # initiate template dictionary and load data from file or default
        self.template_data = {}
        self.get_template_data()

    def get_template_data(self):
        """
        Method to extract template data from a file. If bad data is given it will either revert to previous
        template with an error or create new default / empty template if no previous template was loaded.
        """

        template = self.load_active_template()

        self.template_data['type'] = 'template'
        self.template_data['name'] = 'Template'

        if template:
            self.template_data['template'] = template
        else:  # use default template
            template = {
                # list of dictionaries with name / hourly_pay / hours
                'income_categories': [
                    {
                        'name': 'Main',
                        'hourly_pay': Decimal('15.00'),
                        'hours': Decimal('120.00'),
                        'tax_rate': Decimal('0.2')
                    },
                    {
                        'name': 'Other',
                        'hourly_pay': Decimal('12.00'),
                        'hours': Decimal('10.00'),
                        'tax_rate': Decimal('0.15')
                    }
                ],
                # list of dictionaries with category name and category budget
                'expense_categories': [
                    {
                        'name': 'Food',
                        'budget': Decimal('120.00'),
                    },
                    {
                        'name': 'Miscellaneous',
                        'budget': Decimal('0.00'),
                    }
                ],
                # transaction list contains dictionaries with date / location / category / payment / deposit
                'transactions': [
                    {
                        'date': '1970-01-01',
                        'merchant': 'Home',
                        'category': 'Miscelaneous',
                        'outlay': Decimal('100.00'),
                        'inflow': Decimal('0.00')
                    },
                    {
                        'date': '1970-01-01',
                        'merchant': 'Home',
                        'category': 'Miscellaneous',
                        'outlay': Decimal('100.00'),
                        'inflow': Decimal('0.00')
                    },
                    {
                        'date': '1970-01-01',
                        'merchant': 'Main',
                        'category': 'Income',
                        'outlay': Decimal('100.00'),
                        'inflow': Decimal('900.00')
                    },
                    {
                        'date': '1970-01-01',
                        'merchant': 'Home',
                        'category': 'Food',
                        'outlay': Decimal('50.00'),
                        'inflow': Decimal('0.00')
                    }
                ]
            }
            self.template_data['template'] = template

    @staticmethod
    def initiate_directory(directory):
        """Ensures given directory exists. If not it creates the directory."""

        try:
            os.mkdir(directory)
        except FileExistsError:
            pass

    def save_template_as(self):
        """Save current budget as a template."""

        self.initiate_directory(self.templates_path)
        self.initiate_directory(Path(self.templates_path, "default_template"))

        data_groups = ['income_categories', 'expense_categories', 'transactions']
        file_names = ['income.csv', 'expense.csv', 'transaction.csv']
        for i in range(3):
            df = pd.DataFrame(self.template_data['template'][data_groups[i]])
            filepath = Path(self.templates_path, 'default_template', file_names[i])
            df.to_csv(filepath, index=False)

    def load_active_template(self):
        """Load currently active budget template"""

        income_filepath = Path(self.templates_path, "default_template", "income.csv")
        expense_filepath = Path(self.templates_path, "default_template", "expense.csv")
        transaction_filepath = Path(self.templates_path, "default_template", "transaction.csv")

        self.initiate_directory(self.templates_path)
        self.initiate_directory(Path(self.templates_path, "default_template"))
        try:
            income_df = pd.read_csv(income_filepath, index_col=False,
                                    dtype={"name": str},
                                    converters={"hourly_pay": Decimal, "hours": Decimal, "tax_rate": Decimal})
        except FileNotFoundError:
            return ''
        except pd.errors.EmptyDataError:
            income_df = pd.DataFrame()
        income_lod = income_df.to_dict('records')  # list of dictionaries
        try:
            expense_df = pd.read_csv(expense_filepath, index_col=False,
                                     dtype={"name": str},
                                     converters={"budget": Decimal})
        except FileNotFoundError:
            return ''
        except pd.errors.EmptyDataError:
            expense_df = pd.DataFrame()
        expense_lod = expense_df.to_dict('records')  # list of dictionaries
        try:
            transaction_df = pd.read_csv(transaction_filepath, index_col=False,
                                         dtype={"date": str, "merchant": str, "category": str},
                                         converters={"outlay": Decimal, "inflow": Decimal})
        except FileNotFoundError:
            return ''
        except pd.errors.EmptyDataError:
            transaction_df = pd.DataFrame()
        transaction_lod = transaction_df.to_dict('records')  # list of dictionaries

        return_file = {
            "income_categories": income_lod,
            "expense_categories": expense_lod,
            "transactions": transaction_lod}

        return return_file

    def save_budget_group(self, filepath):
        """Allows user to save a budget grouping to a directory."""

        if self.template_data['type'] == 'template':
            print("This is not a budget group. Use Save Template instead.")
            return

        self.initiate_directory(self.budget_data_path)

        # save path link
        with open(filepath, mode='w') as json_file:
            json.dump({'key': str(Path(self.budget_data_path, Path(filepath).name))}, json_file)

        # save config data
        order_lod = [{v.replace(" ", "_"): v} for v in self.template_data['order']]
        config_file = {
            'name': self.template_data['name'],
            'current_budget': self.template_data['current_budget'],
            'order': order_lod,
        }

        try:
            os.mkdir(Path(self.budget_data_path, Path(filepath).stem))
        except FileExistsError:
            pass

        with open(Path(self.budget_data_path, Path(filepath).stem, "config.json"), mode='w') as json_file:
            json.dump(config_file, json_file)

        # save data fields
        data_groups = ['income_categories', 'expense_categories', 'transactions']
        file_names = ['income.csv', 'expense.csv', 'transaction.csv']
        for d in order_lod:
            try:
                os.mkdir(Path(self.budget_data_path, Path(filepath).stem, list(d.keys())[0]))
            except FileExistsError:
                pass
            for i in range(3):
                df = pd.DataFrame(self.template_data[list(d.values())[0]][data_groups[i]])
                fp = Path(Path(self.budget_data_path, Path(filepath).stem), list(d.keys())[0], file_names[i])
                df.to_csv(fp, index=False)
