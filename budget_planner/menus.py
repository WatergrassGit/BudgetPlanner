import tkinter as tk


class MainMenu(tk.Menu):
    """Main Menu Class"""

    def __init__(self, master, callbacks, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.callbacks = callbacks

        # set up menus
        self.menu_file = tk.Menu(self)
        self.menu_edit = tk.Menu(self)
        self.menu_options = tk.Menu(self)
        self.menu_view = tk.Menu(self)
        self.menu_help = tk.Menu(self)

        # add items to file menu
        self.menu_file.add_command(label="New Budget...", command=self.callbacks["create_budget"])
        self.menu_file.add_command(label="Open Budget...", command=lambda: print("Coming soon..."))
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Save Template As...", command=self.callbacks["save_template_as"])
        self.menu_file.add_command(label="Save Budget", command=lambda: print("Coming soon..."))
        self.menu_file.add_command(label="Save Budget As...", command=lambda: print("Coming soon..."))
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Print...", command=lambda: print("Coming soon..."))
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.master.destroy)

        self.menu_options.add_command(label="Add New Expense Category...", command=self.callbacks["add_category"])
        self.menu_options.add_command(label="Add New Job...", command=self.callbacks["add_job"])
        self.menu_options.add_command(label="Add New Transaction...", command=self.callbacks["add_transaction"])

        # add items to help menu
        self.menu_help.add_command(label="Help", command=lambda: print("Coming soon..."))
        self.menu_help.add_separator()
        self.menu_help.add_command(label="About", command=lambda: print("Coming soon..."))
        
        # add items to menu bar
        self.add_cascade(menu=self.menu_file, label="File")
        self.add_cascade(menu=self.menu_edit, label="Edit")
        self.add_cascade(menu=self.menu_options, label="Options")
        self.add_cascade(menu=self.menu_view, label="View")
        self.add_cascade(menu=self.menu_help, label="Help")
