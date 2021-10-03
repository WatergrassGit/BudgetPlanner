import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from decimal import Decimal
from datetime import date
from .widgets import AutoScrollbar


class BudgetView(ttk.Frame):
    """Page which shows selected budget to user."""

    def __init__(self, master, callbacks, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
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
            command=self.get_previous_budget
        )
        next_button = ttk.Button(
            bottom_frame,
            text="Next",
            command=self.get_next_budget
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
            self.view_data = master.data_model.template_data[newest_budget]

        # fill BudgetView with content
        self.category_column_names = ('#0', 'name', 'budget', 'actual')
        self.editable_category_column_names = self.category_column_names[1:3]
        self.editable_category_column_datatypes = [str, Decimal]
        self.category_column_widths = (0, 160, 80, 80)

        self.job_column_names = ('#0', 'name', 'hourly_pay', 'hours', 'tax_rate', 'wages')
        self.editable_job_column_names = self.job_column_names[1:5]
        self.editable_job_column_datatypes = [str, Decimal, Decimal, Decimal]
        self.job_column_widths = (0, 80, 80, 50, 70, 60)

        self.transaction_column_names = ('#0', 'date', 'merchant', 'category', 'outlay', 'inflow', 'net')
        self.editable_transaction_column_names = self.transaction_column_names[1:6]
        self.editable_transaction_column_datatypes = [str, str, str, Decimal, Decimal]
        self.transaction_column_widths = (0, 80, 160, 160, 80, 80, 80)

        self.update_frames()

        # add styles
        self.styles = ttk.Style()
        self.set_styles()

        # set up events
        scrollable_frame.bind("<Configure>", self.get_canvas_size)
        self.expense_tv.bind("<Button-3>", self.call_category_popup_menu)
        self.middle_tv.bind("<Button-3>", self.call_job_popup_menu)
        self.transaction_tv.bind("<Button-3>", self.call_transaction_popup_menu)

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
            self.title_label.configure(text="Template")

    def add_content_category_frame(self):
        """Function to add category frame with content. Determines which data to load."""

        column_names = self.category_column_names
        column_widths = self.category_column_widths
        column_dictionary = dict(zip(column_names, column_widths))

        # set new names for data in template_data
        income_categories = self.view_data['income_categories']
        expense_categories = self.view_data['expense_categories']
        transactions = self.view_data['transactions']

        # add content to income treeview
        # add the header income treeview
        self.income_tv_header.config(columns=column_names[1:], selectmode='none', height=1)
        for k, v in column_dictionary.items():
            self.income_tv_header.column(k, width=v, stretch='NO')
        self.income_tv_header.insert(
            parent='', index=0, iid=0,
            value=('---INCOME---', 'Budget', 'Actual'),
            tags=('header',)
        )
        self.income_tv_header.tag_configure("header", foreground="black", background="#70AD47")

        # add the main income treeview
        self.income_tv.config(columns=column_names[1:], selectmode='browse')
        for k, v in column_dictionary.items():
            self.income_tv.column(k, width=v, stretch='NO')

        # add income categories to income treeview
        index = 0
        income_budget = 0
        income_actual = 0
        for index, value in enumerate(income_categories):
            if index % 2 == 0:
                parity = 'even'
            else:
                parity = 'odd'
            category_income_total = 0
            for trans in transactions:
                if trans['category'] in "Income" and trans['merchant'] in value['name']:
                    category_income_total += trans['inflow']
            self.income_tv.insert(
                parent='',
                index=index,
                iid=index,
                values=(
                    value['name'],
                    round(value['hourly_pay'] * value['hours'], 2),
                    max(Decimal('0.00'), category_income_total)
                ),
                tags=(parity,)
            )
            income_budget += round(value['hourly_pay'] * value['hours'], 2)
            income_actual += category_income_total
        index += 1
        if index % 2 == 0:
            parity = 'even'
        else:
            parity = 'odd'
        self.income_tv.insert(
            parent='',
            index=index,
            iid=index,
            values=("SUBTOTAL", income_budget, income_actual),
            tags=(parity,)
        )
        # add colors based on tag
        self.income_tv.tag_configure("even", foreground="black", background="white")
        self.income_tv.tag_configure("odd", foreground="black", background="grey75")
        # set height based on number of income categories plus a subtotal row
        self.income_tv.config(height=len(income_categories) + 1)

        # add content to expense treeview
        self.expense_tv_header.config(columns=column_names[1:], selectmode='none', height=1)
        for k, v in column_dictionary.items():
            self.expense_tv_header.column(k, width=v, stretch='NO')

        self.expense_tv_header.insert(
            parent='', index=0, iid=0,
            value=('---EXPENSES---', 'Budget', 'Actual'),
            tags=('header',)
        )
        self.expense_tv_header.tag_configure("header", foreground="black", background="#5B9BD5")

        self.expense_tv.config(columns=column_names[1:], selectmode='browse', height=20)
        for k, v in column_dictionary.items():
            self.expense_tv.column(k, width=v, stretch='NO')

        # add user rows to expense_treeview based on given categories
        expense_table_rows = len(expense_categories)  # keep track of rows needed for treeview
        index = 0
        expense_budget = 0
        expense_actual = 0
        for index, value in enumerate(expense_categories):
            if index % 2 == 0:
                parity = 'even'
            else:
                parity = 'odd'
            # get cost of all transactions for a given expense category
            category_expense_total = 0
            for trans in transactions:
                if trans['category'] in value['name']:
                    category_expense_total += trans['outlay']
            self.expense_tv.insert(
                parent='',
                index=index,
                iid=index,
                values=(
                    value['name'],
                    value['budget'],
                    category_expense_total
                ),
                tags=(parity,)
            )
            expense_budget += value['budget']
            expense_actual += category_expense_total

        # add row to expense treeview for income taxes
        tax_category_name = 'Income'
        category_expense_total = 0
        expense_category_names = [category['name'] for category in expense_categories]
        expense_category_names.append(tax_category_name)
        for trans in transactions:
            if trans['category'] == tax_category_name:
                category_expense_total += trans['outlay']
        tax_total = 0
        for ic in income_categories:
            tax_total += ic['hourly_pay'] * ic['hours'] * ic['tax_rate']
        index += 1
        if index % 2 == 0:
            parity = 'even'
        else:
            parity = 'odd'
        self.expense_tv.insert(
            parent='',
            index=index,
            iid=index,
            values=("Income Tax", round(tax_total, 2), category_expense_total),
            tags=(parity,)
        )
        expense_table_rows += 1
        expense_budget += round(tax_total, 2)
        expense_actual += category_expense_total

        # add row for expense transactions which do not have a matching expense category (hide when empty)
        category_expense_total = 0
        for trans in transactions:
            if trans['category'] not in expense_category_names:
                category_expense_total += trans['outlay']
        if category_expense_total > 0:
            index += 1
            if index % 2 == 0:
                parity = 'even'
            else:
                parity = 'odd'
            self.expense_tv.insert(
                parent='',
                index=index,
                iid=index,
                values=("Uncategorized", Decimal('0.00'), category_expense_total),
                tags=(parity,)
            )
            expense_table_rows += 1
            expense_budget += Decimal('0.00')
            expense_actual += category_expense_total

        # add row for expense subtotals
        index += 1
        if index % 2 == 0:
            parity = 'even'
        else:
            parity = 'odd'
        self.expense_tv.insert(
            parent='',
            index=index,
            iid=index,
            values=("SUBTOTAL", expense_budget, expense_actual),
            tags=(parity,)
        )
        expense_table_rows += 1
        # add colors based on tag
        self.expense_tv.tag_configure("even", foreground="black", background="white")
        self.expense_tv.tag_configure("odd", foreground="black", background="grey75")
        # set number of rows
        self.expense_tv.config(height=expense_table_rows)

        # set up treeview to aggregate income and expense totals
        self.net_income_tv.config(columns=column_names[1:], selectmode='none', height=1)
        for k, v in column_dictionary.items():
            self.net_income_tv.column(k, width=v, stretch='NO')
        self.net_income_tv.insert(
            parent='', index=0, iid=0,
            value=('NET INCOME:', income_budget - expense_budget, income_actual - expense_actual),
            tags=('header',)
        )
        self.net_income_tv.tag_configure("header", foreground="white", background="#4b707e")

    def add_content_middle_frame(self):
        """Function to add middle frame with content. Determines which data to load."""

        # set up general variables
        column_names = self.job_column_names
        column_widths = self.job_column_widths

        column_dictionary = dict(zip(column_names, column_widths))

        # set new names for data in template_data
        jobs = self.view_data['income_categories']

        # add content to middle treeview header
        self.middle_tv_header.config(columns=column_names[1:], selectmode='none', height=1)
        for k, v in column_dictionary.items():
            self.middle_tv_header.column(k, width=v, stretch='NO')

        self.middle_tv_header.insert(
            parent='', index=0, iid=0,
            value=('Job', 'Hourly Rate', 'Hours', 'Tax Rate', 'Wages'),
            tags=('header',)
        )
        self.middle_tv_header.tag_configure("header", foreground="black", background="#A5A5A5")

        # add content to middle treeview
        self.middle_tv.config(columns=column_names[1:], selectmode='browse', height=20)
        for k, v in column_dictionary.items():
            self.middle_tv.column(k, width=v, stretch='NO')

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
                    value['hourly_pay'],
                    value['hours'],
                    value['tax_rate'],
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
        column_dictionary = dict(zip(column_names, column_widths))

        # set new name(s) for data in template_data
        transactions = self.view_data['transactions']

        # add content to transaction treeview header
        self.transaction_tv_header.config(columns=column_names[1:], selectmode='none', height=1)
        for k, v in column_dictionary.items():
            self.transaction_tv_header.column(k, width=v, stretch='NO')

        self.transaction_tv_header.insert(
            parent='', index=0, iid=0,
            value=tuple(name.title() for name in column_names[1:]),
            tags=('header',)
        )
        self.transaction_tv_header.tag_configure("header", foreground="black", background="#ED7D31")

        # add content to transaction treeview
        self.transaction_tv.config(columns=column_names[1:], selectmode='browse', height=20)
        for k, v in column_dictionary.items():
            self.transaction_tv.column(k, width=v, stretch='NO')

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
                    value['outlay'],
                    value['inflow'],
                    value['inflow'] - value['outlay']
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

        self._modify_category_window(
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
            self._modify_category_window(
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
            self._modify_category_window(
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

    def _modify_category_window(self, call, title, entry_defaults, button_text, row=0):
        """
        Method used to add, edit or insert a row to the expense category treeview.

        This is done by creating entry widgets that the user enters data into and then submits.
        This is a private method called by methods which determine whether this method is
        used to add, edit or insert data.
        """

        modify_window = tk.Toplevel(self)
        modify_window.wm_title(title)

        entry_names = self.editable_category_column_names
        function_calls = self.editable_category_column_datatypes

        entries = {}  # holds data submitted

        def call_update_frames():
            """
            Helper function which extracts entry widgets' values. It then adds, inserts, or edits an expense category
            to the active expense category list. It finally refreshes BudgetView.
            """

            new_entry = {en: function_calls[k](entries[en].get()) for k, en in enumerate(entry_names)}
            if call == "add":
                self.view_data['expense_categories'].append(new_entry)
            elif call == "insert":
                self.view_data['expense_categories'].insert(int(row), new_entry)
            elif call == "edit":
                self.view_data['expense_categories'][int(row)] = new_entry
            self.update_frames()

        i = 0
        for i, name in enumerate(entry_names):
            ttk.Label(modify_window, text=name.title()).grid(column=i, row=0)
            entries[name] = ttk.Entry(modify_window)
            entries[name].insert(0, entry_defaults[i])
            entries[name].grid(column=i, row=1)
        modify_button = ttk.Button(modify_window, text=button_text, command=call_update_frames)
        modify_button.grid(column=i, row=2, sticky='e')

    def call_transaction_popup_menu(self, event):
        """Method to create a small popup menu for the transaction treeview"""

        try:
            self.transaction_popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.transaction_popup_menu.grab_release()

    def add_transaction(self):
        """Add new transaction to transaction treeview by calling private method."""

        self._modify_transactions_window(
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
            self._modify_transactions_window(
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
            self._modify_transactions_window(
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

    def _modify_transactions_window(self, call, title, entry_defaults, button_text, row=0):
        """
        Method used to add, edit or insert a row to the transactions treeview.

        This is done by creating entry widgets that the user enters data into and then submits.
        This is a private method called by methods which determine whether this method is
        used to add, edit or insert data.
        """

        modify_transaction_window = tk.Toplevel(self)
        modify_transaction_window.wm_title(title)

        entry_names = self.editable_transaction_column_names
        function_calls = self.editable_transaction_column_datatypes

        entries = {}  # holds data submitted

        def call_update_frames():
            """
            Helper function which extracts entry widgets' values. It then adds, inserts, or edits a transaction to
            the active transaction list. It finally refreshes BudgetView.
            """

            new_entry = {en: function_calls[k](entries[en].get()) for k, en in enumerate(entry_names)}
            if call == "add":
                self.view_data['transactions'].append(new_entry)
            elif call == "insert":
                self.view_data['transactions'].insert(int(row), new_entry)
            elif call == "edit":
                self.view_data['transactions'][int(row)] = new_entry
            self.update_frames()

        i = 0
        for i, name in enumerate(entry_names):
            ttk.Label(modify_transaction_window, text=name.title()).grid(column=i, row=0)
            entries[name] = ttk.Entry(modify_transaction_window)
            entries[name].insert(0, entry_defaults[i])
            entries[name].grid(column=i, row=1)
        modify_transaction_button = ttk.Button(modify_transaction_window, text=button_text, command=call_update_frames)
        modify_transaction_button.grid(column=i, row=2, sticky='e')

    def call_job_popup_menu(self, event):
        """Method to create a small popup menu for the middle treeview"""

        try:
            self.job_popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.job_popup_menu.grab_release()

    def add_job(self):
        """Add new job to middle treeview by calling private method."""

        self._modify_jobs_window(
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
            self._modify_jobs_window(
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
            self._modify_jobs_window(
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

    def _modify_jobs_window(self, call, title, entry_defaults, button_text, row=0):
        """
        Method used to add, edit or insert a row to the middle treeview.

        This is done by creating entry widgets that the user enters data into and then submits.
        This is a private method called by methods which determine whether this method is
        used to add, edit or insert data.
        """

        modify_window = tk.Toplevel(self)
        modify_window.wm_title(title)

        entry_names = self.editable_job_column_names
        function_calls = self.editable_job_column_datatypes

        entries = {}  # holds data submitted

        def call_update_frames():
            """
            Helper function which extracts entry widgets' values. It then adds, inserts, or edits a
            job to the active job list. It finally refreshes BudgetView.
            """

            new_entry = {en: function_calls[k](entries[en].get()) for k, en in enumerate(entry_names)}
            if call == "add":
                self.view_data['income_categories'].append(new_entry)
            elif call == "insert":
                self.view_data['income_categories'].insert(int(row), new_entry)
            elif call == "edit":
                self.view_data['income_categories'][int(row)] = new_entry
            self.update_frames()

        i = 0
        for i, name in enumerate(entry_names):
            ttk.Label(modify_window, text=name.title()).grid(column=i, row=0)
            entries[name] = ttk.Entry(modify_window)
            entries[name].insert(0, entry_defaults[i])
            entries[name].grid(column=i, row=1)
        modify_button = ttk.Button(modify_window, text=button_text, command=call_update_frames)
        modify_button.grid(column=i, row=2, sticky='e')

    def get_previous_budget(self):
        if self.master.data_model.template_data['type'] == 'template':
            print("This is a template.")
            return
        current_budget = self.master.data_model.template_data['current_budget']
        placement = self.master.data_model.template_data['order'].index(current_budget)
        if placement > 0:
            previous_budget = self.master.data_model.template_data['order'][placement - 1]
        else:
            print("There are no earlier budgets!")
            return
        self.master.data_model.template_data["current_budget"] = previous_budget
        self.view_data = self.master.data_model.template_data[previous_budget]
        self.update_frames()

    def get_next_budget(self):
        if self.master.data_model.template_data['type'] == 'template':
            print("This is a template.")
            return
        current_budget = self.master.data_model.template_data['current_budget']
        placement = self.master.data_model.template_data['order'].index(current_budget)
        try:
            next_budget = self.master.data_model.template_data['order'][placement + 1]
            self.master.data_model.template_data["current_budget"] = next_budget
            self.view_data = self.master.data_model.template_data[next_budget]
            self.update_frames()
        except IndexError:
            create_next_budget = messagebox.askyesno(
                title="Add Next Budget",
                message="There is no next budget!",
                detail="Create it?"
            )
            if create_next_budget:
                next_budget = current_budget
                add_next_budget_window = tk.Toplevel(self)
                add_next_budget_window.wm_title("Add Next Budget")

                def gather_info():
                    nonlocal next_budget

                    next_budget = next_name.get()

                    if next_budget in self.master.data_model.template_data["order"]:
                        messagebox.showerror(
                            title="Name Error",
                            message="Budget name already in use!",
                            detail="Choose another name."
                        )
                    else:
                        self.master.data_model.template_data["current_budget"] = next_budget
                        self.master.data_model.template_data["order"].append(next_budget)
                        self.master.data_model.template_data[next_budget] = {
                            'income_categories': [],
                            'expense_categories': [],
                            'transactions': [],
                        }
                        self.view_data = self.master.data_model.template_data[next_budget]
                        self.update_frames()
                        add_next_budget_window.destroy()
                        add_next_budget_window.update()

                label = ttk.Label(add_next_budget_window, text="Next Budget Name")
                next_name = ttk.Entry(add_next_budget_window)
                next_name_submit = ttk.Button(add_next_budget_window, text="Submit", command=gather_info)

                label.grid(column=0)
                next_name.grid(column=1)
                next_name_submit.grid(column=2)

            else:
                return

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


class CreateBudget(tk.Toplevel):
    """Class which has pop-up window with options for user to select when creating a new Budget."""

    def __init__(self, master, callbacks, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.callbacks = callbacks
        self.master = master

        self.wm_title("Create New Budget")

        text_label = ttk.Label(self, text="Budget Name")
        self.budget_name = ttk.Entry(self)
        submit_button = ttk.Button(self, text="Create", command=self.create_new_budget)

        text_label.grid(column=0, row=0)
        self.budget_name.grid(column=1, row=0)
        submit_button.grid(column=2, row=0)

        self.new_budget = {}

    def create_new_budget(self):
        """Sets defaults for a new budget and then calls method to reset BudgetView with new budget."""

        first_budget = "origin"

        self.new_budget["type"] = "budget"
        self.new_budget["name"] = self.budget_name.get()
        self.new_budget["current_budget"] = first_budget
        self.new_budget["order"] = [first_budget]
        self.new_budget[first_budget] = {
            'income_categories': [],
            'expense_categories': [],
            'transactions': [],
        }

        self._initiate_new_budget()

    def _initiate_new_budget(self):
        """Resets BudgetView with new budget."""

        self.master.data_model.template_data = self.new_budget

        newest_budget = self.new_budget['order'][-1]
        self.view_data = self.new_budget[newest_budget]
        self.master.budget_view.view_data = self.new_budget[newest_budget]
        self.callbacks['update_frames']()


class SaveBudget:
    """Class which has pop-up window with options for user to save a budget group."""

    def __init__(self, master, callbacks, *args, **kwargs):
        self.callbacks = callbacks
        self.master = master

        self.master.data_model.initiate_directory(self.master.data_model.budgets_path)

        mask = [("CSV files", "*.csv"), ("All files", "*.*")]

        fp = filedialog.asksaveasfilename(
            title="Save Budget Group As",
            initialdir=self.master.data_model.budgets_path,
            initialfile="new_group.csv",
            filetypes=mask
        )

        if fp:
            self.callbacks["save_budget_group"](fp)


class OverwriteDirectory:
    """Class containing function which calls a popup window asking if the user wants to overwrite a directory."""

    @staticmethod
    def call_messagebox(directory_name):
        return messagebox.askokcancel(
            title="Directory Exists",
            message=f"A directory called {directory_name} already exists!",
            detail="Do you want to overwrite?"
        )
