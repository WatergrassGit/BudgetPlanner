import os
import shutil
import json
import pickle
import pandas as pd
from decimal import Decimal
from pathlib import Path
import threading


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

    def save_as_pickle(self, fp):
        """Save current budget or template as named pickle binary file."""
        with open(fp, 'wb') as f:
            pickle.dump(self.template_data, f)

    def save_template_as_csv(self):
        """Save current budget as a template."""

        self.initiate_directory(self.templates_path)
        self.initiate_directory(Path(self.templates_path, "default_template"))

        data_groups = ['income_categories', 'expense_categories', 'transactions']
        file_names = ['income.csv', 'expense.csv', 'transaction.csv']
        for i in range(3):
            df = pd.DataFrame(self.template_data['template'][data_groups[i]])
            filepath = Path(self.templates_path, 'default_template', file_names[i])
            df.to_csv(filepath, index=False)

    @staticmethod
    def load_pickle(fp):
        """Load budget or template from a given directory."""
        with open(fp, 'rb') as f:
            try:
                result = pickle.load(f)
            except pickle.UnpicklingError:
                result = 'loading_error'
        return result

    def load_active_template(self):
        """Load currently active budget template"""
        default_path = Path(self.templates_path, "default_template")
        return self.load_budget_from_directory(default_path)

    def load_budget_from_directory(self, directory_path):
        """
        Load income, expense, and transaction .csv files from given directory and returns a dictionary.

        :argument
            directory_path (Path): A path pointing to directory to load files from
        :returns
            dict: A dictionary containing each .csv file load as a list of dictionaries
        :exception
            FileNotFoundError: When loading a missing .csv we initiate an empty dataframe
            pd.errors.EmptyDataError: When loading an empty .csv file we initiate an empty dataframe
        """

        filepaths = [
            Path(directory_path, "income.csv"),
            Path(directory_path, "expense.csv"),
            Path(directory_path, "transaction.csv"),
        ]
        dtypes = [
            {"name": str},
            {"name": str},
            {"date": str, "merchant": str, "category": str},
        ]
        converters = [
            {"hourly_pay": Decimal, "hours": Decimal, "tax_rate": Decimal},
            {"budget": Decimal},
            {"outlay": Decimal, "inflow": Decimal},
        ]

        self.initiate_directory(self.templates_path)
        self.initiate_directory(Path(self.templates_path, "default_template"))

        lods = []  # list of a list of dictionaries
        for i in range(3):
            try:
                df = pd.read_csv(filepaths[i], index_col=False, dtype=dtypes[i], converters=converters[i])
            except (FileNotFoundError, pd.errors.EmptyDataError):
                df = pd.DataFrame()
            lods.append(df.to_dict('records'))

        return {"income_categories": lods[0], "expense_categories": lods[1], "transactions": lods[2]}

    def save_budget_group(self, filepath):
        """Allows user to save a budget grouping to a directory."""

        self.initiate_directory(self.budget_data_path)
        fn = Path(filepath).stem
        if self.template_data['type'] == 'template':
            print("This is not a budget group. Use Save Template instead.")
            return

        budget_group_path = Path(self.budget_data_path, fn)

        overwrite = True
        try:
            os.mkdir(budget_group_path)
        except FileExistsError:
            overwrite = self.callbacks["overwrite_budget_group_warning"](fn)

        if overwrite:
            # save path link
            with open(filepath, mode='w') as fp:
                fp.write(str(budget_group_path))

            # save config data
            order_lod = [{"dirname": v.replace(" ", "_"), "name": v} for v in self.template_data['order']]
            config_file = {
                'type': self.template_data['type'],
                'name': self.template_data['name'],
                'current_budget': self.template_data['current_budget'],
                'order': order_lod,
            }

            self.initiate_directory(budget_group_path)
            config_fp = Path(self.budget_data_path, fn, "config.json")
            with open(config_fp, mode='w') as json_file:
                json.dump(config_file, json_file)

            # save data fields
            data_groups = ['income_categories', 'expense_categories', 'transactions']
            file_names = ['income.csv', 'expense.csv', 'transaction.csv']
            for d in order_lod:
                self.initiate_directory(Path(budget_group_path, d['dirname']))
                for i in range(3):
                    df = pd.DataFrame(self.template_data['budgets'][d['name']][data_groups[i]])
                    fp = Path(budget_group_path, d['dirname'], file_names[i])
                    df.to_csv(fp, index=False)

            # this code gets a list of all directories in the budget_group directory for the budget group being saved
            # it then removed any subdirectories which are no longer represented in the budget group
            # this could happen as a result of renaming a budget or replacing an entire budget group
            dirlist = [item for item in os.listdir(budget_group_path) if os.path.isdir(Path(budget_group_path, item))]
            for dir_ in dirlist:
                if dir_ not in [d['dirname'] for d in order_lod]:
                    shutil.rmtree(Path(budget_group_path, dir_))

    def load_budget_group(self, filepath):
        """
        Loads a budget group directory into a python dictionary.

        This is done with the following process:
            * Use argument filepath to open file and get budget group directory location
            * Load configuration file
            * Ensure we are loading a budget group
            * Load each budget in budget group based on configuration file
            * Overwrite self.template_data with budget group
            * Return bool indicating if load was successful

        :argument
            filepath (Path): A path pointing to a file containing budget group directory location
        :returns
            bool: Returns a boolean indicating if load as successful
        """

        csv_file = pd.read_csv(filepath, index_col=False, header=None)

        file_directory = Path(csv_file.iloc[0, 0])

        # step 1: load config.json
        # abort if file not found or if type is not budget
        config_path = Path(file_directory, "config.json")
        with open(config_path, mode='r') as json_file:
            data = json.load(json_file)
        if data['type'] == 'budget':
            print('this is a budget')
        else:
            print('this is not a budget')
            return False  # represents load was unsuccessful

        # step 2: load each directory in config.json based on order
        # if a directory is missing issue a warning
        data['budgets'] = {}
        for d in data['order']:
            fp = Path(file_directory, d['dirname'])
            data['budgets'][d['name']] = self.load_budget_from_directory(fp)

        data['order'] = [d['name'] for d in data['order']]
        self.template_data = data

        return True  # represents load was successful


