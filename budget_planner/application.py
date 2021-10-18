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
            "save_budget_group": self.save_budget_group,
            "overwrite_budget_group_warning": self.overwrite_budget_group_warning,
            "load_budget_group": self.load_budget_group,
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
        """Gets filepath and filename needed for saving a template. Finally calls function to save template."""

        initial_dir = self.data_model.templates_path
        self.data_model.initiate_directory(initial_dir)

        st = v.SaveTemplate(self, self.callbacks, initial_dir)
        if st.filepath:
            self.data_model.save_template_as(st.filepath)

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

    def save_budget_group(self):
        """Opens dialog to select name and location to save budget group. Then sends filepath to model to save."""

        initial_dir = self.data_model.budgets_path
        self.data_model.initiate_directory(initial_dir)

        sbg = v.SaveBudgetGroup(self, self.callbacks, initial_dir)
        if sbg.filepath:
            self.data_model.save_budget_grouping_as(sbg.filepath)

    @staticmethod
    def overwrite_budget_group_warning(group_name):
        """
        Calls function to ask if user wants to overwrite a budget group directory.
        Returns user response as True or False.
        """

        warning_class = v.MessageView()
        response = warning_class.directory_overwrite_messagebox(group_name)
        return response

    def load_budget_group(self):
        """Creates class for user to select budget grouping and then tries to open requested budget grouping."""

        initial_dir = self.data_model.budgets_path
        self.data_model.initiate_directory(initial_dir)

        lbg = v.LoadBudgetGroup(self, self.callbacks, initial_dir)
        if lbg.filepath:
            budget = self.data_model.load_template(lbg.filepath)
            if budget == 'loading_error':
                print('failure to load. wrong file type')
            else:
                if budget.get('type') == 'budget':
                    self.data_model.template_data = budget
                    current_budget = self.data_model.template_data["current_budget"]
                    self.budget_view.view_data = budget['budgets'][current_budget]
                    self.update_frames()
                else:
                    print('not a budget')

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

    def load_template(self):
        """Get filepath and filename of template. Finally, load the template"""

        initial_dir = self.data_model.templates_path
        self.data_model.initiate_directory(initial_dir)

        lt = v.LoadTemplate(self, self.callbacks, initial_dir)
        if lt.filepath:
            template = self.data_model.load_template(lt.filepath)
            if template == 'loading_error':
                print('failure to load. wrong file type')
            else:
                if template.get('type') == 'template':
                    self.data_model.template_data = template
                    self.budget_view.view_data = template['template']
                    self.update_frames()
                else:
                    print('not a template')
