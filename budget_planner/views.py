import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from decimal import Decimal
from datetime import date
from os import path
from .widgets import AutoScrollbar, DateEntry, DollarEntry, RequiredEntry, DecimalEntry, ModifiedCheckboxTreeview


class HomePage(ttk.Frame):
    """Home page shown upon program startup."""
    def __init__(self, master, callbacks, **kwargs):
        super().__init__(master, **kwargs)
        self.callbacks = callbacks

        # Frame to hold recent templates and budgets
        self.recent_files_frame = ttk.Frame(self)

        # Button which exits home page and goes directly to BudgetView
        exit_home_button = ttk.Button(
            self,
            text="X",
            command=lambda: self.callbacks['change_view']('budget_view')
        )
        remove_selected_button = ttk.Button(
            self,
            text="Remove Selected",
            command=self.remove_recent_entries
        )

        # grid primary widgets
        self.recent_files_frame.grid(column=1, row=0, sticky="ns")
        exit_home_button.grid(column=2, row=0, sticky="ne")
        remove_selected_button.grid(column=2, row=1, sticky="se")

        # set grid weight
        self.grid_columnconfigure(2, weight=1)

        # Set up frame widgets
        recent_files_header = ttk.Label(self.recent_files_frame, text="Recent Budgets and Templates")
        recent_files_header.grid(column=0, row=0, columnspan=2)
        self.recent_files = []

        self.message = ttk.Label(self.recent_files_frame, text="None! Create some!")
        self.check_tv = ModifiedCheckboxTreeview(self.recent_files_frame, selectmode='browse')

        self.update_recent_files_frame()

        self.check_tv.bind("<Double-1>", self._load)

    def update_recent_files_frame(self):
        self.recent_files = self.callbacks["get_recent_files"]()
        if not self.recent_files:
            self.check_tv.grid_forget()
            self.message.grid(column=0, row=1)
        else:
            self.message.grid_forget()
            self.check_tv.delete(*self.check_tv.get_children())
            self.check_tv.grid_forget()
            self.check_tv.grid(column=0, row=2)

            self.check_tv.config(
                columns=('type', 'filename', 'file_extension'),
                height=len(self.recent_files)
            )
            self.check_tv.column('#0', width=100, stretch='NO')
            self.check_tv.column('type', width=200)
            self.check_tv.column('filename', width=200)
            self.check_tv.column('file_extension', width=200)

            self.check_tv.heading('#0', text='')
            self.check_tv.heading('type', text='Budget Type', anchor='w')
            self.check_tv.heading('filename', text='Filename', anchor='w')
            self.check_tv.heading('file_extension', text='Extension', anchor='w')

            for i, v in enumerate(self.recent_files):
                # row content
                fn = path.basename(v['filepath'])
                self.check_tv.insert(
                    parent='',
                    index=i,
                    iid=i,
                    values=(
                        f"{v['budget_type']}".title(),
                        f"{path.splitext(fn)[0]}",
                        f"{path.splitext(fn)[1]}",
                    ),
                )

    def remove_recent_entries(self):
        to_remove = []
        for index in range(len(self.check_tv.get_children())):
            if self.check_tv.tag_has('checked', index):
                to_remove.append(index)
        if to_remove:
            self.callbacks["remove_selected_recent_file_links"](to_remove)

    def _load(self, event):
        x, y = event.x, event.y
        rowid = int(self.check_tv.identify_row(y))
        fp = self.recent_files[rowid]['filepath']
        self.callbacks['load'](automatic=True, filepath=fp)


