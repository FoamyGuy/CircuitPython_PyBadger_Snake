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
import displayio
from displayio import Group
import supervisor
import terminalio
from adafruit_pybadger import pybadger
from displayio_listselect import ListSelect
import busio
import os
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server
import gc
from adafruit_wsgi.wsgi_app import WSGIApp
from adafruit_display_text.bitmap_label import Label

try:
    import json as json_module
except ImportError:
    import ujson as json_module

from simple_wsgi_application import SimpleWSGIApplication

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

display = board.DISPLAY

MENU_APPS = {"Snake": "code_snake_game.py", "IR Cam": "code_ir_cam.py"}
MENU_ITEMS = ["Snake", "IR Cam", "Back"]
# MENU_ITEMS = list(MENU_APPS.keys()) + ["Back"]
MENU_IDLE_TIMEOUT = 10  # secconds
MENU_SHOWING = False
MENU_START_TIME = None

LAST_IO_SYNC_TIME = -1
IO_SYNC_DELAY = 0.5

SELECT_RELEASED = True

previous_group = None

list_select = ListSelect(scale=2, items=MENU_ITEMS)
list_select.anchor_point = (0.5, 0.5)
list_select.anchored_position = (display.width // 2, display.height // 2)

pybadger.show_badge(
    name_string="Blinka", hello_scale=2, my_name_is_scale=2, name_scale=3
)

esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
"""Use below for Most Boards"""
# status_light = neopixel.NeoPixel(
#     board.NEOPIXEL, 1, brightness=0.2
# )  # Uncomment for Most Boards


wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)

# Connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected!")

web_app = WSGIApp()

f = open("static/index.html")
index_str = f.read()
f.close()

@web_app.route("/")
def index(request):

    return ("200 OK", [], index_str)


@web_app.route("/led_on/<r>/<g>/<b>")
def led_on(request, r, g, b):  # pylint: disable=unused-argument
    print("led on!")
    pybadger.pixels.fill((int(r), int(g), int(b)))
    return ("200 OK", [], index_str)

@web_app.route("/led_off")
def led_off(request):  # pylint: disable=unused-argument
    print("led off!")
    pybadger.pixels.fill(0)
    return ("200 OK", [], index_str)


# Here we setup our server, passing in our web_app as the application
server.set_interface(esp)
wsgiServer = server.WSGIServer(80, application=web_app)

print("open this IP in your browser: ", esp.pretty_ip(esp.ip_address))

# print(esp.get_time())
# Start the server
wsgiServer.start()

wifi_icon_bmp = displayio.OnDiskBitmap("wifi_14px.bmp")
wifi_icon_tg = displayio.TileGrid(bitmap=wifi_icon_bmp, pixel_shader=wifi_icon_bmp.pixel_shader)
wifi_icon_bmp.pixel_shader.make_transparent(0)

display.root_group.append(wifi_icon_tg)

rc_details_lbl = Label(terminalio.FONT, text=f"Open Browser To:\nhttp://{esp.pretty_ip(esp.ip_address)}",
                       line_spacing=1.0, color=0xffffff)
rc_details_lbl.anchor_point = (0.5, 1.0)
rc_details_lbl.anchored_position = (pybadger.display.width // 2, pybadger.display.height)

qr_screen_group = Group()
qr_screen_group.append(rc_details_lbl)

while True:

    pybadger.auto_dim_display(
        delay=10
    )  # Remove or comment out this line if you have the PyBadge LC
    if pybadger.button.a:
        try:
            display.root_group.remove(wifi_icon_tg)
        except ValueError:
            pass
        pybadger.show_business_card(
            image_name="Blinka.bmp",
            name_string="Blinka",
            name_scale=2,
            email_string_one="blinka@",
            email_string_two="adafruit.com",
        )
    elif pybadger.button.b:
        try:
            display.root_group.remove(wifi_icon_tg)
        except ValueError:
            pass
        not_empty = True
        while not_empty:
            try:
                _ = qr_screen_group.pop()
            except IndexError:
                not_empty = False

        pybadger.show_qr_code(data=f"http://{esp.pretty_ip(esp.ip_address)}")
        pybadger.display.root_group[0].y = 0

        scaled_qr_group = pybadger.display.root_group

        pybadger.display.root_group = qr_screen_group
        qr_screen_group.append(scaled_qr_group)
        qr_screen_group.append(rc_details_lbl)


    elif pybadger.button.start:
        try:
            display.root_group.remove(wifi_icon_tg)
        except ValueError:
            pass
        pybadger.show_badge(
            name_string="Blinka", hello_scale=2, my_name_is_scale=2, name_scale=3
        )
        display.root_group.append(wifi_icon_tg)
    elif pybadger.button.select:
        if SELECT_RELEASED:
            if not MENU_SHOWING:
                MENU_START_TIME = time.monotonic()
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

    if MENU_SHOWING:
        if MENU_START_TIME + MENU_IDLE_TIMEOUT <= time.monotonic():
            print("Menu Idle Timeout")
            pybadger.show(previous_group)
            MENU_SHOWING = False

    if LAST_IO_SYNC_TIME + IO_SYNC_DELAY <= time.monotonic():

        try:
            gc.collect()
            #print(f"free mem: {gc.mem_free()}")
            wsgiServer.update_poll()

            # Could do any other background tasks here, like reading sensors
        except OSError as e:
            print("Failed to update server, restarting ESP32\n", e)
            wifi.reset()
            continue


        LAST_IO_SYNC_TIME = time.monotonic()