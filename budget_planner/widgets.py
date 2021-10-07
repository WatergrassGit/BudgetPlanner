import tkinter as tk
from tkinter import ttk
from datetime import datetime
import decimal


class AutoScrollbar(ttk.Scrollbar):
    """Class from <https://www.geeksforgeeks.org/autohiding-scrollbars-using-python-tkinter/>
    which creates class AutoScrollbar that automatically hides scrollbars when not needed.
    Does not allow pack or place geometry management. Only allows grid geometry management."""

    # Defining set method with all
    # its parameter
    def set(self, low, high):

        if float(low) <= 0.0 and float(high) >= 1.0:

            # Using grid_remove
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        ttk.Scrollbar.set(self, low, high)

    # Defining pack method
    def pack(self, **kw):

        # If pack is used it throws an error
        raise (tk.TclError, "pack cannot be used with \
               this widget")

    # Defining place method
    def place(self, **kw):

        # If place is used it throws an error
        raise (tk.TclError, "place cannot be used  with \
               this widget")


class ValidatedMixin:
    """Adds a validation functionality to an input widget."""

    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)

        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)

        self.config(
            validate='all',
            validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
        )

    def _toggle_error(self, error=''):
        self.error.set(error)
        if error:
            self.config(foreground='red')
        else:
            self.config(foreground='black')

    def _validate(self, proposed, current, char, event, index, action):
        self._toggle_error()
        self.error.set('')
        valid = True
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action,
            )
        return valid

    def _focusout_validate(self, **kwargs):
        return True

    def _key_validate(self, **kwargs):
        return True

    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._key_invalid(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action,
            )

    def _focusout_invalid(self, **kwargs):
        self._toggle_error()

    def _key_invalid(self, **kwargs):
        pass

    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        # if not valid:
        #     self._focusout_invalid(event='focusout')
        return valid


class DateEntry(ValidatedMixin, ttk.Entry):
    """An Entry widget allowing only dates in for form YYYY-MM-DD to be entered."""

    def _invalid(self, proposed, current, char, event, index, action):
        if event != 'key':
            self._toggle_error('Not a valid date')

    def _key_validate(self, action, index, char, **kwargs):
        valid = True

        if action == '0':
            valid = True
        elif index in ('0', '1', '2', '3', '5', '6', '8', '9'):
            valid = char.isdigit()
        elif index in ('4', '7'):
            valid = char == '-'
        else:
            valid = False
        return valid

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            self.error.set('A value is required')
            valid = False
        else:
            try:
                datetime.strptime(self.get(), '%Y-%m-%d')
            except ValueError:
                self.error.set('Invalid date')
                valid = False
        return valid


class DollarEntry(ValidatedMixin, ttk.Entry):
    """An Entry widget allowing only valid dollar amounts with up to 2 decimal places."""

    def _invalid(self, proposed, current, char, event, index, action):
        if event != 'key':
            self._toggle_error('Not a valid dollar amount')

    def _key_validate(self, proposed, action, index, char, **kwargs):
        valid = True

        if action == '0':  # always allow backspace
            valid = True
        elif index == '0':  # allow digits or a "." for first character
            valid = char.isdigit() or char == "."
        elif len(proposed) == 2:  # check all cases of string length 2
            if proposed[0] == '0':
                if proposed[1] == '.':
                    valid = True
                else:
                    valid = False
            elif proposed[0] == '.':
                valid = char.isdigit()
            else:
                if char == '.':
                    valid = True
                else:
                    valid = char.isdigit()
        elif len(proposed) >= 4 and char.isdigit():  # ensure at most 2 decimal places
            if proposed[len(proposed) - 4] == '.':
                valid = False
            else:
                valid = True
        elif char.isdigit():
            valid = True
        elif char == '.':
            try:
                decimal.Decimal(proposed)
                valid = True
            except decimal.InvalidOperation:
                valid = False
        else:
            valid = False
        return valid

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            self.error.set('A value is required')
            valid = False
        else:
            try:
                decimal.Decimal(self.get())
            except (ValueError, decimal.InvalidOperation):
                self.error.set('Invalid dollar')
                valid = False
        return valid


class DecimalEntry(ValidatedMixin, ttk.Entry):
    """An Entry widget allowing only valid decimal amounts between 0 and 1."""

    def _invalid(self, proposed, current, char, event, index, action):
        if event != 'key':
            self._toggle_error('Not a valid dollar amount')

    def _key_validate(self, proposed, action, index, char, **kwargs):
        valid = True

        if action == '0':  # always allow backspace
            valid = True
        elif index == '0':  # allow digits or a "." for first character
            valid = char in ("0", "1") or char == "."
        elif len(proposed) == 2:  # check all cases of string length 2
            if proposed[0] == '0':
                if proposed[1] == '.':
                    valid = True
                else:
                    valid = False
            elif proposed[0] == '.':
                valid = char.isdigit()
            else:
                valid = (char.isdigit() or char == '.') and decimal.Decimal(proposed) <= decimal.Decimal("1")
        elif char.isdigit() and decimal.Decimal(proposed) <= decimal.Decimal("1"):
            valid = True
        elif char == '.':
            try:
                decimal.Decimal(proposed)
                valid = True
            except decimal.InvalidOperation:
                valid = False
        else:
            valid = False
        return valid

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            self.error.set('A value is required')
            valid = False
        else:
            try:
                decimal.Decimal(self.get())
            except (ValueError, decimal.InvalidOperation):
                self.error.set('Invalid Decimal')
                valid = False
        return valid


class RequiredEntry(ValidatedMixin, ttk.Entry):
    """An Entry widget which requires an input"""

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            self.error.set('A value is required')
            valid = False
        return valid
