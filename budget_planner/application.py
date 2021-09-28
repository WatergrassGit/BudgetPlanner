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
        }

        # set up project model
        self.data_model = ProjectModel()

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
        """Wrapper to call save_template_as method from data_model."""
        self.data_model.save_template_as()

    def get_template_data(self):
        """Wrapper to call get_template_data method from data_model."""
        return self.data_model.get_template_data()

    def add_category(self):
        """Used to call add_category from BudgetView"""
        self.budget_view.add_category()

    def add_transaction(self):
        """Used to call add_transaction from BudgetView"""
        self.budget_view.add_transaction()

    def create_budget(self):
        v.CreateBudget(self, self.callbacks)

    def update_frames(self):
        self.budget_view.update_frames()
