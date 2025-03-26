import customtkinter as ct
import CTkColorPicker
from PIL import Image
import pdf_editor
from pathlib import Path

# Fix scalling issues on some devices.
ct.deactivate_automatic_dpi_awareness()
ct.set_appearance_mode("dark")


class MyGui:
    def __init__(self, root):
        self.root = root
        self.root.geometry("400x500")
        self.root.minsize(400, 500)
        self.root.title("Kalima-PDF-Editor")
        # self.browse_pdf()

        self.root.configure(fg_color="#0e0e0f")
        self.pdf_button = ct.CTkButton(
            master=self.root,
            text="Select PDF \n(Or Drag Here)",
            height=50,
            command=self.browse_pdf,
            fg_color="#111f28",
            hover_color="#213c4e",
            text_color="#e3cdb3",
            font=("Figtree", 12, "bold"),
        )
        self.pdf_button.place(relx=0.5, rely=0.5, anchor="center")

    def browse_pdf(self):
        self.pdf = ct.filedialog.askopenfilename(
            initialdir=Path.cwd(), filetypes=[("PDF Files", "*.pdf")]
        )
        # self.pdf = "../../kalima-pdf-editor/Testing/Testing_PDF.pdf"
        if self.pdf:
            self.root.destroy()  # Close the original window
            self.open_pdf_window()

    def open_pdf_window(self):
        # Create a new window
        self.pdf_window = ct.CTk()
        self.pdf_window.geometry("700x600")
        self.pdf_window.title("PDF Editor")
        self.pdf_window.minsize(600, 200)
        self.exclusion_list = []
        self.editing_items = []
        self.current_item = -1
        self.pdf_window.bind("<Delete>", self.delete_item)

        # UI
        self.main = "#111f28"
        self.main_hover = "#213c4e"
        self.success = "#1b6f07"
        self.success_hover = "#2eb00e"
        self.dark = "#0e0e0f"
        self.second_dark = "#121214"
        self.second_dark_hover = "#17171a"
        self.text_color = "#e3cdb3"
        self.global_font_family = "Figtree"
        self.global_font_size = 12
        self.global_font_style = "bold"

        self.pdf_window.configure(fg_color=self.dark)
        # The side panel with differnt tools
        self.side_panel = ct.CTkFrame(self.pdf_window, corner_radius=0, width=200)
        self.side_panel.pack(side="left", fill="both", padx=0, pady=0)

        self.top_frame = ct.CTkFrame(
            self.side_panel, corner_radius=0, fg_color=self.second_dark
        )
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.bottom_frame = ct.CTkFrame(
            self.side_panel, corner_radius=0, fg_color=self.second_dark
        )
        self.bottom_frame.pack(
            side="bottom",
            fill="x",
        )

        self.bg_color_button = ct.CTkButton(
            master=self.top_frame,
            text="Back Color",
            hover_color=self.main_hover,
            command=self.bg_color_picker,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            width=100,
            height=30,
            text_color=self.text_color,
        )
        self.opacity_slider = ct.CTkSlider(
            button_corner_radius=4,
            button_color=self.main_hover,
            master=self.top_frame,
            from_=0,
            to=1,
            command=self.opacity_picker,
            width=100,
        )
        self.opacity_label = ct.CTkLabel(
            master=self.top_frame,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            text_color=self.text_color,
            width=110,
        )
        self.setup_text_buttons()
        self.setup_images_buttons()

        # setup icons
        self.left_arrow = ct.CTkImage(
            dark_image=Image.open("./assets/white-left-arrow.png")
        )
        self.right_arrow = ct.CTkImage(
            dark_image=Image.open("./assets/white-right-arrow.png")
        )

        # setup page movment
        self.current_page_number = 1

        self.text_button = ct.CTkButton(
            self.top_frame,
            text="Add Text",
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            height=40,
            fg_color=self.main,
            hover_color=self.main_hover,
            command=self.add_text,
            text_color=self.text_color,
            width=80,
        )
        self.image_button = ct.CTkButton(
            self.top_frame,
            text="Add Image",
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            height=40,
            fg_color=self.main,
            hover_color=self.main_hover,
            command=self.add_image,
            text_color=self.text_color,
            width=80,
        )
        self.exclusion_entry = ct.CTkEntry(
            self.bottom_frame,
            placeholder_text="Exclude pages eg:10,14,30....",
            fg_color=self.second_dark_hover,
            width=170,
        )
        self.exclusion_entry.bind("<Return>", self.set_exclusion)
        self.exclusion_invert = ct.CTkCheckBox(
            self.bottom_frame,
            border_width=2,
            border_color="#565b5e",
            fg_color=self.main,
            checkmark_color=self.text_color,
            text="",
            width=0,
            hover_color=self.second_dark_hover,
        )
        self.page_entry = ct.CTkEntry(
            self.bottom_frame,
            placeholder_text="",
            width=28,
            fg_color=self.second_dark_hover,
        )
        self.page_entry.bind("<Return>", self.set_page)

        self.left_page_button = ct.CTkButton(
            self.bottom_frame,
            text="",
            image=self.left_arrow,
            height=30,
            command=lambda: self.page_move(False),
            width=90,
            text_color=self.text_color,
            fg_color=self.main,
            hover_color=self.main_hover,
        )
        self.right_page_button = ct.CTkButton(
            self.bottom_frame,
            text="",
            height=30,
            image=self.right_arrow,
            command=lambda: self.page_move(True),
            width=90,
            text_color=self.text_color,
            fg_color=self.main,
            hover_color=self.main_hover,
        )
        self.convert_button = ct.CTkButton(
            self.bottom_frame,
            text="Convert",
            fg_color=self.success,
            height=50,
            text_color=self.text_color,
            hover_color=self.success_hover,
            font=(self.global_font_family, 16),
            command=self.convert_pdf,
        )

        # Configure rows.

        # Configure columns to be equal width.
        self.top_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="column")
        self.bottom_frame.columnconfigure(
            (1, 2),
            weight=0,
        )

        # Grid layout.
        self.text_button.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=10
        )
        self.image_button.grid(
            row=0, column=2, columnspan=2, sticky="ew", padx=5, pady=10
        )
        self.exclusion_entry.grid(
            row=0, column=0, padx=5, pady=5, columnspan=3, sticky="w"
        )
        self.exclusion_invert.grid(row=0, column=2, padx=8, sticky="e")
        self.left_page_button.grid(row=1, padx=5, column=0)
        self.page_entry.grid(row=1, column=1)
        self.right_page_button.grid(row=1, padx=5, column=2, sticky="ew")
        self.convert_button.grid(row=2, padx=5, pady=10, columnspan=3, sticky="ew")
        self.image_frame = ct.CTkFrame(self.pdf_window, fg_color=self.second_dark)
        self.image_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.background_panel = ct.CTkLabel(self.image_frame, text="")

        # Bind the resize event to the image frame (not the whole window).
        self.image_frame.bind("<Configure>", self.resize_image)

        self.resize_id = None
        self.pdf_window.bind("<Configure>", self.debouce_update)

        # Actions after initalization

        self.set_background()

        # Optional: Disable the main window while the new one is open
        self.pdf_window.grab_set()
        self.pdf_window.mainloop()

    def setup_images_buttons(self):
        return

    def setup_text_buttons(self):
        self.background_opacity_slider = ct.CTkSlider(
            master=self.top_frame,
            button_corner_radius=4,
            button_color=self.main_hover,
            from_=0,
            to=1,
            command=self.background_opacity_picker,
            width=100,
        )
        self.background_opacity_label = ct.CTkLabel(
            master=self.top_frame,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            text_color=self.text_color,
            width=110,
        )
        self.font_menu = ct.CTkOptionMenu(
            master=self.top_frame,
            # values=list(font.families()),
            values=self.load_fonts(),
            command=self.font_family_picker,
            fg_color=self.main,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            button_color=self.main,
            button_hover_color=self.main_hover,
            dropdown_fg_color=self.second_dark,
            dropdown_text_color=self.text_color,
            dropdown_hover_color=self.second_dark_hover,
            width=215,
            height=36,
            text_color=self.text_color,
        )

        self.font_size_slider = ct.CTkSlider(
            master=self.top_frame,
            button_corner_radius=4,
            button_color=self.main_hover,
            from_=1,
            to=100,
            command=self.font_size_picker,
            width=215,
        )
        self.font_size_label = ct.CTkLabel(
            master=self.top_frame,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            text_color=self.text_color,
            width=110,
        )

        self.text_color_button = ct.CTkButton(
            master=self.top_frame,
            text="Text Color",
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            text_color=self.text_color,
            hover_color=self.main_hover,
            command=self.text_color_picker,
            width=100,
            height=30,
        )

        self.text_entry = ct.CTkEntry(
            master=self.top_frame,
            placeholder_text="Input text",
            width=215,
            height=36,
            fg_color=self.second_dark_hover,
        )

        self.text_submit = ct.CTkButton(
            master=self.top_frame, text="Submit", command=self.set_text
        )

    def update_side_panel(self):
        if self.current_item != -1:
            item = self.editing_items[self.current_item]
            self.bg_color_button.configure(
                fg_color=item["bg_color"],
            )
            self.opacity_slider.set(item["opacity"])
            if "text" in item:
                self.bg_color_button.configure(
                    width=100,
                    height=30,
                )
                self.bg_color_button.grid(
                    row=1,
                    column=1,
                    columnspan=2,
                    pady=10,
                )
                self.opacity_label.grid(row=2, column=0, columnspan=2, padx=5)
                self.opacity_label.configure(text="Opacity: " + str(item["opacity"]))
                self.background_opacity_label.grid(
                    row=2, column=2, columnspan=2, pady=0
                )
                self.background_opacity_label.configure(
                    text="BG Opacity: " + str(item["opacity"])
                )
                self.opacity_slider.configure(width=100)
                self.opacity_slider.grid(row=3, column=0, columnspan=2, pady=0)
                self.background_opacity_slider.grid(
                    row=3,
                    column=2,
                    columnspan=2,
                )

                self.bg_color_button.grid(
                    row=4, column=0, columnspan=2, pady=10, padx=5
                )
                self.text_color_button.grid(
                    row=4, column=2, columnspan=2, pady=10, padx=5
                )
                self.text_color_button.configure(fg_color=item["text_color"])
                self.background_opacity_slider.set(item["bg_opacity"])
                self.font_size_label.grid(row=5, column=1, columnspan=2, padx=5)
                self.font_size_label.configure(
                    text="Font Size: " + str(item["font_size"])
                )
                self.font_size_slider.set(item["font_size"])
                self.font_size_slider.grid(row=6, column=1, columnspan=2, padx=5)

                self.text_entry.grid(row=7, padx=5, pady=15, column=0, columnspan=4)
                self.font_menu.grid(row=8, column=0, padx=5, pady=0, columnspan=4)
            else:
                self.bg_color_button.configure(width=215, height=36)
                self.bg_color_button.grid(
                    row=1, column=0, columnspan=4, pady=10, padx=5
                )
                self.background_opacity_slider.grid_forget()
                self.opacity_label.grid(row=2, column=1, columnspan=2)
                self.opacity_slider.configure(width=215)
                self.opacity_slider.grid(
                    row=3,
                    column=1,
                    columnspan=2,
                )
                self.background_opacity_label.grid_forget()
                self.background_opacity_slider.grid_forget()
                self.font_size_slider.grid_forget()
                self.font_size_label.grid_forget()
                self.font_menu.grid_forget()
                self.text_color_button.grid_forget()
                self.text_entry.grid_forget()
                self.text_submit.grid_forget()
        else:
            self.background_opacity_slider.grid_forget()
            self.opacity_slider.grid_forget()
            self.font_menu.grid_forget()
            self.font_size_slider.grid_forget()
            self.text_color_button.grid_forget()
            self.text_entry.grid_forget()
            self.text_submit.grid_forget()
            self.bg_color_button.grid_forget()

    def delete_item(self, event):
        if self.current_item >= 0:
            item = self.editing_items[self.current_item]
            item["panel"].destroy()
            self.editing_items[self.current_item] = {
                "index": item["index"],
                "deleted": True,
            }
        self.current_item = -1
        self.update_side_panel()

    def set_exclusion(self, event):
        input_text = self.exclusion_entry.get()
        try:
            values = [int(x.strip()) for x in input_text.split(",") if x.strip()]
            if values:  # Ensure list isn’t empty
                self.exclusion_list = values
            else:
                print("No values entered!")
        except ValueError:
            print("Invalid input - use numbers like '1, 2, 3, 4'!")

    def set_page(self, event):
        input_text = self.page_entry.get()
        try:
            value = int(input_text)
            if 0 < value <= self.pdf_page_count:
                self.current_page_number = value
                self.set_background()
            else:
                print("No values entered!")
        except ValueError:
            print("Invalid input - use numbers like '10'!")

    def load_fonts(self):
        active_fonts = []
        fonts = pdf_editor.load_project_fonts()
        for font in fonts:
            active_fonts.append(font[0])
            ct.FontManager.load_font(str(font[2]))
        return active_fonts

    def set_text(self):
        input_text = self.text_entry.get()
        item = self.editing_items[self.current_item]
        if "text" in item:
            item["text"] = input_text
            item["panel"].configure(text=input_text)

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
        self.opacity_label.configure(text="Opacity: " + str(item["opacity"]))

    def background_opacity_picker(self, value):
        item = self.editing_items[self.current_item]
        item["bg_opacity"] = round(value, 1)
        self.background_opacity_label.configure(
            text="BG Opacity: " + str(item["bg_opacity"])
        )

    def font_family_picker(self, font):
        item = self.editing_items[self.current_item]
        if "text" in item:
            item["panel"].configure(font=(font, item["font_size"]))
            item["font_family"] = font

    def font_size_picker(self, value):
        item = self.editing_items[self.current_item]
        if "text" in item:
            item["panel"].configure(font=(item["font_family"], value))
            item["font_size"] = round(value)
            self.font_size_label.configure(text="Font Size: " + str(item["font_size"]))

    def text_color_picker(self):
        pick_color = CTkColorPicker.AskColor()
        color = pick_color.get()
        item = self.editing_items[self.current_item]
        if color and "text" in item:
            self.text_color_button.configure(fg_color=color)
            item["panel"].configure(text_color=color)
            item["text_color"] = color

    def set_background(self, image_location="Temp/temp_background.png"):
        self.pdf_page_count = pdf_editor.convert_pdf_page(
            self.pdf, self.current_page_number, image_location
        )
        self.base_pdf = Image.open(image_location)
        self.background_image = ct.CTkImage(
            dark_image=self.base_pdf,
            size=(400, 600),
        )
        self.background_panel.configure(image=self.background_image)

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
        save_path = ct.filedialog.asksaveasfilename(
            initialdir=Path.cwd(),
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile="output.pdf",
        )
        pdf_editor.setup_loop_file(self.pdf)
        for item in self.editing_items:
            is_final = False
            if item["index"] == len(self.editing_items) - 1:
                is_final = True
            if "deleted" not in item:
                if "image" in item:
                    item_translations = pdf_editor.percentage_converter(
                        self.pdf,
                        (item["width_percent"], item["height_percent"]),
                        (item["relative_x"], item["relative_y"]),
                    )
                    pdf_editor.resize_and_save_image(
                        item["image_location"],
                        item["opacity"],
                        item_translations[0][0],
                        item_translations[0][1],
                        item["panel"]._fg_color,
                    )
                else:
                    item_translations = pdf_editor.percentage_converter(
                        self.pdf,
                        (item["width_percent"], item["height_percent"]),
                        (item["relative_x"], item["relative_y"]),
                        item["relative_font_size"],
                    )
                    pdf_editor.create_text_pdf(
                        item["text"],
                        (item_translations[0][0], item_translations[0][1]),
                        item["opacity"],
                        bg_color=item["bg_color"],
                        text_color=item["text_color"],
                        font_family=item["font_family"],
                        font_size=item_translations[2],
                    )
                pdf_editor.merge_pdfs(
                    save_path,
                    item_translations[0][1],
                    is_final,
                    item_translations[1],
                    self.exclusion_list,
                    invert=bool(self.exclusion_invert.get()),
                )

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
            "opacity": 1,
        }
        print(item["index"])

        drag_panel.bind("<Button-1>", lambda event: self.start_action(event, item))
        drag_panel.bind("<B1-Motion>", lambda event: self.do_action(event, item))
        drag_panel.bind(
            "<ButtonRelease-1>", lambda event: self.stop_action(event, item)
        )
        self.calulate_relative_dimensions(item)
        self.editing_items.append(item)
        self.current_item = item["index"]
        self.update_side_panel()

    def add_text(self):
        drag_panel = ct.CTkLabel(
            self.background_panel,
            text="Your text",
            text_color="#FFFFFF",
            fg_color="#000000",
            width=120,
            height=120,
            anchor="center",
            font=("Arial", 12),
        )
        drag_panel.place(anchor="center")
        item = {
            "index": len(self.editing_items),
            "type": "text",
            "text": "Your text",
            "panel": drag_panel,
            "font_family": "Arial",
            "font_size": 12,
            "relative_font_size": 12,
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
            "bg_color": "#000000",
            "text_color": "#FFFFFF",
            "opacity": 1,
            "bg_opacity": 1,
        }
        drag_panel.bind("<Button-1>", lambda event: self.start_action(event, item))
        drag_panel.bind("<B1-Motion>", lambda event: self.do_action(event, item))
        drag_panel.bind(
            "<ButtonRelease-1>", lambda event: self.stop_action(event, item)
        )
        self.calulate_relative_dimensions(item)

        self.editing_items.append(item)
        self.current_item = item["index"]
        self.update_side_panel()

    # A function to calculate all the required relative numbers for the conversion.
    def calulate_relative_dimensions(self, item):
        item_width = item["panel"].winfo_width()
        item_height = item["panel"].winfo_height()
        item_position_x = item["panel"].winfo_x()
        item_position_y = item["panel"].winfo_y()

        scaling = (
            self.background_panel.winfo_height() / self.background_image.cget("size")[1]
        )

        self.rendered_background_width = self.background_image.cget("size")[0] * scaling
        self.rendered_pdf_height = self.background_image.cget("size")[1] * scaling
        item["relative_x"] = (
            item_position_x
            - (
                (self.background_panel.winfo_width() - self.rendered_background_width)
                / 2
            )
        ) / self.rendered_background_width

        item["relative_y"] = item_position_y / self.background_panel.winfo_height()

        item["width_percent"] = item_width / self.rendered_background_width
        item["height_percent"] = item_height / self.rendered_pdf_height
        if "text" in item:
            font_height_px = item["font_size"]
            font_percentage = font_height_px / self.rendered_pdf_height
            item["relative_font_size"] = font_percentage

    def start_action(self, event, item):
        self.current_item = item["index"]
        self.update_side_panel()
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
        self.calulate_relative_dimensions(item)
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
        new_width = self.image_frame._current_width
        new_height = self.image_frame._current_height
        side_panel = self.side_panel.winfo_width() - 40

        if new_width / new_height > aspect_ratio:
            new_width = int(new_height * aspect_ratio)

        self.pdf_window.minsize(int(side_panel + new_height), 600)

        # Update the CTkImage size dynamically
        self.background_image.configure(size=(new_width, new_height))

        # Optional: Force update the label to reflect the new image size
        self.background_panel.configure(image=self.background_image)

    def debouce_update(self, event):
        if self.resize_id is not None:
            self.pdf_window.after_cancel(self.resize_id)
        self.resize_id = self.pdf_window.after(400, self.update_all_items)

    def update_all_items(self):
        if len(self.editing_items):
            for item in self.editing_items:
                if "deleted" not in item:
                    self.calulate_relative_dimensions(item)


root = ct.CTk()
app = MyGui(root)
root.mainloop()
