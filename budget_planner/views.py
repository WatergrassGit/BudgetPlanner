import tkinter as tk
from tkinter import ttk
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
        income_treeview = ttk.Treeview(category_frame)
        expense_treeview = ttk.Treeview(category_frame)
        net_income_label = ttk.Label(category_frame, text="Net Income:")

        # set up widgets for middle frame
        middle_label = ttk.Label(middle_frame, text="Job Income")
        middle_treeview = ttk.Treeview(middle_frame)

        # content for transaction frame
        transaction_label = ttk.Label(transaction_frame, text="Transactions")
        transaction_treeview = ttk.Treeview(transaction_frame)

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
        middle_frame.grid(column=1, row=1, sticky='nwes')
        transaction_frame.grid(column=2, row=1, sticky='nwes')

        # grid content for category frame
        category_label.grid(row=0)
        income_treeview.grid(row=1)
        expense_treeview.grid(row=2)
        net_income_label.grid(row=3)

        # grid content for middle frame
        middle_label.grid(row=0)
        middle_treeview.grid(row=1)

        # grid content for transaction frame
        transaction_label.grid(row=0)
        transaction_treeview.grid(row=1)

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

        # set up events
        scrollable_frame.bind("<Configure>", self.get_canvas_size)

    def get_canvas_size(self, *args):
        _, _, self.canvas_width, self.canvas_height = self.canvas.bbox('all')
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              width=self.canvas_width,
                              height=self.canvas_height)
