import numpy as nm
import pytesseract
import re
import pydirectinput
import time
import cv2
import math
from PIL import ImageGrab
from PIL import ImageFilter
import sched
import sys
import tkinter
from tkinter import ttk, simpledialog, messagebox
from throttle import *
import requests
import logging
from win32 import win32api
import webbrowser
import ctypes
from ahk import AHK
from multiprocessing import Process, Value
import socket
from flask import Flask
from flask import render_template
from flask import request, redirect, send_file

active = Value(ctypes.c_bool, False)
newchange = Value(ctypes.c_bool, False)

def ws(active, newchange):
    app = Flask(__name__)
    @app.route('/')
    def home():
        return render_template("index.html", toggle=active.value)

    @app.route('/status')
    def status():
        status = { "toggle": active.value }
        return status

    @app.route('/status/off')
    def status_off():
        active.value = False
        status = { "toggle": active.value, "response": 200 }
        return status

    @app.route('/status/on')
    def status_on():
        active.value = True
        status = { "toggle": active.value, "response": 200 }
        return status
    @app.route('/shot')
    def shot():
        im = ImageGrab.grab()
        im.save("temp/screenshot.png")
        return send_file("temp/screenshot.png", "PNG")

    @app.route("/send", methods=["POST"])
    def send():
        newchange.value = True
        form = request.form
        try:
            if form["switch"] == "on":
                active.value = True
            else:
                active.value = False
        except:
            active.value = False
        return redirect("/")

    def run():
        app.run(host='0.0.0.0', port='7878')
    run()