class ProjectSettings:
    """Class to hold project settings. Uses default values whenever no other value found."""

    MAX_NUMBER_OF_RECENT_FILES = 10

    def __init__(self, master):
        self.master = master

        self.settings_changed = False
        self.settings_path = Path("budget_planner", "settings.json")

        try:  # initiate settings from file or with empty dictionary as needed
            with open(self.settings_path, mode='r') as json_file:
                self.settings = json.load(json_file)
        except FileNotFoundError:
            self.settings = {}

        self.settings.setdefault('window_size', '1280x720')
        self.settings.setdefault('recent_files', [])
        self.settings.setdefault('current_file_filepath', '')
        self.settings['current_file_filepath'] = ''  # for now this ensures default view has no associated filepath

    def update_current_file_filepath(self, fp):
        """Stores a filepath in settings dictionary with key current_file_filepath."""
        self.settings['current_file_filepath'] = fp
        self.settings_changed = True

    def reset_current_file_filepath(self):
        """Reset settings dictionary by associating current_file_filepath's key to an empty string."""
        self.settings['current_file_filepath'] = ''
        self.settings_changed = True

    def update_recent_files(self, budget_type, fp):
        """Method to add most recent file to beginning of recent_files list."""

        list_input = dict(budget_type=budget_type, filepath=fp)

        while len(self.settings['recent_files']) > self.MAX_NUMBER_OF_RECENT_FILES:
            self.settings['recent_files'].pop()

        # get all copies of list_input in the recent_files list and remove them
        indices = [i for i, x in enumerate(self.settings['recent_files']) if x == list_input]
        indices.reverse()  # reverse order to ensure we remove correct values
        for i in indices:
            self.settings['recent_files'].pop(i)

        # add list_input to the front of the list
        self.settings['recent_files'].insert(0, list_input)
        self.settings_changed = True

    def remove_from_recent_files(self, indices):
        indices.sort(reverse=True)
        for index in indices:
            self.settings['recent_files'].pop(index)
        self.settings_changed = True

    def clear_recent_files(self):
        self.settings['recent_files'] = []
        self.settings_changed = True

    def get_recent_files(self):
        return self.settings['recent_files']

    def set_window_size(self, width, height):
        self.settings_changed = self.settings['window_size'] != f"{width}x{height}"
        if self.settings_changed:
            self.settings['window_size'] = f"{width}x{height}"
            self.settings_changed = True

    def update_settings_file(self):
        if not os.path.exists(self.settings_path):
            thread = threading.Thread(target=self._save_settings)
            thread.start()
            self.settings_changed = False
        else:
            if self.settings_changed:
                thread = threading.Thread(target=self._save_settings)
                thread.start()
                self.settings_changed = False

    def _save_settings(self):
        with open(self.settings_path, mode='w') as json_file:
            json.dump(self.settings, json_file)