class BudgetView(ttk.Frame):
    """Page which shows selected budget to user."""

    def __init__(self, master, callbacks, **kwargs):
        super().__init__(master, **kwargs)
        self.callbacks = callbacks
        self.master = master

        # set up widgets for primary layer
        self.canvas = tk.Canvas(self)
        self.v_scroll = AutoScrollbar(self, orient=tk.VERTICAL)
        bottom_frame = ttk.Frame(self)

        # set up scrollable frame
        scrollable_frame = ttk.Frame(self)

        # set up widgets for scrollable frame
        self.title_label = ttk.Label(scrollable_frame, text="Title: Current Budget")
        category_frame = ttk.Frame(scrollable_frame)
        middle_frame = ttk.Frame(scrollable_frame)
        transaction_frame = ttk.Frame(scrollable_frame)

        # set up widgets for category frame
        category_label = ttk.Label(category_frame, text="Categories")
        self.income_tv_header = ttk.Treeview(category_frame, show='tree')
        self.income_tv = ttk.Treeview(category_frame, show='tree')
        self.expense_tv_header = ttk.Treeview(category_frame, show='tree')
        self.expense_tv = ttk.Treeview(category_frame, show='tree')
        self.net_income_tv = ttk.Treeview(category_frame, show='tree')
        self.category_popup_menu = tk.Menu(self.expense_tv)
        self.category_popup_menu.add_command(label="Add Category...", command=self.add_category)
        self.category_popup_menu.add_command(label="Insert Category...", command=self.insert_category)
        self.category_popup_menu.add_command(label="Edit Category...", command=self.edit_category)
        self.category_popup_menu.add_separator()
        self.category_popup_menu.add_command(label="Remove Category", command=self.delete_category)

        # set up widgets for middle frame
        middle_label = ttk.Label(middle_frame, text="Expected Job Income")
        self.middle_tv_header = ttk.Treeview(middle_frame, show='tree')
        self.middle_tv = ttk.Treeview(middle_frame, show='tree')
        self.job_popup_menu = tk.Menu(self.expense_tv)
        self.job_popup_menu.add_command(label="Add Job...", command=self.add_job)
        self.job_popup_menu.add_command(label="Insert Job...", command=self.insert_job)
        self.job_popup_menu.add_command(label="Edit Job...", command=self.edit_job)
        self.job_popup_menu.add_separator()
        self.job_popup_menu.add_command(label="Remove Job", command=self.delete_job)

        # content for transaction frame
        transaction_label = ttk.Label(transaction_frame, text="Transactions")
        self.transaction_tv_header = ttk.Treeview(transaction_frame, show='tree')
        self.transaction_tv = ttk.Treeview(transaction_frame, show='tree')
        self.transaction_popup_menu = tk.Menu(self.transaction_tv)
        self.transaction_popup_menu.add_command(label="Add Transaction...", command=self.add_transaction)
        self.transaction_popup_menu.add_command(label="Insert Transaction...", command=self.insert_transaction)
        self.transaction_popup_menu.add_command(label="Edit Transaction...", command=self.edit_transaction)
        self.transaction_popup_menu.add_separator()
        self.transaction_popup_menu.add_command(label="Remove Transaction", command=self.delete_transaction)

        # set up widgets for bottom frame
        previous_button = ttk.Button(
            bottom_frame,
            text="Previous",
            command=self.callbacks["get_previous_budget"]
        )
        next_button = ttk.Button(
            bottom_frame,
            text="Next",
            command=self.callbacks["get_next_budget"]
        )
        self.h_scroll = ttk.Scrollbar(bottom_frame, orient=tk.HORIZONTAL)

        # grid primary layer widgets
        self.canvas.grid(column=0, row=0, sticky='nw')
        self.v_scroll.grid(column=1, row=0, sticky='ns')
        bottom_frame.grid(column=0, row=1, sticky='nwes')

        # grid scrollable frame widgets
        self.title_label.grid(column=0, row=0, columnspan=3, sticky=(tk.W + tk.E))
        category_frame.grid(column=0, row=1, sticky='nwes')
        middle_frame.grid(column=1, row=1, padx=20, sticky='nwes')
        transaction_frame.grid(column=2, row=1, sticky='nwes')

        # grid content for category frame
        category_label.grid(row=0)
        self.income_tv_header.grid(row=1)
        self.income_tv.grid(row=2)
        self.expense_tv_header.grid(row=3)
        self.expense_tv.grid(row=4)
        self.net_income_tv.grid(row=5, pady=(20, 0))

        # grid content for middle frame
        middle_label.grid(row=0)
        self.middle_tv_header.grid(row=1)
        self.middle_tv.grid(row=2)

        # grid content for transaction frame
        transaction_label.grid(row=0)
        self.transaction_tv_header.grid(row=1)
        self.transaction_tv.grid(row=2)

        # grid content for bottom frame
        previous_button.grid(column=0, row=0)
        next_button.grid(column=1, row=0)
        self.h_scroll.grid(column=2, row=0, sticky=(tk.W + tk.E))

        # apply weights to BudgetView sub-frames as needed
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(2, weight=1)

        # ensure scrollbars show up above canvas
        bottom_frame.tkraise()
        self.v_scroll.tkraise()

        # attach scrollable frame to canvas
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # set up canvas
        self.canvas_width, self.canvas_height = 0, 0

        # activate scrollbars for canvas containing scrollable frame
        self.h_scroll['command'] = self.canvas.xview
        self.v_scroll['command'] = self.canvas.yview
        self.canvas.configure(
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )

        # initiate data containers for view
        if self.master.data_model.template_data['type'] == 'template':
            self.view_data = master.data_model.template_data['template']  # not a copy
        if self.master.data_model.template_data['type'] == 'budget':
            newest_budget = master.data_model.template_data['order'][-1]
            self.view_data = master.data_model.template_data['budgets'][newest_budget]

        # fill BudgetView with content
        self.category_column_names = ('#0', 'name', 'budget', 'actual')
        self.editable_category_column_names = self.category_column_names[1:3]
        self.editable_category_column_datatypes = [str, Decimal]
        self.category_entry_widgets = [RequiredEntry, DollarEntry]
        self.category_column_widths = (0, 160, 80, 80)
        self.category_column_orientations = ('w', 'w', 'e', 'e')

        self.job_column_names = ('#0', 'name', 'hourly_pay', 'hours', 'tax_rate', 'wages')
        self.editable_job_column_names = self.job_column_names[1:5]
        self.editable_job_column_datatypes = [str, Decimal, Decimal, Decimal]
        self.job_entry_widgets = [RequiredEntry, DollarEntry, DollarEntry, DecimalEntry]
        self.job_column_widths = (0, 80, 80, 50, 70, 60)
        self.job_column_orientations = ('w', 'w', 'e', 'e', 'e', 'e')

        self.transaction_column_names = ('#0', 'date', 'merchant', 'category', 'outlay', 'inflow', 'net')
        self.editable_transaction_column_names = self.transaction_column_names[1:6]
        self.editable_transaction_column_datatypes = [str, str, str, Decimal, Decimal]
        self.transaction_entry_widgets = [DateEntry, RequiredEntry, RequiredEntry, DollarEntry, DollarEntry]
        self.transaction_column_widths = (0, 80, 160, 160, 80, 80, 80)
        self.transaction_column_orientations = ('w', 'w', 'w', 'w', 'e', 'e', 'e')

        self.update_frames()

        # add styles
        self.styles = ttk.Style()
        self.set_styles()

        # set up events
        scrollable_frame.bind("<Configure>", self.get_canvas_size)
        self.expense_tv.bind("<Button-3>", self.call_category_popup_menu)
        self.middle_tv.bind("<Button-3>", self.call_job_popup_menu)
        self.transaction_tv.bind("<Button-3>", self.call_transaction_popup_menu)

        self.bind("<Configure>", self.resize)

    def get_canvas_size(self, *args):
        _, _, self.canvas_width, self.canvas_height = self.canvas.bbox('all')
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              width=self.canvas_width,
                              height=self.canvas_height)

    def update_frames(self):
        """Method which updates BudgetView."""

        self.middle_tv_header.delete(*self.middle_tv_header.get_children())
        self.middle_tv.delete(*self.middle_tv.get_children())
        self.transaction_tv_header.delete(*self.transaction_tv_header.get_children())
        self.transaction_tv.delete(*self.transaction_tv.get_children())
        self.income_tv_header.delete(*self.income_tv_header.get_children())
        self.income_tv.delete(*self.income_tv.get_children())
        self.expense_tv_header.delete(*self.expense_tv_header.get_children())
        self.expense_tv.delete(*self.expense_tv.get_children())
        self.net_income_tv.delete(*self.net_income_tv.get_children())

        self.middle_tv_header.grid_forget()  # forget
        self.middle_tv.grid_forget()
        self.middle_tv_header.grid()  # remember
        self.middle_tv.grid()
        self.add_content_middle_frame()

        self.transaction_tv_header.grid_forget()  # forget
        self.transaction_tv.grid_forget()
        self.transaction_tv_header.grid()  # remember
        self.transaction_tv.grid()
        self.add_content_transaction_frame()  # repopulate

        self.income_tv_header.grid_forget()  # forget
        self.income_tv.grid_forget()
        self.expense_tv_header.grid_forget()
        self.expense_tv.grid_forget()
        self.net_income_tv.grid_forget()
        self.income_tv_header.grid()  # remember
        self.income_tv.grid()
        self.expense_tv_header.grid()
        self.expense_tv.grid()
        self.net_income_tv.grid(pady=(20, 0))
        self.add_content_category_frame()  # repopulate

        self._update_title()  # update current budget title

    def _update_title(self):
        if self.master.data_model.template_data["type"] == "budget":
            name = self.master.data_model.template_data["name"]
            sub_name = self.master.data_model.template_data["current_budget"]

            self.title_label.configure(text=name + ": " + sub_name)
        else:
            name = self.master.data_model.template_data["name"]
            self.title_label.configure(text=name)

    def add_content_category_frame(self):
        """Function to fill category frame with content. Determines how to display data."""

        column_names = self.category_column_names
        column_widths = self.category_column_widths
        column_orientations = self.category_column_orientations
        column_list = list(zip(column_names, column_widths, column_orientations))

        # set new names for data in view_data
        income_categories = self.view_data['income_categories']
        expense_categories = self.view_data['expense_categories']
        transactions = self.view_data['transactions']

        # add content to income treeview header
        self.income_tv_header.config(columns=column_names[1:], selectmode='none', height=1)
        for v in column_list:
            self.income_tv_header.column(v[0], width=v[1], stretch='NO', anchor=v[2])
        self.income_tv_header.insert(
            parent='', index=0, iid=0,
            value=('---INCOME---', 'Expected', 'Actual'),
            tags=('header',)
        )
        self.income_tv_header.tag_configure("header", foreground="black", background="#70AD47")

        # add content to income treeview body
        self.income_tv.config(columns=column_names[1:], selectmode='browse')
        for v in column_list:
            self.income_tv.column(v[0], width=v[1], stretch='NO', anchor=v[2])

        # initialize variables
        actual_income = Decimal('0')
        uncategorized_income = Decimal('0')

        # create dictionary to hold values which will be inserted into the income treeview body
        income_category_totals = {
            k['name']: {'expected': k['hourly_pay'] * k['hours'], 'actual': Decimal('0')}
            for k in income_categories
        }

        for tran in transactions:
            inflow = tran['inflow']
            merchant = tran['merchant']
            if inflow > 0:
                actual_income += inflow
                if merchant in income_category_totals.keys():
                    income_category_totals[merchant]['actual'] += inflow
                else:
                    uncategorized_income += inflow

        # determine whether to display uncategorized income row
        if uncategorized_income > 0:
            income_category_totals['Uncategorized'] = dict(expected=Decimal('0'), actual=uncategorized_income)

        expected_income = Decimal(sum([v['expected'] for v in income_category_totals.values()]))
        income_category_totals['SUBTOTAL'] = dict(expected=expected_income, actual=actual_income)

        for index, (k, v) in enumerate(income_category_totals.items()):
            if index % 2 == 0:
                parity = 'even'
            else:
                parity = 'odd'
            self.income_tv.insert(
                parent='',
                index=index,
                iid=index,
                values=(k, round(v['expected'], 2), round(v['actual'], 2)),
                tags=(parity,)
            )
        # add colors based on tag
        self.income_tv.tag_configure("even", foreground="black", background="white")
        self.income_tv.tag_configure("odd", foreground="black", background="grey75")
        # set height based on number of income categories plus a subtotal row
        self.income_tv.config(height=len(income_category_totals))

        # add content to expense treeview header
        self.expense_tv_header.config(columns=column_names[1:], selectmode='none', height=1)
        for v in column_list:
            self.expense_tv_header.column(v[0], width=v[1], stretch='NO', anchor=v[2])

        self.expense_tv_header.insert(
            parent='', index=0, iid=0,
            value=('---EXPENSES---', 'Budget', 'Actual'),
            tags=('header',)
        )
        self.expense_tv_header.tag_configure("header", foreground="black", background="#5B9BD5")

        # add content to expense treeview body
        self.expense_tv.config(columns=column_names[1:], selectmode='browse', height=20)
        for v in column_list:
            self.expense_tv.column(v[0], width=v[1], stretch='NO', anchor=v[2])

        # add user rows to expense_treeview based on given categories
        actual_expense = Decimal('0')
        taxed_income = Decimal('0')
        uncategorized_expense = Decimal('0')

        # create dictionary to hold values which will be inserted into the expense treeview body
        expense_category_totals = {
            k['name']: {'budget': k['budget'], 'actual': Decimal('0')}
            for k in expense_categories
        }

        for tran in transactions:
            outlay = tran['outlay']
            merchant = tran['merchant']
            category = tran['category']
            if outlay > 0:
                actual_expense += outlay
                if category in expense_category_totals.keys():
                    expense_category_totals[category]['actual'] += outlay
                elif merchant in [k['name'] for k in income_categories]:
                    taxed_income += outlay
                else:
                    uncategorized_expense += outlay

        budgeted_income_taxes = Decimal(
            sum([ic['hourly_pay'] * ic['hours'] * ic['tax_rate'] for ic in income_categories])
        )
        expense_category_totals['Income Tax'] = dict(budget=budgeted_income_taxes, actual=taxed_income)

        # determine whether to display uncategorized expense row
        if uncategorized_expense > 0:
            expense_category_totals['Uncategorized'] = dict(budget=Decimal('0'), actual=uncategorized_expense)

        budgeted_expense = Decimal(sum([v['budget'] for v in expense_category_totals.values()]))
        expense_category_totals['SUBTOTAL'] = dict(budget=budgeted_expense, actual=actual_expense)

        for index, (k, v) in enumerate(expense_category_totals.items()):
            if index % 2 == 0:
                parity = 'even'
            else:
                parity = 'odd'
            self.expense_tv.insert(
                parent='',
                index=index,
                iid=index,
                values=(k, round(v['budget'], 2), round(v['actual'], 2)),
                tags=(parity,)
            )

        # add colors based on tag
        self.expense_tv.tag_configure("even", foreground="black", background="white")
        self.expense_tv.tag_configure("odd", foreground="black", background="grey75")
        # set number of rows
        self.expense_tv.config(height=len(expense_category_totals))

        # set up treeview to aggregate income and expense totals
        self.net_income_tv.config(columns=column_names[1:], selectmode='none', height=1)
        for v in column_list:
            self.net_income_tv.column(v[0], width=v[1], stretch='NO', anchor=v[2])
        self.net_income_tv.insert(
            parent='', index=0, iid=0,
            value=(
                'NET INCOME:',
                round(expected_income - budgeted_expense, 2),
                round(actual_income - actual_expense, 2)
            ),
            tags=('header',)
        )
        self.net_income_tv.tag_configure("header", foreground="white", background="#4b707e")

    def add_content_middle_frame(self):
        """Function to add middle frame with content. Determines which data to load."""

        # set up general variables
        column_names = self.job_column_names
        column_widths = self.job_column_widths
        column_orientations = self.job_column_orientations
        column_list = list(zip(column_names, column_widths, column_orientations))

        # set new names for data in template_data
        jobs = self.view_data['income_categories']

        # add content to middle treeview header
        self.middle_tv_header.config(columns=column_names[1:], selectmode='none', height=1)
        for v in column_list:
            self.middle_tv_header.column(v[0], width=v[1], stretch='NO', anchor=v[2])

        self.middle_tv_header.insert(
            parent='', index=0, iid=0,
            value=('Job', 'Hourly Rate', 'Hours', 'Tax Rate', 'Wages'),
            tags=('header',)
        )
        self.middle_tv_header.tag_configure("header", foreground="black", background="#A5A5A5")

        # add content to middle treeview
        self.middle_tv.config(columns=column_names[1:], selectmode='browse', height=20)
        for v in column_list:
            self.middle_tv.column(v[0], width=v[1], stretch='NO', anchor=v[2])

        for index, value in enumerate(jobs):
            if index % 2 == 0:
                parity = 'even'
            else:
                parity = 'odd'
            self.middle_tv.insert(
                parent='',
                index=index,
                iid=index,
                values=(
                    value['name'],
                    round(value['hourly_pay'], 2),
                    round(value['hours'], 2),
                    round(value['tax_rate'], 2),
                    round(value['hourly_pay'] * value['hours'], 2)
                ),
                tags=(parity,)
            )

        self.middle_tv.tag_configure("even", foreground="black", background="#D9D9D9")
        self.middle_tv.tag_configure("odd", foreground="black", background="white")
        self.middle_tv.config(height=len(jobs))

    def add_content_transaction_frame(self):
        """Function to add transaction frame with content. Determines which data to load."""

        # set up transaction column names and widths
        column_names = self.transaction_column_names
        column_widths = self.transaction_column_widths
        column_orientations = self.transaction_column_orientations
        column_list = list(zip(column_names, column_widths, column_orientations))

        # set new name(s) for data in template_data
        transactions = self.view_data['transactions']

        # add content to transaction treeview header
        self.transaction_tv_header.config(columns=column_names[1:], selectmode='none', height=1)
        for v in column_list:
            self.transaction_tv_header.column(v[0], width=v[1], stretch='NO', anchor=v[2])

        self.transaction_tv_header.insert(
            parent='', index=0, iid=0,
            value=tuple(name.title() for name in column_names[1:]),
            tags=('header',)
        )
        self.transaction_tv_header.tag_configure("header", foreground="black", background="#ED7D31")

        # add content to transaction treeview
        self.transaction_tv.config(columns=column_names[1:], selectmode='browse', height=20)
        for v in column_list:
            self.transaction_tv.column(v[0], width=v[1], stretch='NO', anchor=v[2])

        for index, value in enumerate(transactions):
            if index % 2 == 0:
                parity = 'even'
            else:
                parity = 'odd'
            self.transaction_tv.insert(
                parent='',
                index=index,
                iid=index,
                values=(
                    value['date'],
                    value['merchant'],
                    value['category'],
                    round(value['outlay'], 2),
                    round(value['inflow'], 2),
                    round(value['inflow'] - value['outlay'], 2)
                ),
                tags=(parity,)
            )

        self.transaction_tv.tag_configure("even", foreground="black", background="#B4C6E7")
        self.transaction_tv.tag_configure("odd", foreground="black", background="#D9E1F2")
        self.transaction_tv.config(height=len(transactions))

    def call_category_popup_menu(self, event):
        """Method to create a small popup menu for the expense category treeview"""

        try:
            self.category_popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.category_popup_menu.grab_release()

    def add_category(self):
        """Add new category to the expense category treeview by calling private method."""

        self._modify_table_window(
            table="expense_categories",
            call="add",
            title="New Category",
            entry_defaults=['Placeholder', Decimal(0)],
            button_text="Add"
        )

    def insert_category(self):
        """
        Method which checks to see if we have a selected row in the expense category treeview.

        If no row is selected this function quits. If a row is selected user is allowed to add
        a new category above the selected row by calling a private method.
        """

        row = self.expense_tv.focus()  # get expense category treeview's selected row number
        if row:  # doesn't run if empty string is returned
            self._modify_table_window(
                table="expense_categories",
                call="insert",
                title="Insert Category",
                entry_defaults=['Placeholder', Decimal(0)],
                button_text="Insert",
                row=row
            )

    def edit_category(self):
        """
        Method which allows user to update selected expense category information by calling a private method.

        If no row is selected, nothing happens.
        """

        row = self.expense_tv.focus()  # get treeview row
        if row:  # runs only if a row is selected
            defaults = self.view_data['expense_categories'][int(row)]  # get data from selected treeview row
            defaults = [defaults[d] for d in self.editable_category_column_names]
            self._modify_table_window(
                table="expense_categories",
                call="edit",
                title="Edit Category",
                entry_defaults=defaults,
                button_text="Edit",
                row=row
            )

    def delete_category(self):
        """
        Deletes selected row from expense category treeview and updates BudgetView.

        If no row selected, nothing happens. This only applies for user created categories.
        """

        row = self.expense_tv.focus()
        if row:
            try:  # only works if
                del self.view_data['expense_categories'][int(row)]  # remove selected treeview row
            except IndexError:
                # IndexError can occur if we select a category not created by user
                pass
            finally:
                self.update_frames()

    def call_transaction_popup_menu(self, event):
        """Method to create a small popup menu for the transaction treeview"""

        try:
            self.transaction_popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.transaction_popup_menu.grab_release()

    def add_transaction(self):
        """Add new transaction to transaction treeview by calling private method."""

        self._modify_table_window(
            table="transactions",
            call="add",
            title="New Transaction",
            entry_defaults=[date.today(), "home", "food", Decimal(100), Decimal(0)],
            button_text="Add"
        )

    def insert_transaction(self):
        """
        Method which checks to see if we have a selected row in the transaction treeview.

        If no row is selected this function quits. If a row is selected user is allowed to add
        a new transaction above the selected row by calling a private method.
        """

        row = self.transaction_tv.focus()  # get transaction treeview selected row number
        if row:  # doesn't run if empty string is returned
            self._modify_table_window(
                table="transactions",
                call="insert",
                title="Insert Transaction",
                entry_defaults=[date.today(), "Home", "Food", Decimal(100), Decimal(0)],
                button_text="Insert",
                row=row
            )

    def edit_transaction(self):
        """
        Method which allows user to update selected transaction information by calling a private method.

        If no row is selected, nothing happens.
        """

        row = self.transaction_tv.focus()  # get treeview row
        if row:  # runs only if a row is selected
            defaults = self.view_data['transactions'][int(row)]  # get data from selected treeview row
            defaults = [defaults[d] for d in self.editable_transaction_column_names]
            self._modify_table_window(
                table="transactions",
                call="edit",
                title="Edit Transaction",
                entry_defaults=defaults,
                button_text="Edit",
                row=row
            )

    def delete_transaction(self):
        """Deletes selected row from transactions and updates BudgetView. If no row selected, nothing happens."""

        row = self.transaction_tv.focus()
        if row:
            del self.view_data['transactions'][int(row)]  # remove selected treeview row
            self.update_frames()

    def call_job_popup_menu(self, event):
        """Method to create a small popup menu for the middle treeview"""

        try:
            self.job_popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.job_popup_menu.grab_release()

    def add_job(self):
        """Add new job to middle treeview by calling private method."""

        self._modify_table_window(
            table='income_categories',
            call="add",
            title="New Job",
            entry_defaults=["Job1", Decimal(0), Decimal(0), Decimal(0)],
            button_text="Add"
        )

    def insert_job(self):
        """
        Method which checks to see if we have a selected row in the middle treeview.

        If no row is selected this function quits. If a row is selected user is allowed to add
        a new job above the selected row by calling a private method.
        """

        row = self.middle_tv.focus()  # get middle treeview selected row number
        if row:  # doesn't run if empty string is returned
            self._modify_table_window(
                table='income_categories',
                call="insert",
                title="Insert Job",
                entry_defaults=["Job2", Decimal(0), Decimal(0), Decimal(0)],
                button_text="Insert",
                row=row
            )

    def edit_job(self):
        """
        Method which allows user to update selected job information by calling a private method.

        If no row is selected, nothing happens.
        """

        row = self.middle_tv.focus()  # get treeview row
        if row:  # runs only if a row is selected
            defaults = self.view_data['income_categories'][int(row)]  # get data from selected treeview row
            defaults = [defaults[d] for d in self.editable_job_column_names]
            self._modify_table_window(
                table='income_categories',
                call="edit",
                title="Edit Job",
                entry_defaults=defaults,
                button_text="Edit",
                row=row
            )

    def delete_job(self):
        """Deletes selected row from income categories and updates BudgetView. If no row selected, nothing happens."""

        row = self.middle_tv.focus()
        if row:
            del self.view_data['income_categories'][int(row)]  # remove selected treeview row
            self.update_frames()

    def _modify_table_window(self, table, call, title, entry_defaults, button_text, row=0):
        """
        Method called to add, edit or insert a row in one of the BudgetView treeviews.

        This is done by creating entry widgets that the user enters data into and then submits.
        This is a private method called by methods which determine whether this method is
        used to add, edit or insert data.
        """

        modify_window = tk.Toplevel(self)
        modify_window.wm_title(title)

        # set if elif else for which table is being updated
        if table == 'income_categories':
            entry_names = self.editable_job_column_names
            entry_widgets = self.job_entry_widgets
            function_calls = self.editable_job_column_datatypes
            which_treeview = table
        elif table == 'expense_categories':
            entry_names = self.editable_category_column_names
            entry_widgets = self.category_entry_widgets
            function_calls = self.editable_category_column_datatypes
            which_treeview = table
        else:  # case when table == 'transactions'
            entry_names = self.editable_transaction_column_names
            entry_widgets = self.transaction_entry_widgets
            function_calls = self.editable_transaction_column_datatypes
            which_treeview = table

        entries = {}  # holds data submitted

        def call_update_frames():
            """
            Helper function which extracts entry widgets' values. It then adds, inserts, or edits a
            the selected treeview. It finally refreshes BudgetView.
            """

            # catch errors
            errors = {}
            for key, widget in entries.items():
                if hasattr(widget, "trigger_focusout_validation"):
                    widget.trigger_focusout_validation()
                error_code = ''
                try:
                    error_code = widget.error.get()
                except AttributeError:
                    error_code = ''
                finally:
                    if error_code:
                        errors[key] = widget.error.get()
            # display errors if they exist
            if errors:
                error_mesasage = ''
                for key, value in errors.items():
                    error_mesasage += f'\n\t{key} : {value}'

                messagebox.showerror(
                    title="Entry Errors",
                    message=f"The following errors occurred: {error_mesasage}",
                    detail="Data must be resubmitted."
                )

            if not errors:
                new_entry = {en: function_calls[k](entries[en].get()) for k, en in enumerate(entry_names)}
                if which_treeview == 'transactions':
                    update = True
                elif call == 'edit':
                    update = True
                elif new_entry['name'] not in [en['name'] for en in self.view_data[which_treeview]]:
                    update = True
                else:
                    update = False
                if update:
                    if call == "add":
                        self.view_data[which_treeview].append(new_entry)
                    elif call == "insert":
                        self.view_data[which_treeview].insert(int(row), new_entry)
                    elif call == "edit":
                        self.view_data[which_treeview][int(row)] = new_entry
                    self.update_frames()

        i = 0
        for i, name in enumerate(entry_names):
            ttk.Label(modify_window, text=name.title()).grid(column=i, row=0)
            entries[name] = entry_widgets[i](modify_window)
            for j, string in enumerate(str(entry_defaults[i])):
                entries[name].insert(j, string)
            entries[name].grid(column=i, row=1)
        modify_button = ttk.Button(modify_window, text=button_text, command=call_update_frames)
        modify_button.grid(column=i, row=2, sticky='e')

    def set_styles(self):
        #self.styles.theme_use('clam')
        self.styles.configure('mystyle.Treeview', highlightthickness=0, bd=0, font=('Calibri', 11))
        self.styles.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        self.styles.map(
            "Treeview",
            background=[('selected', 'focus', '#948383')],
            foreground=[('selected', 'focus', 'white')]
        )

        self.income_tv_header.configure(style="mystyle.Treeview")
        self.income_tv.configure(style="mystyle.Treeview")
        self.expense_tv_header.configure(style="mystyle.Treeview")
        self.expense_tv.configure(style="mystyle.Treeview")
        self.net_income_tv.configure(style="mystyle.Treeview")

        self.middle_tv_header.configure(style="mystyle.Treeview")
        self.middle_tv.configure(style="mystyle.Treeview")

        self.transaction_tv_header.configure(style="mystyle.Treeview")
        self.transaction_tv.configure(style="mystyle.Treeview")

    def resize(self, event):
        self.callbacks['set_window_size'](event.width, event.height)