if __name__ == '__main__':
    root = tkinter.Tk()
    photo = tkinter.PhotoImage(file="img/ap_icon_new.png")
    root.title("button")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    w = 50
    h = 50
    x = 100
    y = 100
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.lift()
    root.overrideredirect(True)
    root.call('wm', 'attributes', '.', '-topmost', '1')
    button = tkinter.Button(root, text="button1",
                            image=photo, bg="orange")
    button.grid(column=1, row=1, sticky=tkinter.E+tkinter.W)
    root.grid_columnconfigure(2, weight=2)
    try:
        ahk = AHK()
    except:
        print("AutoHotkey was not found! Please install it in order to continue.")
        exit()
    continue_route = False

    print("SCR-Autopilot v0.4.1-beta by MaTY (matyroblox01)")
    
    print("Checking for updates...")
    URL = "https://matyapi.matymt.repl.co/scr-autopilot/newest-version"
    r = requests.get(url=URL)
    data = r.json()
    version = data['version']
    if not version == "0.4.1":
        print("Your version is outdated! Please install the latest release on https://github.com/scr-autopilot/scr-autopilot/releases")
        outdatedask = messagebox.askyesno(
            "SCR-Autopilot", "Your version of SCR-Autopilot is outdated. Do you want to go to the releases page to download a new version?")
        if outdatedask == True:
            webbrowser.open(
                "https://github.com/scr-autopilot/scr-autopilot/releases")
            exit()
    else:
        print("Your version is up-to-date.")
    logging.basicConfig(filename='autopilot.log', filemode='w',
                        level=logging.DEBUG, format="[%(levelname)s] [%(asctime)s] %(message)s")
    print("\nDisclaimer:\nSCR-Autopilot is still in a beta version so it can't handle some situations well.\nWe recommend using SCR-Autopilot on private servers.\nUSE OF THIS SOFTWARE AT YOUR RISK.\nWaiting for the user input in the dialog box.")
    warningask = messagebox.askokcancel("Disclaimer", "SCR-Autopilot is still in a beta version so it can't handle some situations well.\nWe recommend using SCR-Autopilot on private servers.\n\nUSE OF THIS SOFTWARE AT YOUR RISK.", icon='warning')
    if warningask == False:
        exit()
    display_size = ImageGrab.grab().size
    logging.debug(f'Display resolution: {display_size[0]}, {display_size[1]}')
    resolution = simpledialog.askstring(
        "Question", "What is the resolution? (fhd, hd)")
    if resolution == "fhd":
        spd_pos = 884, 957, 947, 985
        lim_pos = 889, 987, 942, 1016
        green_pos = 1440, 983, 1441, 984
        yellow_pos = 1438, 1016, 1439, 1017
        double_yellow_pos = 1438, 950, 1439, 951
        red_pos = 1438, 1045, 1439, 1046
        distance_pos = 555, 1046, 605, 1070
        awsbutton_pos = 1330, 994, 1331, 995
        throttle_pos = 843, 931, 845, 1074
        doors_pos = 870, 822, 871, 823
        loading_pos = 781, 823, 782, 824
        continue_pos = 1032, 460, 1033, 461
        undershoot_pos = 709, 906, 710, 907
        awaiting_pos = 862, 823, 863, 824
        buzzer_pos = 824, 816, 825, 817
    elif resolution == "hd":
        messagebox.showerror(
            "Error", 'HD resolution is discontinued in the current version.')
        sys.exit()
        time.sleep(1)
        spd_pos = 573, 594, 630, 630
        lim_pos = 569, 627, 618, 653
        green_pos = 1118, 624, 1119, 625
        yellow_pos = 1120, 654, 1121, 655
        double_yellow_pos = 1120, 590, 1121, 591
        red_pos = 1120, 688, 1121, 689
        distance_pos = 239, 686, 284, 708
        awsbutton_pos = 1047, 597, 1048, 598
        throttle_pos = 522, 570, 525, 713
    else:
        messagebox.showerror(
            "Error", 'Please type only "fhd" (without the quotation marks) if you have FHD monitor, or type "hd" (without the quotation marks) if you have HD monitor.')
        sys.exit()


    max_speed = simpledialog.askinteger(
        "Question", "What is the maximum speed of your train in MPH? (E.g. 100, 125, 75 etc.)", minvalue=1)
    continue_ask = messagebox.askyesno(
        "Question", "Would you like to automatically continue in the route after finsihing?")
    if max_speed == None:
        messagebox.showerror("Error", 'Settings incorrect. Please try again.')
        exit()
    if continue_ask == True:
        continue_route = True
    PROCESS_PER_MONITOR_DPI_AWARE = 2
    MDT_EFFECTIVE_DPI = 0


    def print_dpi():
        shcore = ctypes.windll.shcore
        monitors = win32api.EnumDisplayMonitors()
        hresult = shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
        assert hresult == 0
        dpiX = ctypes.c_uint()
        dpiY = ctypes.c_uint()
        for i, monitor in enumerate(monitors):
            shcore.GetDpiForMonitor(
                monitor[0].handle,
                MDT_EFFECTIVE_DPI,
                ctypes.byref(dpiX),
                ctypes.byref(dpiY)
            )
            logging.debug(
                f"Monitor {i} = dpiX: {dpiX.value}, dpiY: {dpiY.value}"
            )


    print_dpi()

    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
    time.sleep(1)
    solve = None
    continuing = False
    ignorelim = False
    ignoreaws = False

    wsask = continue_ask = messagebox.askyesno(
        "Question", "Would you like to start a webserver so you can remotely control the autopilot?")
    if wsask == True:
        print("Starting the webserver...")
        p = Process(target=ws, args=(active,newchange,))
        p.start()
        time.sleep(3)
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    print("""  ___  ___ ___      _       _            _ _     _   
    / __|/ __| _ \___ /_\ _  _| |_ ___ _ __(_) |___| |_
    \__ \ (__|   /___/ _ \ || |  _/ _ \ '_ \ | / _ \  _|
    |___/\___|_|_\  /_/ \_\_,_|\__\___/ .__/_|_\___/\__|
                                    |_|               
    """)
    print("Press the red button that has appeared on your screen to engage the autopilot. You can press the button again to disengage the autopilot.")
    if wsask == True:
        print("\n\nFor the remote control, navigate to:", "http://" + socket.gethostbyname(socket.gethostname()) + ":7878 on a different device.","\nYou need to be on a same network to open the website.\n\n")
    print("Settings:")
    print("Screen resolution:", resolution)
    print("Train max speed:", max_speed)
    print("Automatically continue:", continue_route)


    def task():
        global solve
        global continuing
        global ignorelim
        global ignoreaws
        print("ignorelim", ignorelim)
        if continue_route == True:
            im = ImageGrab.grab(bbox=(continue_pos))
            pix = im.load()
            continue_value = pix[0, 0]  # Set the RGBA Value of the image (tuple)
            if continue_value == (255, 255, 255):
                continuing = True
                ahk.click(991, 470)
                ahk.click(327, 833)
        im = ImageGrab.grab(bbox=(awsbutton_pos))
        pix = im.load()
        awsbutton_value = pix[0, 0]  # Set the RGBA Value of the image (tuple)
        if awsbutton_value == (255, 255, 255):
            pydirectinput.keyDown("q")
            pydirectinput.keyUp("q")
            print("Reset the AWS")
        logging.debug(f'AWS pixel RGB: {awsbutton_value}')
        cap = ImageGrab.grab(bbox=(throttle_pos))
        img = cap
        count = 0
        bottom_throttle_pixel = None
        for y in range(img.height):
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                if y == img.height - 1:
                    bottom_throttle_pixel = pixel
                if pixel == (0, 176, 85):
                    count += 1

        currentThrottle = int(math.floor(100 * (count / 142)))
        speed = currentThrottle/100 * max_speed

        if currentThrottle == 0:
            logging.debug(f'Throttle pixel RGB: {bottom_throttle_pixel}')
        print("Current throttle: ", currentThrottle)
        if currentThrottle == None:
            messagebox.showerror("Error", "I can't read the throttle")
            supportask = messagebox.askyesno(
                "Question", "It looks like you got an error. You can try again, but if this error persists, you can join the support server. Do you want to join the support server on Discord?")
            if supportask == True:
                webbrowser.open(
                    "https://discord.gg/jtQ2R8cxWq")
                exit()
        else:
            # LIMIT
            cap = ImageGrab.grab(bbox=(lim_pos))
            cap = cap.filter(ImageFilter.MedianFilter())
            cap = cv2.cvtColor(nm.array(cap), cv2.COLOR_RGB2GRAY)
            tesstr = pytesseract.image_to_string(
                cap,
                config="--psm 7")
            lim = 0
            lim = [int(s) for s in re.findall(r'\b\d+\b', tesstr)]
            if lim == []:
                if continuing == False and ignorelim == False:
                    messagebox.showerror("Error", "I can't read the limit")
                    supportask = messagebox.askyesno(
                        "Question", "It looks like you got an error. You can try again, but if this error persists, you can join the support server. Do you want to join the support server on Discord?")
                    if supportask == True:
                        webbrowser.open(
                            "https://discord.gg/jtQ2R8cxWq")
                        exit()
            else:
                cap = ImageGrab.grab()
                src = nm.array(cap)
                gray = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
                gray = cv2.medianBlur(gray, 5)
                rows = gray.shape[0]
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                        param1=100, param2=30,
                                        minRadius=1, maxRadius=30)
                
                if circles is not None:
                    circles = nm.uint16(nm.around(circles))
                    for i in circles[0, :]:
                        x = i[0] - i[2]
                        y = i[1] - i[2]
                        w = 2*i[2]
                        h = 2*i[2]
                        center = (i[0], i[1])
                        if w > 39:
                            txt = pytesseract.image_to_string(gray[y:y+h, x:x+w], config="--psm 6")
                            if "W" in txt:
                                pydirectinput.keyDown("h")
                                pydirectinput.keyUp("h")
                        cv2.circle(src, center, 1, (0, 100, 100), 3)
                        radius = i[2]
                        cv2.circle(src, center, radius, (255, 0, 255), 3)

                templim = lim[0]
                lim = lim[0]
                lim = int(lim)
                if ignoreaws == False:
                    im = ImageGrab.grab(bbox=(red_pos))
                    pix = im.load()
                    # Set the RGBA Value of the image (tuple)
                    red_value = pix[0, 0]
                    im = ImageGrab.grab(bbox=(yellow_pos))
                    pix = im.load()
                    # Set the RGBA Value of the image (tuple)
                    yellow_value = pix[0, 0]
                    im = ImageGrab.grab(bbox=(green_pos))
                    pix = im.load()
                    # Set the RGBA Value of the image (tuple)
                    green_value = pix[0, 0]
                    im = ImageGrab.grab(bbox=(double_yellow_pos))
                    pix = im.load()
                    # Set the RGBA Value of the image (tuple)
                    double_yellow_value = pix[0, 0]
                    if red_value == (255, 0, 0):
                        print("AWS:", "red")
                        lim = 0
                    if yellow_value == (255, 190, 0):
                        print("AWS:", "yellow")
                        if templim > 45:
                            lim = 45
                    if double_yellow_value == (255, 190, 0):
                        print("AWS:", "double_yellow")
                        if templim > 75:
                            lim = 75
                    if green_value == (0, 255, 0):
                        print("AWS:", "green")

                print("Limit: ", lim)
                limitThrottle = int((lim / max_speed) * 100)

                print("Limit throttle: ", limitThrottle)

                cap = ImageGrab.grab(bbox=(distance_pos))
                cap = cap.filter(ImageFilter.MedianFilter())
                cap = cv2.cvtColor(nm.array(cap), cv2.COLOR_RGB2GRAY)
                tesstr = pytesseract.image_to_string(
                    cap,
                    config="--psm 6")
                distance = 0
                distance = [int(s) for s in re.findall(r'\b\d+\b', tesstr)]
                try:
                    m_distance = distance[0]
                    distance = distance[1]
                    print(m_distance, distance)
                    if distance == 00 and m_distance == 0 or continuing == True:
                        im = ImageGrab.grab(bbox=(loading_pos))
                        pix = im.load()
                        loading_value = pix[0, 0]
                        im = ImageGrab.grab(bbox=(doors_pos))
                        pix = im.load()
                        doors_value = pix[0, 0]
                        im = ImageGrab.grab(bbox=(undershoot_pos))
                        pix = im.load()
                        undershoot_value = pix[0, 0]
                        im = ImageGrab.grab(bbox=(awaiting_pos))
                        pix = im.load()
                        awaiting_value = pix[0, 0]
                        im = ImageGrab.grab(bbox=(buzzer_pos))
                        pix = im.load()
                        buzzer_value = pix[0, 0]
                        print(buzzer_value)
                        if undershoot_value == (255, 255, 255):
                            print("UNDERSHOOT")
                            pydirectinput.keyDown("w")
                            time.sleep(0.4)
                            pydirectinput.keyUp("w")
                        if doors_value == (255, 255, 255):
                            print("CLOSING DOORS")
                            pydirectinput.keyDown("t")
                            pydirectinput.keyUp("t")
                            time.sleep(4)
                            continuing = False
                            ignorelim = False
                            ignoreaws = False
                        elif loading_value == (255, 255, 255):
                            print("LOADING")
                        elif awaiting_value == (255, 255, 255):
                            print("WAITING FOR GUARD")
                        elif buzzer_value == (255, 255, 255):
                            print("ACTIVATING THE BUZZER")
                            pydirectinput.keyDown("t")
                            pydirectinput.keyUp("t")
                        else:
                            print("Autopilot is currently stopping.")
                            pydirectinput.keyDown("s")
                            time.sleep(5)
                            pydirectinput.keyUp("s")
                            pydirectinput.keyDown("t")
                            pydirectinput.keyUp("t")
                    elif distance <= 20 and m_distance == 0:
                        if lim >= 45:
                            print("Slowing down to prepare for station arrival.")
                            ignoreaws = True
                            ignorelim = True
                            throttle(currentThrottle, int((42 / max_speed) * 100))
                        else:
                            throttle(currentThrottle, limitThrottle)
                    else:
                        throttle(currentThrottle, limitThrottle)
                except IndexError:
                    pass
        solve = root.after(600, task)

    checkChanges = None
    def f_checkChanges():
        global checkChanges
        if newchange.value == True:
            newchange.value = False
            if active.value == True:
                button.configure(bg="green")
                root.after(600, task)
            elif active.value == False:
                button.configure(bg="red")
                try:
                    root.after_cancel(solve)
                except:
                    print("Error...")
        checkChanges = root.after(2000, f_checkChanges)
    checkChanges = root.after(2000, f_checkChanges)

    def onClick():
        if active.value == False:
            active.value = True
            button.configure(bg="green")
            root.after(600, task)
        else:
            active.value = False
            button.configure(bg="red")
            root.after_cancel(solve)

    button.configure(bg="red", command=onClick)
    switchask = messagebox.askyesno(
        "SCR-Autopilot", 'Autopilot is set up. Do you want to turn it on now? You can also turn it on or off by using the "AP" button on your screen.')
    if switchask == True:
        onClick()
    root.mainloop()
