import tkinter as tk
from tkinter import ttk
from . import views as v
from . import menus
from . models import ProjectModel


class Application(tk.Tk):
    """BudgetPlanner Main Application"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wm_title("Budget Planner")
        self.geometry("1280x720")

        # set up callback dictionary
        self.callbacks = {
            "save_template_as": self.save_template_as,
            "add_transaction": self.add_transaction,
            "add_category": self.add_category,
            "create_budget": self.create_budget,
            "update_frames": self.update_frames,
            "add_job": self.add_job,
            "save_budget_as": self.save_budget_as,
            "overwrite_budget_group_warning": self.overwrite_budget_group_warning,
            "load_budget": self.load_budget,
            "get_previous_budget": self.get_previous_budget,
            "get_next_budget": self.get_next_budget,
            "load_template": self.load_template,
        }

        # set up project model
        self.data_model = ProjectModel(self, self.callbacks)

        # set up menu
        self.option_add('*tearOff', False)
        self.main_menu = menus.MainMenu(self, self.callbacks)
        self.config(menu=self.main_menu)

        # set up budget view
        self.budget_view = v.BudgetView(self, self.callbacks)
        self.budget_view.grid(column=0, row=0, sticky='nsew')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def save_template_as(self):
        """Sends basic template information to save_as for further processing."""
        initial_dir = self.data_model.templates_path
        self.save_as(initial_dir=initial_dir, filename="new_template.pkl", file_type="template")

    def save_budget_as(self):
        """Sends basic budget information to save_as for further processing."""
        initial_dir = self.data_model.budgets_path
        self.save_as(initial_dir=initial_dir, filename="new_budget.pkl", file_type="budget")

    def save_as(self, initial_dir, filename, file_type):
        """Save template or budget."""

        # before finalizing the save operations ensure we are saving the correct type of data
        if self.data_model.template_data.get('type') == file_type:
            self.data_model.initiate_directory(initial_dir)
            mask = [("Pickle files", "*.pkl"), ("All files", "*.*")]
            title = f"Save {file_type.title()} As"

            sp = v.SavePickle(initial_dir, filename=filename, title=title, mask=mask)
            if sp.filepath:
                self.data_model.save_as_pickle(sp.filepath)
        else:
            print(f"Your data is not of type {file_type}!")

    def get_template_data(self):
        """Wrapper to call get_template_data method from data_model."""
        return self.data_model.get_template_data()

    def add_category(self):
        """Used to call add_category from BudgetView"""
        self.budget_view.add_category()

    def add_job(self):
        """Used to call add_job from BudgetView"""
        self.budget_view.add_job()

    def add_transaction(self):
        """Used to call add_transaction from BudgetView"""
        self.budget_view.add_transaction()

    def create_budget(self):
        v.CreateBudget(self, self.callbacks)

    def update_frames(self):
        self.budget_view.update_frames()

    @staticmethod
    def overwrite_budget_group_warning(group_name):
        """
        Calls function to ask if user wants to overwrite a budget group directory.
        Returns user response as True or False.
        """

        warning_class = v.MessageView()
        response = warning_class.directory_overwrite_messagebox(group_name)
        return response

    def load_template(self):
        initial_dir = self.data_model.templates_path
        self.load(initial_dir=initial_dir, file_type='template')

    def load_budget(self):
        initial_dir = self.data_model.budgets_path
        self.load(initial_dir=initial_dir, file_type='budget')

    def load(self, initial_dir, file_type):
        """Load template or budget."""

        self.data_model.initiate_directory(initial_dir)
        mask = [("Pickle files", "*.pkl"), ("All files", "*.*")]
        title = f"Load {file_type.title()}"

        lp = v.LoadPickle(initial_dir, title, mask)
        if lp.filepath:
            result = self.data_model.load_pickle(lp.filepath)
            if result == 'loading_error':
                print('Failure to load. Wrong file type.')
            else:
                if result.get('type', '') == file_type == 'template':
                    self.data_model.template_data = result
                    self.budget_view.view_data = result['template']
                    self.update_frames()
                elif result.get('type', '') == file_type == 'budget':
                    self.data_model.template_data = result
                    current_budget = self.data_model.template_data["current_budget"]
                    self.budget_view.view_data = result['budgets'][current_budget]
                    self.update_frames()
                else:
                    print(f'Not a {file_type}.')

    def load_budget_group_old(self):
        """Creates class for user to select budget grouping and then tries to open requested budget grouping."""
        lb = v.LoadBudget(self, self.callbacks)
        success = False
        if lb.filepath:
            success = self.data_model.load_budget_group(lb.filepath)
        if success:
            current_budget = self.data_model.template_data["current_budget"]
            self.budget_view.view_data = self.data_model.template_data['budgets'][current_budget]
            self.update_frames()

    def get_previous_budget(self):
        if self.data_model.template_data['type'] == 'template':
            print("This is a template.")
            return
        current_budget = self.data_model.template_data['current_budget']
        placement = self.data_model.template_data['order'].index(current_budget)
        if placement > 0:
            previous_budget = self.data_model.template_data['order'][placement - 1]
        else:
            print("There are no earlier budgets!")
            return
        self.data_model.template_data["current_budget"] = previous_budget
        self.budget_view.view_data = self.data_model.template_data['budgets'][previous_budget]
        self.update_frames()

    def get_next_budget(self):
        if self.data_model.template_data['type'] == 'template':
            print("This is a template.")
            return
        current_budget = self.data_model.template_data['current_budget']
        placement = self.data_model.template_data['order'].index(current_budget)
        try:
            next_budget = self.data_model.template_data['order'][placement + 1]
            self.data_model.template_data["current_budget"] = next_budget
            self.budget_view.view_data = self.data_model.template_data['budgets'][next_budget]
            self.update_frames()
        except IndexError:
            warning_class = v.MessageView()
            create_next_budget = warning_class.create_next_budget_messagebox()  # asks if we want to create a new budget
            if create_next_budget:
                v.AddNextBudget(self, self.callbacks, current_budget, self.create_new_budget)

    def create_new_budget(self, new_budget, template='blank'):
        """Uses view info to append a budget to the current budget group and then update the view."""

        penultimate = self.data_model.template_data["current_budget"]

        self.data_model.template_data["current_budget"] = new_budget
        self.data_model.template_data["order"].append(new_budget)
        if template == 'saved':  # currently set to blank
            self.data_model.template_data['budgets'][new_budget] = {
                'income_categories': [],
                'expense_categories': [],
                'transactions': [],
            }
        elif template == 'previous':
            self.data_model.template_data['budgets'][new_budget] = {
                'income_categories': self.data_model.template_data['budgets'][penultimate]['income_categories'],
                'expense_categories': self.data_model.template_data['budgets'][penultimate]['expense_categories'],
                'transactions': [],
            }
        else:  # default or when template='blank'
            self.data_model.template_data['budgets'][new_budget] = {
                'income_categories': [],
                'expense_categories': [],
                'transactions': [],
            }
        self.budget_view.view_data = self.data_model.template_data['budgets'][new_budget]
        self.update_frames()