class CreateBudget(tk.Toplevel):
    """Class which has pop-up window with options for user to select when creating a new Budget or Budget Template."""

    def __init__(self, master, callbacks, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.callbacks = callbacks
        self.master = master

        self.wm_title("New")

        self.type = tk.StringVar(value='budget')
        self.budget_select = ttk.Radiobutton(self, text="Budget", variable=self.type, value='budget', command=self.form_update)
        self.template_select = ttk.Radiobutton(self, text="Template", variable=self.type, value='template', command=self.form_update)

        self.budget_form = ttk.Frame(self)
        self.template_form = ttk.Frame(self)

        self.submit_button = ttk.Button(self, text="Submit", command=self.create_new)

        self.budget_select.grid(column=0, row=0)
        self.template_select.grid(column=1, row=0)
        self.submit_button.grid(column=1, row=2, sticky="e")

        if self.type.get() == 'budget':
            self.budget_form.grid(column=0, row=1, columnspan=2)
        else:
            self.template_form.grid(column=0, row=1, columnspan=2)

        # set up budget form
        text_label_r1 = ttk.Label(self.budget_form, text="Budget Group Name: ")
        self.budget_group_name = ttk.Entry(self.budget_form)
        self.budget_group_name.insert(0, "New Budget")

        text_label_r2 = ttk.Label(self.budget_form, text="Initial Budget Name: ")
        self.budget_name = ttk.Entry(self.budget_form)
        self.budget_name.insert(0, "Origin")

        text_label_r1.grid(column=0, row=0)
        text_label_r2.grid(column=0, row=1)
        self.budget_group_name.grid(column=1, row=0)
        self.budget_name.grid(column=1, row=1)

        # set up template form
        template_text_label = ttk.Label(self.template_form, text="Template Name: ")
        self.template_name = ttk.Entry(self.template_form)
        self.template_name.insert(0, "New Template")

        template_text_label.grid(column=0, row=0)
        self.template_name.grid(column=1, row=0)

        self.new_budget = {}
        self.new_template = {}

    def form_update(self):
        if self.type.get() == 'budget':
            self.template_form.grid_forget()
            self.budget_form.grid(column=0, row=1, columnspan=2)
        else:
            self.budget_form.grid_forget()
            self.template_form.grid(column=0, row=1, columnspan=2)

    def create_new(self):
        """Determines if we are creating a new Budget or a new Template."""

        if self.type.get() == 'budget':
            self.create_new_budget()
        else:
            self.create_new_template()

        self.callbacks['reset_current_file_filepath']()
        self.callbacks['disable_quick_save']()

    def create_new_template(self):
        """Sets defaults for a new template and then calls method to reset BudgetView with new template."""

        # get template form data
        name = self.template_name.get()

        self.new_template["type"] = "template"
        self.new_template["name"] = name
        self.new_template["template"] = {
            'income_categories': [],
            'expense_categories': [],
            'transactions': [],
        }

        self._initiate_new_template()

    def _initiate_new_template(self):
        """Resets BudgetView with new template."""

        self.master.data_model.template_data = self.new_template

        self.master.budget_view.view_data = self.new_template['template']
        self.callbacks['update_frames']()
        self.callbacks['change_view']("budget_view")

    def create_new_budget(self):
        """Sets defaults for a new budget and then calls method to reset BudgetView with new budget."""

        # get budget form data
        group_name = self.budget_group_name.get()
        first_budget = self.budget_name.get()

        self.new_budget["type"] = "budget"
        self.new_budget["name"] = group_name
        self.new_budget["current_budget"] = first_budget
        self.new_budget["budgets"] = {}
        self.new_budget["order"] = [first_budget]
        self.new_budget["budgets"][first_budget] = {
            'income_categories': [],
            'expense_categories': [],
            'transactions': [],
        }

        self._initiate_new_budget()

    def _initiate_new_budget(self):
        """Resets BudgetView with new budget."""

        self.master.data_model.template_data = self.new_budget

        newest_budget = self.new_budget['order'][-1]
        self.view_data = self.new_budget['budgets'][newest_budget]
        self.master.budget_view.view_data = self.new_budget['budgets'][newest_budget]
        self.callbacks['update_frames']()
        self.callbacks['change_view']("budget_view")


class SaveBudget:
    """Class which has pop-up window with options for user to save a budget group."""

    def __init__(self, master, callbacks, *args, **kwargs):
        self.callbacks = callbacks
        self.master = master

        self.master.data_model.initiate_directory(self.master.data_model.budgets_path)

        mask = [("CSV files", "*.csv"), ("All files", "*.*")]

        self.filepath = filedialog.asksaveasfilename(
            title="Save Budget Group As",
            initialdir=self.master.data_model.budgets_path,
            initialfile="new_group.csv",
            filetypes=mask
        )


class LoadBudget:
    """Class which has pop-up window allowing user to select a csvfile pointing to a budget group to load."""

    def __init__(self, master, callbacks, *args, **kwargs):
        self.callbacks = callbacks
        self.master = master

        bdp = self.master.data_model.budgets_path  # budgets directory path
        self.master.data_model.initiate_directory(bdp)

        mask = [("CSV files", "*.csv"), ("All files", "*.*")]

        self.filepath = filedialog.askopenfilename(
            title="Load Budget Group",
            initialdir=bdp,
            filetypes=mask
        )


class MessageView:
    """Class containing messages which are called outside of main view."""

    @staticmethod
    def directory_overwrite_messagebox(directory_name):
        return messagebox.askokcancel(
            title="Directory Exists",
            message=f"A directory called {directory_name} already exists!",
            detail="Do you want to overwrite?"
        )

    @staticmethod
    def create_next_budget_messagebox():
        return messagebox.askyesno(
            title="Add Next Budget",
            message="There is no next budget!",
            detail="Create it?"
        )


class AddNextBudget(tk.Toplevel):
    """ """

    def __init__(self, master, callbacks, current, add_budget_func, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.callbacks = callbacks
        self.master = master
        self.newest_budget = current
        self.add_budget_func = add_budget_func

        self.wm_title("Add Budget")

        # create widgets
        self.name_label = ttk.Label(self, text="Budget Name: ")
        self.next_name = ttk.Entry(self)
        self.radiobutton_label = ttk.Label(self, text="Template: ")

        self.rbs = tk.StringVar(value='previous')
        self.blank_rb = ttk.Radiobutton(self, text="Blank", variable=self.rbs, value="blank")
        self.previous_rb = ttk.Radiobutton(self, text="Previous", variable=self.rbs, value="previous")
        self.saved_rb = ttk.Radiobutton(self, text="Saved", variable=self.rbs, value="saved")

        self.next_name_submit = ttk.Button(self, text="Submit", command=self.gather_info)

        # grid widgets
        self.name_label.grid(column=0, row=0, sticky='w')
        self.next_name.grid(column=1, row=0)
        self.radiobutton_label.grid(column=0, row=1, sticky='w')
        self.blank_rb.grid(column=1, row=1, sticky='w')
        self.previous_rb.grid(column=1, row=2, sticky='w')
        self.saved_rb.grid(column=1, row=3, sticky='w')
        self.next_name_submit.grid(column=1, row=4, sticky='e')

    def gather_info(self):
        self.newest_budget = self.next_name.get()

        if self.newest_budget in self.master.data_model.template_data["order"]:
            messagebox.showerror(
                title="Name Error",
                message="Budget name already in use!",
                detail="Choose another name."
            )
        elif self.newest_budget == '':
            messagebox.showerror(
                title="Name Error",
                message="Budget name must be at least one character long!",
                detail="Choose another name."
            )
        else:
            self.add_budget_func(self.newest_budget, template=self.rbs.get())
            self.destroy()
            self.update()


class SaveTemplate:
    """Class which has pop-up window with options for user to save a budget template."""

    def __init__(self, master, callbacks, initial_dir, *args, **kwargs):
        self.callbacks = callbacks
        self.master = master
        self.initial_dir = initial_dir

        mask = [("Pickle files", "*.pkl"), ("All files", "*.*")]

        self.filepath = filedialog.asksaveasfilename(
            title="Save Template As",
            initialdir=self.initial_dir,
            initialfile="template.pkl",
            filetypes=mask
        )


class SaveBudgetGroup:
    """Class which has pop-up window with options for user to save a budget group."""

    def __init__(self, master, callbacks, initial_dir, *args, **kwargs):
        self.callbacks = callbacks
        self.master = master
        self.initial_dir = initial_dir

        self.master.data_model.initiate_directory(self.master.data_model.budgets_path)

        mask = [("Pickle files", "*.pkl"), ("All files", "*.*")]

        self.filepath = filedialog.asksaveasfilename(
            title="Save Budget Grouping As",
            initialdir=self.master.data_model.budgets_path,
            initialfile="new_group.pkl",
            filetypes=mask
        )


class SavePickle:
    """Class which has pop-up window allowing user to save a file in Pickle format."""
    def __init__(self, filename, title, mask, *args, **kwargs):
        self.filepath = filedialog.asksaveasfilename(
            title=title,
            initialfile=filename,
            filetypes=mask
        )


class LoadPickle:
    """Class which has pop-up window allowing user to select a Pickle file to load."""
    def __init__(self, title, mask, *args, **kwargs):
        self.filepath = filedialog.askopenfilename(
            title=title,
            filetypes=mask
        )
