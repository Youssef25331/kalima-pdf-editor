import customtkinter as ct
import math
from PIL import Image
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
            command=self.add_image,
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

        self.image_frame = ct.CTkFrame(self.pdf_window)
        self.image_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.background_panel = ct.CTkLabel(self.image_frame)

        # Bind the resize event to the image frame (not the whole window)
        self.image_frame.bind("<Configure>", self.resize_image)

        # Actions after initalization

        self.set_background()
        self.editing_items = []

        # Optional: Disable the main window while the new one is open
        self.pdf_window.grab_set()
        self.pdf_window.mainloop()

    def set_background(self, image_location="temp_pdf.png"):
        self.pdf_page_count = pdf_editor.convert_pdf_page(
            self.pdf, self.current_page_number
        )
        self.background_panel.destroy()
        self.base_pdf = Image.open(image_location)
        self.background_image = ct.CTkImage(
            dark_image=self.base_pdf,
            size=(400, 600),
        )

        self.background_panel = ct.CTkLabel(
            self.image_frame, image=self.background_image
        )
        self.background_panel.pack(fill="both", expand=True, padx=0, pady=0)
        self.resize_image()

    def page_move(self, right):
        if right and self.current_page_number < self.pdf_page_count:
            self.current_page_number += 1
            self.set_background()
        elif (not right) and self.current_page_number > 1:
            self.current_page_number -= 1
            self.set_background()

    def convert_pdf(self):
        image_translations = pdf_editor.percentage_converter(
            self.pdf,
            (self.image_pdf_width_percentage, self.image_pdf_height_percentage),
            (self.image_pdf_relative_x, self.image_pdf_relative_y),
        )
        pdf_editor.resize_and_save_image(
            self.loaded_logo,
            "temp.pdf",
            image_translations[0][0],
            image_translations[0][1],
            self.drag_panel._fg_color,
        )
        pdf_editor.merge_pdfs(
            self.pdf,
            "temp.pdf",
            "output.pdf",
            image_translations[0][1],
            image_translations[1],
            [1],
        )
        return

    def add_image(self):
        loaded_logo = ct.filedialog.askopenfilename(
            initialdir=Path.cwd(),
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp")],
        )
        new_image = Image.open(loaded_logo).convert("RGBA")  # Ensure RGBA mode
        overlay_image = ct.CTkImage(light_image=new_image, size=(120, 30))
        drag_panel = ct.CTkLabel(
            self.background_panel, image=overlay_image, text="", fg_color="#FFFFFF"
        )
        drag_panel.place(x=0, y=0)
        item = {
            "image": overlay_image,
            "panel": drag_panel,
            "width": 120,
            "height": 40,
            "x": 0,
            "y": 0,
            "is_resizing": False,
            "resize_edge": None,
            "start_x": 0,
            "start_y": 0,
            "relative_x": 0,
            "relative_y": 0,
            "width_percent": 0,
            "height_percent": 0,
        }
        drag_panel.bind("<B1-Motion>", lambda event: self.do_drag(event, item))
        self.calulate_relation(item)

        self.editing_items.append(item)

    # A function to calculate all the required relative numbers for the conversion.
    def calulate_relation(self, item):
        image_width = item["panel"].winfo_width()
        image_height = item["panel"].winfo_height()
        image_position_x = item["panel"].winfo_x()
        image_position_y = item["panel"].winfo_y()

        scaling = (
            self.background_panel.winfo_height() / self.background_image.cget("size")[1]
        )

        rendered_pdf_width = self.background_image.cget("size")[0] * scaling
        rendered_pdf_height = self.background_image.cget("size")[1] * scaling
        item["relative_x"] = (
            image_position_x
            - ((self.background_panel.winfo_width() - rendered_pdf_width) / 2)
        ) / rendered_pdf_width

        item["relative_y"] = image_position_y / self.background_panel.winfo_height()

        item["width_percent"] = image_width / rendered_pdf_width
        item["height_percent"] = image_height / rendered_pdf_height

    def start_drag(self, event):
        return

    def do_drag(self, event, item):
        image_position_x = item["panel"].winfo_x()
        image_position_y = item["panel"].winfo_y()

        item["panel"].configure(fg_color="#000000")
        # Calculate the new position
        new_x = image_position_x + event.x
        new_y = image_position_y + event.y

        # Optional: Constrain within image_frame bounds
        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()
        drag_width = item["panel"].winfo_width()
        drag_height = item["panel"].winfo_height()

        # Bind withing image_frame
        new_x = max(drag_width / 2, min(new_x, frame_width - drag_width / 2))
        new_y = max(drag_height / 2, min(new_y, frame_height - drag_height / 2))

        # Move the draggable image
        item["panel"].place(x=new_x, y=new_y, anchor="center")
        self.calulate_relation(item)

    def resize_image(self, event=None):
        orig_width, orig_height = self.base_pdf.size
        aspect_ratio = orig_width / orig_height
        new_width = self.image_frame.winfo_width()
        new_height = self.image_frame._current_height

        if new_width / new_height > aspect_ratio:
            new_width = int(new_height * aspect_ratio)

        # Update the CTkImage size dynamically
        self.background_image.configure(size=(new_width, new_height))

        # Optional: Force update the label to reflect the new image size
        self.background_panel.configure(image=self.background_image)


root = ct.CTk()
app = MyGui(root)
root.mainloop()
