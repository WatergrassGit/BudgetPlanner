import tkinter as tk
from tkinter import ttk
from decimal import Decimal
from datetime import date
from .widgets import AutoScrollbar


class BudgetView(ttk.Frame):
    """Page which shows selected budget to user."""

    def __init__(self, master, callbacks, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.callbacks = callbacks

        # set up widgets for primary layer
        self.canvas = tk.Canvas(self)
        self.v_scroll = AutoScrollbar(self, orient=tk.VERTICAL)
        bottom_frame = ttk.Frame(self)

        # set up scrollable frame
        scrollable_frame = ttk.Frame(self)

        # set up widgets for scrollable frame
        title_label = ttk.Label(scrollable_frame, text="Title: Current Budget")
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

        # set up widgets for middle frame
        middle_label = ttk.Label(middle_frame, text="Expected Job Income")
        self.middle_tv_header = ttk.Treeview(middle_frame, show='tree')
        self.middle_tv = ttk.Treeview(middle_frame, show='tree')

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
            command=lambda: print("Not yet available...")
        )
        next_button = ttk.Button(
            bottom_frame,
            text="Next",
            command=lambda: self.get_canvas_size()
        )
        self.h_scroll = ttk.Scrollbar(bottom_frame, orient=tk.HORIZONTAL)

        # grid primary layer widgets
        self.canvas.grid(column=0, row=0, sticky='nw')
        self.v_scroll.grid(column=1, row=0, sticky='ns')
        bottom_frame.grid(column=0, row=1, sticky='nwes')

        # grid scrollable frame widgets
        title_label.grid(column=0, row=0, columnspan=3, sticky=(tk.W + tk.E))
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
        self.template_data = self.callbacks['get_template_data']()
        self.income_categories = []  # list of strings
        self.expense_categories = []  # list of dictionaries with category name and category budget
        self.job_list = []  # list of dictionaries with name / hourly_pay / hours / pay
        # transaction list contains dictionaries with date / location / category / payment / deposit / net
        self.transaction_list = []

        # fill BudgetView with content
        self.transaction_column_names = ('#0', 'date', 'location', 'category', 'payment', 'deposit', 'net')
        self.editable_transaction_column_names = ('date', 'location', 'category', 'payment', 'deposit')
        self.editable_transaction_column_datatypes = [str, str, str, Decimal, Decimal]
        self.transaction_column_widths = (0, 80, 160, 160, 80, 80, 80)
        self._update_frames()

        # add styles
        self.styles = ttk.Style()
        self.set_styles()

        # set up events
        scrollable_frame.bind("<Configure>", self.get_canvas_size)
        self.transaction_tv.bind("<Button-3>", self.call_transaction_popup_menu)

    def get_canvas_size(self, *args):
        _, _, self.canvas_width, self.canvas_height = self.canvas.bbox('all')
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              width=self.canvas_width,
                              height=self.canvas_height)

    def _update_frames(self):
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
        self.net_income_tv.grid()
        self.add_content_category_frame()  # repopulate

    def add_content_category_frame(self):
        """Function to add category frame with content. Determines which data to load."""

        column_names = ('budget_type', 'budget', 'actual')
        column_widths = (160, 80, 80)
        column_dictionary = dict(zip(column_names, column_widths))

        # set new names for data in template_data
        income_categories = self.template_data['income_categories']
        expense_categories = self.template_data['expense_categories']
        transactions = self.template_data['transaction_list']

        # add content to income treeview
        # add the header income treeview
        self.income_tv_header.config(columns=column_names, selectmode='none', height=1)
        self.income_tv_header.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.income_tv_header.column(k, width=v)
        self.income_tv_header.insert(
            parent='', index=0, iid=0,
            value=('---INCOME---', 'Budget', 'Actual'),
            tags=('header',)
        )
        self.income_tv_header.tag_configure("header", foreground="black", background="#70AD47")

        # add the main income treeview
        self.income_tv.config(columns=column_names, selectmode='browse')
        self.income_tv.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.income_tv.column(k, width=v)

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
                if trans['category'] in "Income" and trans['location'] in value['name']:
                    category_income_total += trans['deposit']
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
        self.expense_tv_header.config(
            columns=('budget_type', 'budget', 'actual'),
            selectmode='none',
            height=1
        )
        self.expense_tv_header.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.expense_tv_header.column(k, width=v)

        self.expense_tv_header.insert(
            parent='', index=0, iid=0,
            value=('---EXPENSES---', 'Budget', 'Actual'),
            tags=('header',)
        )
        self.expense_tv_header.tag_configure("header", foreground="black", background="#5B9BD5")

        self.expense_tv.config(
            columns=('budget_type', 'budget', 'actual'),
            selectmode='browse',
            height=20
        )
        self.expense_tv.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.expense_tv.column(k, width=v)

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
                    category_expense_total += trans['payment']
            self.expense_tv.insert(
                parent='',
                index=index,
                iid=index,
                values=(
                    value['name'],
                    value['expense_budget'],
                    category_expense_total
                ),
                tags=(parity,)
            )
            expense_budget += value['expense_budget']
            expense_actual += category_expense_total

        # add row to expense treeview for income taxes
        tax_category_name = 'Income'
        category_expense_total = 0
        expense_category_names = [category['name'] for category in expense_categories]
        expense_category_names.append(tax_category_name)
        for trans in transactions:
            if trans['category'] == tax_category_name:
                category_expense_total += trans['payment']
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
        expense_actual += category_expense_total

        # add row for expense transactions which do not have a matching expense category (hide when empty)
        category_expense_total = 0
        for trans in transactions:
            if trans['category'] not in expense_category_names:
                category_expense_total += trans['payment']
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
        self.net_income_tv.config(columns=column_names, selectmode='none', height=1)
        self.net_income_tv.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.net_income_tv.column(k, width=v)
        self.net_income_tv.insert(
            parent='', index=0, iid=0,
            value=('NET INCOME:', income_budget - expense_budget, income_actual - expense_actual),
            tags=('header',)
        )
        self.net_income_tv.tag_configure("header", foreground="white", background="#4b707e")

    def add_content_middle_frame(self):
        """Function to add middle frame with content. Determines which data to load."""

        # set up general variables
        column_names = ('job', 'rate', 'hours', 'tax_rate', 'wages')
        column_widths = (80, 80, 50, 70, 60)
        column_dictionary = dict(zip(column_names, column_widths))

        # set new names for data in template_data
        jobs = self.template_data['income_categories']

        # add content to middle treeview header
        self.middle_tv_header.config(columns=column_names, selectmode='none', height=1)
        self.middle_tv_header.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.middle_tv_header.column(k, width=v, stretch='NO')

        self.middle_tv_header.insert(
            parent='', index=0, iid=0,
            value=('Job', 'Hourly Pay', 'Hours', 'Tax Rate', 'Pay'),
            tags=('header',)
        )
        self.middle_tv_header.tag_configure("header", foreground="black", background="#A5A5A5")

        # add content to middle treeview
        self.middle_tv.config(columns=column_names, selectmode='browse', height=20)
        self.middle_tv.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.middle_tv.column(k, width=v)

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
        transactions = self.template_data['transaction_list']

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
                    value['location'],
                    value['category'],
                    value['payment'],
                    value['deposit'],
                    value['deposit'] - value['payment']
                ),
                tags=(parity,)
            )

        self.transaction_tv.tag_configure("even", foreground="black", background="#B4C6E7")
        self.transaction_tv.tag_configure("odd", foreground="black", background="#D9E1F2")
        self.transaction_tv.config(height=len(transactions))

    def call_transaction_popup_menu(self, event):
        """Method to create a small popup menu for the transaction treeview"""

        try:
            self.transaction_popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.transaction_popup_menu.grab_release()

    def add_transaction(self):
        """Add new transaction to transaction treeview by calling internal method."""

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
            defaults = self.template_data['transaction_list'][int(row)]  # get data from selected treeview row
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
            del self.template_data['transaction_list'][int(row)]  # remove selected treeview row
            self._update_frames()

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
                self.template_data['transaction_list'].append(new_entry)
            elif call == "insert":
                self.template_data['transaction_list'].insert(int(row), new_entry)
            elif call == "edit":
                self.template_data['transaction_list'][int(row)] = new_entry
            self._update_frames()

        i = 0
        for i, name in enumerate(entry_names):
            ttk.Label(modify_transaction_window, text=name.title()).grid(column=i, row=0)
            entries[name] = ttk.Entry(modify_transaction_window)
            entries[name].insert(0, entry_defaults[i])
            entries[name].grid(column=i, row=1)
        modify_transaction_button = ttk.Button(modify_transaction_window, text=button_text, command=call_update_frames)
        modify_transaction_button.grid(column=i, row=2, sticky='e')

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
