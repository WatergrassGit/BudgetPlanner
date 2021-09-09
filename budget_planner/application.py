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
            "get_template_data": self.get_template_data,
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
