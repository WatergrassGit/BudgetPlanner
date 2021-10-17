================
 Budget Planner
================

Description
===========

This program will use Tkinter to allow the user to make budgets and record financial transactions. The program will be designed with sequential budgeting periods in mind.

Features (future)
-----------------

* Easily scroll between budgets in sequential order.
* Allow users to add new budgets.
* Store income tables, expense tables, and transactions for each budget period.

Authors
=======

MH, 2021

Main Requirements
=================

* Python 3.7
* Tkinter

General Notes
=============

The program consists of two main data structures referred to as a template and a budget grouping. Both are dictionaries
and we describe their content below:

* template (dict)
    - 'type' (key, str): 'template' (str)
    - 'name' (key, str): 'Template' (str)
    - 'template' (key, str): dict
        + income_categories (key, str): list containing dictionaries
        + expense_categories (key, str): list containing dictionaries
        + transactions (key, str): list containing dictionaries
* grouping (dict)
    - 'type' (key, str): 'budget' (str)
    - 'name' (key, str): '*' (str)
    - 'current_budget' (key, str): '*' (str)
    - 'order' (key, str): list of budget names
    - 'budget' (key, str): dictionary of budgets
        + 'budget1' (key, str): dict
            * income_categories (key, str): list containing dictionaries
            * expense_categories (key, str): list containing dictionaries
            * transactions (key, str): list containing dictionaries
        + 'budget2' (key, str): dict

Data will be stored in JSON or CSV files.

Future Goals
============

To be filled in at a later date.
