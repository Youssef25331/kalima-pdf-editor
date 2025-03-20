import customtkinter as ct
import CTkColorPicker
from tkinter import font
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
        self.exclusion_list = []
        self.editing_items = []
        self.current_item = -1

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

        self.image_button = ct.CTkButton(
            master=self.side_panel,
            text="Click TO add Image",
            height=40,
            command=self.add_image,
        )
        self.image_button.pack(pady=10, anchor="center")

        self.text_button = ct.CTkButton(
            master=self.side_panel,
            text="Click TO add Text",
            height=40,
            command=self.add_text,
        )
        self.text_button.pack(pady=10, anchor="center")

        self.font_menu = ct.CTkOptionMenu(
            master=self.side_panel,
            values=list(font.families()),
            command=self.font_family_picker,
        )
        self.font_menu.pack(pady=5)
        self.font_slider = ct.CTkSlider(
            master=self.side_panel, from_=0, to=100, command=self.font_size_picker
        )
        self.font_slider.set(12)
        self.font_slider.pack(pady=10)

        self.opacity_slider = ct.CTkSlider(
            master=self.side_panel, from_=0, to=1, command=self.opacity_picker
        )
        self.opacity_slider.set(1)
        self.opacity_slider.pack(pady=10)

        self.bg_color_button = ct.CTkButton(
            master=self.side_panel,
            text="Pick Background Color",
            command=self.bg_color_picker,
        )
        self.bg_color_button.pack(pady=10)

        self.text_color_button = ct.CTkButton(
            master=self.side_panel,
            text="Pick Text Color",
            command=self.text_color_picker,
        )
        self.text_color_button.pack(pady=10)

        self.exclusion_entry = ct.CTkEntry(
            master=self.side_panel,
            placeholder_text="10,14,30....",
            width=150,
        )
        self.exclusion_entry.pack(pady=5)

        self.exlusion_submit = ct.CTkButton(
            master=self.side_panel, text="Submit", command=self.set_exclusion
        )
        self.exlusion_submit.pack(pady=5)

        self.submit_button = ct.CTkButton(
            master=self.side_panel,
            text="Convert",
            height=20,
            command=self.convert_pdf,
        )

        self.submit_button.pack(pady=40, anchor="s")

        self.image_frame = ct.CTkFrame(self.pdf_window)
        self.image_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.background_panel = ct.CTkLabel(self.image_frame)

        # Bind the resize event to the image frame (not the whole window)
        self.image_frame.bind("<Configure>", self.resize_image)

        # Actions after initalization

        self.set_background()

        # Optional: Disable the main window while the new one is open
        self.pdf_window.grab_set()
        self.pdf_window.mainloop()

    def set_exclusion(self):
        input_text = self.exclusion_entry.get()
        try:
            values = [int(x.strip()) for x in input_text.split(",") if x.strip()]
            if values:  # Ensure list isn’t empty
                self.exclusion_list = values
            else:
                print("No values entered!")
        except ValueError:
            print("Invalid input - use numbers like '1, 2, 3, 4'!")

    def bg_color_picker(self):
        pick_color = CTkColorPicker.AskColor()
        color = pick_color.get()
        if color:
            item = self.editing_items[self.current_item]
            self.bg_color_button.configure(fg_color=color)
            item["panel"].configure(fg_color=color)
            item["bg_color"] = color

    def opacity_picker(self, value):
        item = self.editing_items[self.current_item]
        item["opacity"] = round(value, 1)

    def font_family_picker(self, font):
        item = self.editing_items[self.current_item]
        if "text" in item:
            item["panel"].configure(font=(font, 12))
            item["font_family"] = font

    def font_size_picker(self, value):
        item = self.editing_items[self.current_item]
        if "text" in item:
            item["panel"].configure(font=(item["font_family"], value))
            item["font_size"] = value

    def text_color_picker(self):
        pick_color = CTkColorPicker.AskColor()
        color = pick_color.get()
        item = self.editing_items[self.current_item]
        if color and "text" in item:
            self.bg_color_button.configure(fg_color=color)
            item["panel"].configure(text_color=color)
            item["text_color"] = color

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
        item = self.editing_items[self.current_item]
        image_translations = pdf_editor.percentage_converter(
            self.pdf,
            (item["width_percent"], item["height_percent"]),
            (item["relative_x"], item["relative_y"]),
        )
        pdf_editor.resize_and_save_image(
            item["image_location"],
            "temp.pdf",
            item["opacity"],
            image_translations[0][0],
            image_translations[0][1],
            item["panel"]._fg_color,
        )
        pdf_editor.merge_pdfs(
            self.pdf,
            "temp.pdf",
            "output.pdf",
            image_translations[0][1],
            image_translations[1],
            self.exclusion_list,
        )
        return

    def add_image(self):
        loaded_logo = ct.filedialog.askopenfilename(
            initialdir=Path.cwd(),
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp")],
        )
        new_image = Image.open(loaded_logo).convert("RGBA")  # Ensure RGBA mode
        size = (120, int(120 * new_image.size[1] / new_image.size[0]))
        overlay_image = ct.CTkImage(
            light_image=new_image,
            size=size,
        )
        drag_panel = ct.CTkLabel(
            self.background_panel, image=overlay_image, text="", fg_color="#FFFFFF"
        )
        drag_panel.place(x=0, y=0)
        item = {
            "index": len(self.editing_items),
            "image_location": loaded_logo,
            "image": overlay_image,
            "panel": drag_panel,
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
            "bg_color": "#FFFFFF",
            "text_color": "000000",
            "opacity": 1,
        }
        print(item["index"])

        drag_panel.bind("<Button-1>", lambda event: self.start_action(event, item))
        drag_panel.bind("<B1-Motion>", lambda event: self.do_action(event, item))
        drag_panel.bind(
            "<ButtonRelease-1>", lambda event: self.stop_action(event, item)
        )
        self.calulate_relation(item)

        self.editing_items.append(item)

    def add_text(self):
        drag_panel = ct.CTkLabel(
            self.background_panel,
            text="This is a text",
            text_color="#000000",
            fg_color="#FFFFFF",
            width=120,
            height=120,
            anchor="center",
        )
        drag_panel.place(anchor="center")
        item = {
            "index": len(self.editing_items),
            "type": "text",
            "text": "this is a text",
            "panel": drag_panel,
            "font_family": "ariel",
            "font_size": "12",
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
            "bg_color": "#FFFFFF",
            "opacity": 1,
        }
        drag_panel.bind("<Button-1>", lambda event: self.start_action(event, item))
        drag_panel.bind("<B1-Motion>", lambda event: self.do_action(event, item))
        drag_panel.bind(
            "<ButtonRelease-1>", lambda event: self.stop_action(event, item)
        )
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

        self.rendered_background_width = self.background_image.cget("size")[0] * scaling
        self.rendered_pdf_height = self.background_image.cget("size")[1] * scaling
        item["relative_x"] = (
            image_position_x
            - (
                (self.background_panel.winfo_width() - self.rendered_background_width)
                / 2
            )
        ) / self.rendered_background_width

        item["relative_y"] = image_position_y / self.background_panel.winfo_height()

        item["width_percent"] = image_width / self.rendered_background_width
        item["height_percent"] = image_height / self.rendered_pdf_height

    def start_action(self, event, item):
        self.current_item = item["index"]
        x, y = event.x, event.y
        width = item["panel"].winfo_width()
        height = item["panel"].winfo_height()
        border = 10  # How many pixels near an edge to consider resizing.

        # Determine if click is near an edge based on mouse relative position.
        if x >= width - border and y >= height - border:
            item["is_resizing"] = True
            item["resize_edge"] = "bottom-right"  # Resize from bottom-right corner
        elif x >= width - border:
            item["is_resizing"] = True
            item["resize_edge"] = "right"
        elif y >= height - border:
            item["is_resizing"] = True
            item["resize_edge"] = "bottom"
        else:
            item["is_resizing"] = False

    def do_action(self, event, item):
        if item["is_resizing"]:
            self.do_resize(event, item)
        else:
            self.do_drag(event, item)

    def do_resize(self, event, item):
        new_width = item["panel"].winfo_width()
        new_height = item["panel"].winfo_height()
        if item["resize_edge"] == "bottom":
            dy = event.y - item["panel"].winfo_height()
            new_width = item["panel"].winfo_width()
            new_height = item["panel"].winfo_height() + dy
            self.image_frame.configure(cursor="sb_down_arrow")
        elif item["resize_edge"] == "right":
            dx = event.x - item["panel"].winfo_width()
            new_width = item["panel"].winfo_width() + dx
            self.image_frame.configure(cursor="sb_right_arrow")
        elif item["resize_edge"] == "bottom-right":
            dx = event.x - item["panel"].winfo_width()
            new_width = item["panel"].winfo_width() + dx
            new_height = item["panel"].winfo_height() + dx
            self.image_frame.configure(cursor="sizing")
        if "image" in item:
            item["image"].configure(size=(new_width, new_height))
        else:
            item["panel"].configure(width=new_width, height=new_height)

    def stop_action(self, event, item):
        self.calulate_relation(item)
        self.image_frame.configure(cursor="")

    def do_drag(self, event, item):
        image_position_x = item["panel"].winfo_x()
        image_position_y = item["panel"].winfo_y()

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
