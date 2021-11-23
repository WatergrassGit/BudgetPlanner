from os import path
IMAGE_DIRECTORY = path.dirname(__file__)

# Treeview checkbox images modified from originals:
# These three checkbox icons were isolated from
# Checkbox States.svg (https://commons.wikimedia.org/wiki/File:Checkbox_States.svg?uselang=en)
# by Marekich [CC BY-SA 3.0  (https://creativecommons.org/licenses/by-sa/3.0)]
IM_CHECKED = path.join(IMAGE_DIRECTORY, "checked.png")
IM_UNCHECKED = path.join(IMAGE_DIRECTORY, "unchecked.png")
IM_TRISTATE = path.join(IMAGE_DIRECTORY, "tristate.png")