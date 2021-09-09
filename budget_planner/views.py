import tkinter as tk
from tkinter import ttk
from decimal import Decimal
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
        self.add_content_middle_frame()
        self.add_content_transaction_frame()
        self.add_content_category_frame()

        # add styles
        self.styles = ttk.Style()
        self.set_styles()

        # set up events
        scrollable_frame.bind("<Configure>", self.get_canvas_size)

    def get_canvas_size(self, *args):
        _, _, self.canvas_width, self.canvas_height = self.canvas.bbox('all')
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              width=self.canvas_width,
                              height=self.canvas_height)

    def add_content_category_frame(self):
        """Function to add category frame with content. Determines which data to load."""

        column_names = ('budget_type', 'budget', 'actual')
        column_widths = (160, 80, 80)
        column_dictionary = {}
        for i, col in enumerate(column_names):
            column_dictionary[col] = column_widths[i]

        # add content to income treeview
        self.income_tv_header.config(
            columns=column_names,
            selectmode='none',
            height=1
        )
        self.income_tv_header.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.income_tv_header.column(k, width=v)

        self.income_tv_header.insert(
            parent='', index=0, iid=0,
            value=('---INCOME---', 'Budget', 'Actual'),
            tags=('header',)
        )
        self.income_tv_header.tag_configure("header", foreground="black", background="#70AD47")

        self.income_tv.config(
            columns=('budget_type', 'budget', 'actual'),
            selectmode='browse',
            height=20
        )
        self.income_tv.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.income_tv.column(k, width=v)

        job_with_budget = []
        income_jobs = self.template_data['job_list']
        for job in income_jobs:
            job_with_budget.append({job['name']: round(job['hourly_pay'] * job['hours'], 2)})
        income_categories = self.template_data['income_categories']
        for job in income_categories:
            job_with_budget.append({job: Decimal('0.00')})
        index = 0
        income_budget = 0
        income_actual = 0
        for index, value in enumerate(job_with_budget):
            for k, v in value.items():
                if index % 2 == 0:
                    parity = 'even'
                else:
                    parity = 'odd'
                self.income_tv.insert(
                    parent='',
                    index=index,
                    iid=index,
                    values=(k, v, 0),
                    tags=(parity,)
                )
                income_budget += v
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

        self.income_tv.tag_configure("even", foreground="black", background="white")
        self.income_tv.tag_configure("odd", foreground="black", background="grey75")

        self.income_tv.config(height=len(job_with_budget) + 1)

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

        expense_categories = self.template_data['expense_categories']
        index = 0
        expense_budget = 0
        expense_actual = 0
        for index, value in enumerate(expense_categories):
            for k, v in value.items():
                if index % 2 == 0:
                    parity = 'even'
                else:
                    parity = 'odd'
                self.expense_tv.insert(
                    parent='',
                    index=index,
                    iid=index,
                    values=(k, v, 0),
                    tags=(parity,)
                )
                expense_budget += v

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

        self.expense_tv.tag_configure("even", foreground="black", background="white")
        self.expense_tv.tag_configure("odd", foreground="black", background="grey75")

        self.expense_tv.config(height=len(expense_categories) + 1)

        #
        self.net_income_tv.config(
            columns=('budget_type', 'budget', 'actual'),
            selectmode='none',
            height=1
        )
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

        column_names = ('job', 'rate', 'hours', 'wages')
        column_widths = (80, 80, 50, 60)
        column_dictionary = {}
        for i, col in enumerate(column_names):
            column_dictionary[col] = column_widths[i]

        # add content to middle treeview
        self.middle_tv_header.config(
            columns=column_names,
            selectmode='none',
            height=1
        )
        self.middle_tv_header.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.middle_tv_header.column(k, width=v)

        self.middle_tv_header.insert(
            parent='', index=0, iid=0,
            value=('Job', 'Hourly Pay', 'Hours', 'Pay'),
            tags=('header',)
        )
        self.middle_tv_header.tag_configure("header", foreground="black", background="#A5A5A5")

        self.middle_tv.config(
            columns=column_names,
            selectmode='browse',
            height=20
        )
        self.middle_tv.column('#0', width=0, stretch='NO')
        for k, v in column_dictionary.items():
            self.middle_tv.column(k, width=v)

        jobs = self.template_data['job_list']
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
                    round(value['hourly_pay'] * value['hours'], 2)
                ),
                tags=(parity,)
            )

        self.middle_tv.tag_configure("even", foreground="black", background="#D9D9D9")
        self.middle_tv.tag_configure("odd", foreground="black", background="white")

        self.middle_tv.config(height=len(jobs))

    def add_content_transaction_frame(self):
        """Function to add transaction frame with content. Determines which data to load."""

        # add content to income treeview
        self.transaction_tv_header.config(
            columns=('date', 'location', 'category', 'payment', 'deposit', 'net'),
            selectmode='none',
            height=1
        )
        self.transaction_tv_header.column('#0', width=0, stretch='NO')
        self.transaction_tv_header.column('date', width=80)
        self.transaction_tv_header.column('location', width=160)
        self.transaction_tv_header.column('category', width=160)
        self.transaction_tv_header.column('payment', width=80)
        self.transaction_tv_header.column('deposit', width=80)
        self.transaction_tv_header.column('net', width=80)

        self.transaction_tv_header.insert(
            parent='', index=0, iid=0,
            value=('Date', 'Location', 'Category', 'Payment', 'Deposit', 'Net'),
            tags=('header',)
        )
        self.transaction_tv_header.tag_configure("header", foreground="black", background="#ED7D31")

        self.transaction_tv.config(
            columns=('date', 'location', 'category', 'payment', 'deposit', 'net'),
            selectmode='browse',
            height=20
        )
        self.transaction_tv.column('#0', width=0, stretch='NO')
        self.transaction_tv.column('date', width=80)
        self.transaction_tv.column('location', width=160)
        self.transaction_tv.column('category', width=160)
        self.transaction_tv.column('payment', width=80)
        self.transaction_tv.column('deposit', width=80)
        self.transaction_tv.column('net', width=80)

        transactions = self.template_data['transaction_list']
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
                    value['payment'] - value['deposit']
                ),
                tags=(parity,)
            )

        self.transaction_tv.tag_configure("even", foreground="black", background="#B4C6E7")
        self.transaction_tv.tag_configure("odd", foreground="black", background="#D9E1F2")

        self.transaction_tv.config(height=len(transactions))

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
