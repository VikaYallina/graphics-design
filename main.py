# Graphics & design class assignment 1
#
# Task:   given a picture figure out where the red balls(spherical shape) are and mark them
# Input:  a non-trivial picture (jpg, png??)
# Output: a new picture where all of the red balls are marked and possibly numbered(how?)

# Possible solution:
#   1. Find out the spectrum of color red
#   2. Define all areas that are colored red in the picture
#   3. Result is a color matrix where only red spectrum is left, all other colors are nulled
#   4. Try to figure out the shapes of the red ares in the color matrix - How??
#   5. Mark the outlines of the spheres in the original matrix with some color(green)
#   6. profit?


#  Problems
#   1. Many balls in one area == giant unidentified shape
#   2. The red ball might not be fully in frame(cut by some object)

from PIL import Image, ImageTk
import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.img = None
        self.out = None
        self.filename = ""

        self.img1 = tk.Label(self.master, text="here1")
        self.img1.grid(row=1, column=0)
        self.img2 = tk.Label(self.master, text="here2")
        self.img2.grid(row=1, column=1)

        self.file_select = tk.Button(self.master, text="Choose image", command=self.callback) \
            .grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_btn = tk.Button(self.master, text="Start", command=self.task) \
            .grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(self.master, text="Dp").grid(row=2, column=0)
        self.dp_entry = tk.Entry(self.master)
        self.dp_entry.grid(row=2, column=1)
        self.dp_entry.insert(0, "1.0")

        tk.Label(self.master, text="minDist").grid(row=3, column=0)
        self.minDist_entry = tk.Entry(self.master)
        self.minDist_entry.grid(row=3, column=1)
        self.minDist_entry.insert(0, "50")

        tk.Label(self.master, text="param1").grid(row=4, column=0)
        self.param1_entry = tk.Entry(self.master)
        self.param1_entry.grid(row=4, column=1)
        self.param1_entry.insert(0, "450")

        tk.Label(self.master, text="param2").grid(row=5, column=0)
        self.param2_entry = tk.Entry(self.master)
        self.param2_entry.grid(row=5, column=1)
        self.param2_entry.insert(0, "20")

        tk.Label(self.master, text="minRadius").grid(row=6, column=0)
        self.minRadius_entry = tk.Entry(self.master)
        self.minRadius_entry.grid(row=6, column=1)
        self.minRadius_entry.insert(0, "15")

        tk.Label(self.master, text="maxRadius").grid(row=7, column=0)
        self.maxRadius_entry = tk.Entry(self.master)
        self.maxRadius_entry.grid(row=7, column=1)
        self.maxRadius_entry.insert(0, "40")

    def callback(self):
        self.filename = filedialog.askopenfilename(filetypes=[
            ("Images", ".jpeg .jpg .png"),
            ("JPEG", ".jpeg"),
            ("JPG", ".jpg"),
            ("PNG", ".png"),
        ])
        self.img = Image.open(self.filename, mode="r")
        h, w = self.img.size
        self.img = self.img.resize((int(h / 2), int(w / 2)))
        self.img = ImageTk.PhotoImage(self.img)
        self.img1.config(image=self.img)
        self.img1.image = self.img

    def task(self):
        im = cv2.imread(self.filename)
        out = im.copy()
        # Преобразование изображения в цветовую модель hsv
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        # Нижние границы красного
        low_b1 = np.array([0, 100, 100])
        high_b1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, low_b1, high_b1)
        # Верхние границы
        low_b2 = np.array([160, 100, 100])
        high_b2 = np.array([179, 255, 255])
        mask2 = cv2.inRange(hsv, low_b2, high_b2)

        mask_comb = cv2.add(mask1, mask2)
        res = cv2.bitwise_and(im, im, mask=mask_comb)

        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 13)
        gray_lap = cv2.Laplacian(gray_blur, cv2.CV_8UC1, ksize=5)
        dilate_lap = cv2.dilate(gray_lap, (3, 3))
        lap_blur = cv2.bilateralFilter(dilate_lap, 5, 9, 9)

        # Main function for detecting circles
        circles = cv2.HoughCircles(lap_blur, cv2.HOUGH_GRADIENT,
                                   float(self.dp_entry.get()),
                                   int(self.minDist_entry.get()),
                                   param1=int(self.param1_entry.get()),
                                   param2=int(self.param2_entry.get()),
                                   minRadius=int(self.minRadius_entry.get()),
                                   maxRadius=int(self.maxRadius_entry.get()))

        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(out, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(out, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            # show the output image
            out = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
            self.out = Image.fromarray(out)
            h, w = self.out.size
            self.out = self.out.resize((int(h / 2), int(w / 2)))
            self.out = ImageTk.PhotoImage(self.out)

            self.img2.config(image=self.out)
            self.img2.image = self.out


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("500x300")
    app = App(master=root)
    app.mainloop()
