# SPDX-FileCopyrightText: 2023 Tim C
# SPDX-License-Identifier: MIT
"""
Adapted from PyBadger simpletest example.

Select button shows a menu to launch external python scripts,
select button while it's showing submits the selection on current item.

To add new scripts:
 - Add a name in MENU_ITEMS and MENU_APPS
 - Add a filename in MENU_APPS that points to the script
"""
import time
import board
import supervisor
from adafruit_pybadger import pybadger
from displayio_listselect import ListSelect

display = board.DISPLAY

MENU_APPS = {"Snake": "code_snake_game.py", "IR Cam": "code_ir_cam.py"}
MENU_ITEMS = ["Snake", "IR Cam", "Back"]
#MENU_ITEMS = list(MENU_APPS.keys()) + ["Back"]
MENU_SHOWING = False

SELECT_RELEASED = True

previous_group = None

list_select = ListSelect(scale=2, items=MENU_ITEMS)
list_select.anchor_point = (0.5, 0.5)
list_select.anchored_position = (display.width // 2, display.height // 2)

pybadger.show_badge(
    name_string="Blinka", hello_scale=2, my_name_is_scale=2, name_scale=3
)

while True:
    pybadger.auto_dim_display(
        delay=10
    )  # Remove or comment out this line if you have the PyBadge LC
    if pybadger.button.a:
        pybadger.show_business_card(
            image_name="Blinka.bmp",
            name_string="Blinka",
            name_scale=2,
            email_string_one="blinka@",
            email_string_two="adafruit.com",
        )
    elif pybadger.button.b:
        pybadger.show_qr_code(data="https://circuitpython.org")
    elif pybadger.button.start:
        pybadger.show_badge(
            name_string="Blinka", hello_scale=2, my_name_is_scale=2, name_scale=3
        )
    elif pybadger.button.select:
        if SELECT_RELEASED:
            if not MENU_SHOWING:
                previous_group = pybadger.display.root_group
                pybadger.show(list_select)
                MENU_SHOWING = True
            else:
                MENU_SHOWING = False
                print(f"user selected: {list_select.selected_item}")
                if list_select.selected_item in MENU_APPS.keys():
                    supervisor.set_next_code_file(MENU_APPS[list_select.selected_item])
                    supervisor.reload()

                elif list_select.selected_item == "Back":
                    pybadger.show(previous_group)
                else:  # Unknown item, just go back
                    pybadger.show(previous_group)

        SELECT_RELEASED = False

    elif pybadger.button.up:
        if MENU_SHOWING:
            list_select.move_selection_up()
            time.sleep(0.1)

    elif pybadger.button.down:
        if MENU_SHOWING:
            list_select.move_selection_down()
            time.sleep(0.1)
    else:
        SELECT_RELEASED = True
