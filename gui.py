import time
import customtkinter as ct
import math
from PIL import ImageTk, Image
from numpy import size
import pdf_editor
from pathlib import Path


class MyGui:
    def __init__(self, root):
        self.root = root
        self.root.geometry("400x500")
        self.root.minsize(400, 500)
        self.root.title("Kalima-PDF-Editor")

        self.pdf_button = ct.CTkButton(
            master=self.root,
            text="Select PDF (Or Drag Here)",
            height=40,
            command=self.browse_pdf,
        )
        self.pdf_button.place(relx=0.5, rely=0.5, anchor="center")

    def browse_pdf(self):
        self.pdf = ct.filedialog.askopenfilename(
            initialdir=Path.cwd(), filetypes=[("PDF Files", "*.pdf")]
        )
        if self.pdf:
            self.root.destroy()  # Close the original window
            self.open_pdf_window()

    def open_pdf_window(self):
        # Create a new window
        self.pdf_window = ct.CTk()
        self.pdf_window.geometry("700x600")
        self.pdf_window.title("PDF Editor")
        self.pdf_window.minsize(600, 600)

        # The side panel with differnt tools
        self.side_panel = ct.CTkFrame(self.pdf_window, width=200, height=600)
        self.side_panel.pack(side="left", fill="y", padx=10, pady=10)

        # setup page movment
        self.current_page_number = 1
        self.button1 = ct.CTkButton(
            self.side_panel, text="Page Right", command=lambda: self.page_move(True)
        )
        self.button2 = ct.CTkButton(
            self.side_panel, text="Page Left", command=lambda: self.page_move(False)
        )
        self.button1.pack(pady=10, padx=10)
        self.button2.pack(pady=10, padx=10)

        self.logo_button = ct.CTkButton(
            master=self.side_panel,
            text="Click TO add Image",
            height=40,
            command=self.add_logo,
        )
        self.logo_button.pack(anchor="center")

        self.submit_button = ct.CTkButton(
            master=self.side_panel,
            text="Convert",
            height=20,
            command=self.convert_pdf,
        )

        self.submit_button.pack(pady=40, anchor="s")

        # self.checkbox_var = ct.BooleanVar(
        #     value=False
        # )  # Variable to track checkbox state
        # self.checkbox = ct.CTkCheckBox(
        #     self.side_panel,
        #     text="Toggle Option",
        #     variable=self.checkbox_var,
        # )
        # self.checkbox.pack(pady=10, padx=10)

        self.base_pdf = Image.open("background.png")
        self.img = ct.CTkImage(
            dark_image=self.base_pdf,
            size=(400, 600),
        )

        self.image_frame = ct.CTkFrame(self.pdf_window)
        self.image_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.image_panel = ct.CTkLabel(self.image_frame)

        # Bind the resize event to the image frame (not the whole window)
        self.image_frame.bind("<Configure>", self.resize_image)

        # Functions after initalization
        self.set_image()

        # Optional: Disable the main window while the new one is open
        self.pdf_window.grab_set()
        self.pdf_window.mainloop()

    def set_image(self, image_location="temp_pdf.png"):
        self.pdf_page_count = pdf_editor.convert_pdf_page(
            self.pdf, self.current_page_number
        )
        self.image_panel.destroy()
        self.base_pdf = Image.open(image_location)
        self.img = ct.CTkImage(
            dark_image=self.base_pdf,
            size=(400, 600),
        )

        self.image_panel = ct.CTkLabel(self.image_frame, image=self.img, text="")
        self.image_panel.pack(fill="both", expand=True, padx=0, pady=0)
        self.resize_image()

    def page_move(self, right):
        if right and self.current_page_number < self.pdf_page_count:
            self.current_page_number += 1
            self.set_image()
        elif (not right) and self.current_page_number > 1:
            self.current_page_number -= 1
            self.set_image()

    def add_logo(self):
        self.loaded_logo = ct.filedialog.askopenfilename(
            initialdir=Path.cwd(),
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp")],
        )
        self.add_image()

    def convert_pdf(self):
        pdf_editor.merge_pdfs(
            "testing2.pdf",
            "temp.pdf",
            "output.pdf",
            30,
            (self.image_pdf_relative_x,0.05),
            [1],
            True,
        )
        return

    def add_image(self):
        new_image = Image.open(self.loaded_logo)
        self.overlay_image = ct.CTkImage(light_image=new_image, size=(120, 40))
        self.drag_panel = ct.CTkLabel(
            self.image_panel, image=self.overlay_image, text=""
        )
        self.drag_panel.place(x=0, y=0)
        self.drag_panel.bind("<Button-1>", self.start_drag)
        self.drag_panel.bind("<B1-Motion>", self.do_drag)

    def start_drag(self, event):
        # Store the initial mouse position relative to the draggable image
        return

    def do_drag(self, event):
        # Calculate the new position
        new_x = self.drag_panel.winfo_x() + event.x
        new_y = self.drag_panel.winfo_y() + event.y

        scaling = self.image_panel.winfo_height() / self.img.cget("size")[1]
        rendered_image_width = self.img.cget("size")[0] * scaling
        rendered_image_height = self.img.cget("size")[1] * scaling
        self.image_pdf_relative_x = (
            self.drag_panel.winfo_x()
            - ((self.image_panel.winfo_width() - rendered_image_width) / 2)
        ) / rendered_image_width

        self.image_pdf_relative_y = (
            self.drag_panel.winfo_y() / self.image_panel.winfo_height()
        )
        print(self.image_pdf_relative_x, self.image_pdf_relative_y)

        # Optional: Constrain within image_frame bounds
        frame_width = self.image_frame._current_width
        frame_height = self.image_frame._current_height
        drag_width = self.drag_panel._current_width
        drag_height = self.drag_panel._current_height

        # Bind withing image_frame
        new_x = max(0, min(new_x, frame_width - drag_width))  # Keep within x bounds
        new_y = max(0, min(new_y, frame_height - drag_height))

        # Move the draggable image
        self.drag_panel.place(x=new_x, y=new_y)

    def resize_image(self, event=None):
        orig_width, orig_height = self.base_pdf.size
        aspect_ratio = orig_width / orig_height
        new_width = self.image_frame.winfo_width()
        new_height = self.image_frame._current_height

        if new_width / new_height > aspect_ratio:
            new_width = int(new_height * aspect_ratio)

        # Update the CTkImage size dynamically
        self.img.configure(size=(new_width, new_height))

        # Optional: Force update the label to reflect the new image size
        self.image_panel.configure(image=self.img)


root = ct.CTk()
app = MyGui(root)
root.mainloop()
