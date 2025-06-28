import customtkinter as ct
from customtkinter.windows.ctk_tk import tkinter
import CTkColorPicker
from PIL import Image
import pdf_editor
from pathlib import Path
import pywinstyles

# Fix scalling issues on some devices.
ct.deactivate_automatic_dpi_awareness()
ct.set_appearance_mode("dark")


class MyGui:
    def __init__(self, root: ct.CTk):
        self.root = root
        self.root.geometry("400x500")
        self.root.minsize(400, 500)
        self.root.title("Kalima-PDF-Editor")
        self.root.iconbitmap(pdf_editor.get_base_path() / "assets" / "logo.ico")
        self.browse_pdf()
        self.root.configure(fg_color="#0e0e0f")
        self.pdf_button = ct.CTkButton(
            master=self.root,
            text="Select PDF",
            height=50,
            command=self.browse_pdf,
            fg_color="#111f28",
            hover_color="#213c4e",
            text_color="#e3cdb3",
            font=("Figtree", 12, "bold"),
        )
        self.pdf_button.place(relx=0.5, rely=0.5, anchor="center")

    def browse_pdf(self):
        # self.pdf = ct.filedialog.askopenfilename(
        #     initialdir=Path.cwd(), filetypes=[("PDF Files", "*.pdf")]
        # )
        # if self.pdf:
        #     self.root.destroy()  # Close the original window
        #     self.open_pdf_window()
        self.pdf = "../../kalima-pdf-editor/Testing/Testing_PDF.pdf"
        self.root.destroy()
        self.open_pdf_window()

    def open_pdf_window(self):
        # Create a new window
        self.pdf_window = ct.CTk()

        # To show popup confirming exit
        self.pdf_window.protocol(
            "WM_DELETE_WINDOW", lambda: self.confirm_exit(self.pdf_window)
        )

        ## Menu bar for special options
        self.menubar = tkinter.Menu(self.pdf_window)
        self.pdf_window.config(menu=self.menubar)

        self.file_menu = tkinter.Menu(
            self.menubar,
        )
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.pdf_window.geometry("700x600")
        self.pdf_window.title("PDF Editor")
        self.pdf_window.minsize(600, 200)
        self.exclusion_list = []
        self.is_include = False
        self.editing_items = []
        self.current_item = -1
        self.pdf_window.bind("<Delete>", self.delete_item)
        self.mouse_frame_position_x = 0
        self.mouse_frame_position_y = 0
        self.encryption_key = ""

        self.pdf_window.iconbitmap(pdf_editor.get_base_path() / "assets" / "logo.ico")

        # UI
        self.main = "#111f28"
        self.main_hover = "#213c4e"
        self.success = "#1b6f07"
        self.success_hover = "#2eb00e"
        self.fail = "#B00B05"
        self.fail_hover = "#D60D06"
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
            text="Opacity: ",
            text_color=self.text_color,
            width=110,
        )
        self.opacity_entry = ct.CTkEntry(
            self.top_frame,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            text_color=self.text_color,
            placeholder_text="",
            width=30,
            border_width=0,
            fg_color=self.second_dark,
        )
        self.opacity_entry.bind("<Return>", self.set_opacity)
        self.setup_text_buttons()
        self.setup_images_buttons()

        # setup icons
        self.left_arrow = ct.CTkImage(
            dark_image=Image.open(
                pdf_editor.get_base_path() / "assets" / "white-left-arrow.png"
            )
        )
        self.right_arrow = ct.CTkImage(
            dark_image=Image.open(
                pdf_editor.get_base_path() / "assets" / "white-right-arrow.png"
            )
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
            border_width=1,
            width=170,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            text_color=self.text_color,
        )
        self.exclusion_entry.bind("<Return>", self.set_exclusion)
        self.exclusion_invert = ct.CTkCheckBox(
            self.bottom_frame,
            border_color="#565b5e",
            fg_color=self.main,
            border_width=1,
            checkmark_color=self.text_color,
            text="",
            width=0,
            hover_color=self.second_dark_hover,
        )
        self.page_entry = ct.CTkEntry(
            self.bottom_frame,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            text_color=self.text_color,
            border_width=1,
            placeholder_text="",
            width=28,
            fg_color=self.second_dark_hover,
        )
        self.page_entry.bind("<Return>", self.set_page)

        self.left_page_button = ct.CTkButton(
            self.bottom_frame,
            text="",
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            text_color=self.text_color,
            image=self.left_arrow,
            height=30,
            command=lambda: self.page_move(False),
            width=90,
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
            row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=16
        )
        self.image_button.grid(
            row=0, column=2, columnspan=2, sticky="ew", padx=5, pady=16
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
        self.pdf_window.bind("<Motion>", self.set_mouse_pos)

        # Bind the resize event to the image frame (not the whole window).
        self.image_frame.bind("<Configure>", self.resize_image)

        self.resize_id = None
        self.pdf_window.bind("<Configure>", self.debouce_update)

        # Actions after initalization

        self.set_background()

        # Optional: Disable the main window while the new one is open
        self.pdf_window.mainloop()

    def setup_images_buttons(self):
        print("Close button clicked, but exit is disabled.")

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
        self.background_opacity_entry = ct.CTkEntry(
            self.top_frame,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            border_width=0,
            fg_color=self.second_dark,
            text_color=self.text_color,
            placeholder_text="",
            width=30,
        )
        self.background_opacity_entry.bind("<Return>", self.set_background_opacity)
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
            width=210,
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
            width=210,
            height=36,
            fg_color=self.second_dark_hover,
        )
        self.text_entry.bind("<Return>", self.set_text)

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
                self.opacity_label.grid(
                    row=2,
                    column=0,
                    columnspan=2,
                )
                self.opacity_label.configure(text="Opacity: ")

                self.background_opacity_label.grid(
                    row=2,
                    column=2,
                    columnspan=2,
                )
                self.opacity_label.grid(
                    row=2,
                    column=0,
                    columnspan=2,
                )
                self.opacity_entry.grid(
                    row=2, column=1, columnspan=2, padx=78, sticky="w"
                )
                self.opacity_entry.delete(0, "end")
                self.opacity_entry.insert(0, str(item["opacity"]))
                self.opacity_entry.lift()
                self.background_opacity_entry.grid(
                    row=2, column=2, columnspan=2, sticky="e"
                )
                self.background_opacity_entry.lift()
                self.background_opacity_label.configure(text="BG Opacity:   ")
                self.background_opacity_entry.delete(0, "end")
                self.background_opacity_entry.insert(0, str(item["bg_opacity"]))
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
                self.opacity_slider.grid_forget()
                self.opacity_slider.grid_forget()
                self.opacity_entry.grid(
                    row=2, column=2, columnspan=2, sticky="w", padx=24
                )
                self.opacity_entry.delete(0, "end")
                self.opacity_entry.insert(0, str(item["opacity"]))
                self.bg_color_button.configure(width=215, height=36)
                self.bg_color_button.grid(
                    row=1, column=0, columnspan=4, pady=10, padx=5
                )
                self.background_opacity_entry.grid_forget()
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
        else:
            self.opacity_label.grid_forget()
            self.font_size_label.grid_forget()
            self.opacity_entry.grid_forget()
            self.background_opacity_entry.grid_forget()
            self.background_opacity_label.grid_forget()
            self.background_opacity_slider.grid_forget()
            self.opacity_slider.grid_forget()
            self.font_menu.grid_forget()
            self.font_size_slider.grid_forget()
            self.text_color_button.grid_forget()
            self.text_entry.grid_forget()
            self.bg_color_button.grid_forget()

    def delete_item(self, event):
        if self.current_item >= 0:
            item = self.editing_items[self.current_item]
            item["panel"].destroy()
            if "text" in item:
                item["panel_clone"].destroy()
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
            if values and not self.exclusion_invert.get():  # Ensure list isn’t empty
                self.exclusion_list = values
                self.is_include = False
                self.show_popup_window(
                    self.pdf_window,
                    "Success",
                    "Success!",
                    self.success,
                    "Pages '" + input_text + "' Will not be edited.",
                    self.text_color,
                )
            elif values and self.exclusion_invert.get():
                self.exclusion_list = values
                self.is_include = True
                self.show_popup_window(
                    self.pdf_window,
                    "Success",
                    "Success!",
                    self.success,
                    "Only pages '" + input_text + "' Will be edited.",
                    self.text_color,
                )

            else:
                self.show_popup_window(
                    self.pdf_window,
                    "Error",
                    "Error!",
                    self.fail,
                    "No Values where entered.",
                    self.text_color,
                )
        except ValueError:
            self.show_popup_window(
                self.pdf_window,
                "Error",
                "Error!",
                self.fail,
                "Invalid input - use numbers like '1, 2, 3, 4'!",
                self.text_color,
            )

    def set_page(self, event):
        input_text = self.page_entry.get()
        try:
            value = int(input_text)
            if 0 < value <= self.pdf_page_count:
                self.current_page_number = value
                self.set_background()
            else:
                self.show_popup_window(
                    self.pdf_window,
                    "Error",
                    "Error!",
                    self.fail,
                    "No Values where entered.",
                    self.text_color,
                )
                print("No values entered!")
        except ValueError:
            self.show_popup_window(
                self.pdf_window,
                "Error",
                "Error!",
                self.fail,
                "Invalid input - use numbers like '10'!",
                self.text_color,
            )
            print("Invalid input - use numbers like '10'!")

    def load_fonts(self):
        active_fonts = []
        fonts = pdf_editor.load_project_fonts()
        for font in fonts:
            active_fonts.append(font[0])
            ct.FontManager.load_font(str(font[2]))
        return active_fonts

    def set_text(self, event):
        input_text = self.text_entry.get()
        item = self.editing_items[self.current_item]
        if "text" in item:
            item["text"] = input_text
            item["panel"].configure(text=input_text)
            item["panel_clone"].configure(text=input_text)

    def bg_color_picker(self):
        pick_color = CTkColorPicker.AskColor(
            bg_color=self.dark,
            fg_color=self.second_dark,
            button_color=self.main,
            button_hover_color=self.main_hover,
        )
        pick_color.after(
            200,
            lambda: pick_color.iconbitmap(
                pdf_editor.get_base_path() / "assets" / "logo.ico"
            ),
        )
        color = pick_color.get()
        if color:
            item = self.editing_items[self.current_item]
            self.bg_color_button.configure(fg_color=color)
            item["panel"].configure(fg_color=color)
            item["panel_clone"].configure(fg_color=color)
            pywinstyles.set_opacity(item["panel_clone"], color=color)
            item["bg_color"] = color

    def opacity_picker(self, value):
        item = self.editing_items[self.current_item]
        item["opacity"] = round(value, 1)
        pywinstyles.set_opacity(
            item["panel"], value=item["opacity"] * item["bg_opacity"]
        )
        pywinstyles.set_opacity(
            item["panel_clone"],
            color="black",
            value=item["opacity"],
        )
        self.opacity_entry.delete(0, "end")
        self.opacity_entry.insert(0, str(item["opacity"]))

    def set_opacity(self, event):
        item = self.editing_items[self.current_item]
        try:
            value = float(self.opacity_entry.get())
            if 0 <= value <= 1:
                item["opacity"] = round(value, 1)
                self.opacity_entry.delete(0, "end")
                self.opacity_entry.insert(0, str(item["opacity"]))
                self.opacity_slider.set(value)
                pywinstyles.set_opacity(
                    item["panel"], value=item["opacity"] * item["bg_opacity"]
                )
                pywinstyles.set_opacity(
                    item["panel_clone"],
                    color="black",
                    value=item["opacity"],
                )
            else:
                self.show_popup_window(
                    self.pdf_window,
                    "Error",
                    "Error!",
                    self.fail,
                    "Invalid input - use decimals between 0 and 1",
                    self.text_color,
                )
                print("Invalid input - use decimals between 0 and 1")
        except ValueError:
            self.show_popup_window(
                self.pdf_window,
                "Error",
                "Error!",
                self.fail,
                "Invalid input - use decimals between 0 and 1",
                self.text_color,
            )
            print("Invalid input - use decimals between 0 and 1")

    def background_opacity_picker(self, value):
        item = self.editing_items[self.current_item]
        item["bg_opacity"] = round(value, 1)
        pywinstyles.set_opacity(
            item["panel"], value=item["opacity"] * item["bg_opacity"]
        )
        self.background_opacity_entry.delete(0, "end")
        self.background_opacity_entry.insert(0, str(item["bg_opacity"]))

    def set_background_opacity(self, event):
        item = self.editing_items[self.current_item]
        try:
            value = float(self.background_opacity_entry.get())
            if 0 <= value <= 1:
                item["bg_opacity"] = round(value, 1)
                self.background_opacity_entry.delete(0, "end")
                self.background_opacity_entry.insert(0, str(item["opacity"]))
                self.background_opacity_slider.set(value)
                pywinstyles.set_opacity(
                    item["panel"], value=item["opacity"] * item["bg_opacity"]
                )
            else:
                self.show_popup_window(
                    self.pdf_window,
                    "Error",
                    "Error!",
                    self.fail,
                    "Invalid input - use decimals between 0 and 1",
                    self.text_color,
                )
                print("Invalid input - use decimals between 0 and 1")
        except ValueError:
            self.show_popup_window(
                self.pdf_window,
                "Error",
                "Error!",
                self.fail,
                "Invalid input - use decimals between 0 and 1",
                self.text_color,
            )
            print("Invalid input - use decimals between 0 and 1")

    def font_family_picker(self, font):
        item = self.editing_items[self.current_item]
        if "text" in item:
            item["panel"].configure(font=(font, item["font_size"]))
            item["panel_clone"].configure(font=(font, item["font_size"]))
            item["font_family"] = font

    def font_size_picker(self, value):
        item = self.editing_items[self.current_item]
        if "text" in item:
            item["panel"].configure(
                text=item["text"], font=(item["font_family"], value)
            )
            item["panel_clone"].configure(font=(item["font_family"], value))
            item["font_size"] = round(value)
            self.font_size_label.configure(text="Font Size: " + str(item["font_size"]))

    def text_color_picker(self):
        pick_color = CTkColorPicker.AskColor(
            bg_color=self.dark,
            fg_color=self.second_dark,
            button_color=self.main,
            button_hover_color=self.main_hover,
        )
        pick_color.after(
            200,
            lambda: pick_color.iconbitmap(
                pdf_editor.get_base_path() / "assets" / "logo.ico"
            ),
        )
        color = pick_color.get()
        item = self.editing_items[self.current_item]
        if color and "text" in item:
            self.text_color_button.configure(fg_color=color)
            item["panel"].configure(text_color=color)
            item["panel_clone"].configure(text_color=color)
            item["text_color"] = color

    def set_background(self, image_location="Temp/Temp"):
        self.pdf_page_count = pdf_editor.convert_pdf_page(
            self.pdf, self.current_page_number, image_location, False
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

        if not save_path:
            return

        encrypt_popup = self.show_encrypt_window(
            self.pdf_window,
            "Uknown Error!",
            "Encrypt",
            self.success,
            "Would you like to encrypt the PDF? (Keep the field empty to leave it unencrypted)",
            self.text_color,
        )
        self.pdf_window.wait_window(encrypt_popup)

        pdf_editor.setup_loop_file(self.pdf)
        deleted = 0
        for item in self.editing_items:
            try:
                is_final = False
                if item["index"] == len(self.editing_items) - 1:
                    is_final = True
                if "deleted" not in item:
                    if "image" in item:
                        item_translations = pdf_editor.percentage_converter(
                            self.pdf,
                            (item["width_percent"], item["height_percent"]),
                            (item["relative_x"], item["relative_y"]),
                            edit_page=self.current_page_number,
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
                            edit_page=self.current_page_number,
                        )
                        pdf_editor.create_text_pdf(
                            item["text"],
                            (item_translations[0][0], item_translations[0][1]),
                            item["opacity"],
                            bg_color=item["bg_color"],
                            text_color=item["text_color"],
                            font_family=item["font_family"],
                            font_size=item_translations[2],
                            bg_opacity=item["bg_opacity"],
                        )
                    pdf_editor.merge_pdfs(
                        save_path,
                        item_translations[0][1],
                        is_final,
                        item_translations[1],
                        self.exclusion_list,
                        invert=self.is_include,
                        owner_pw=self.encryption_key,
                    )
                else:
                    deleted += 1
            except PermissionError as e:
                self.show_popup_window(
                    self.pdf_window,
                    "Error",
                    "Uknown Error!",
                    self.fail,
                    str(e) + "\nMake sure not to open the file while editing.",
                    self.text_color,
                )
                print("Unkown error!")
                return
            except Exception as e:
                self.show_popup_window(
                    self.pdf_window,
                    "Error",
                    "Uknown Error!",
                    self.fail,
                    str(e),
                    self.text_color,
                )
                print("Unkown error!")
                return
        if deleted == len(self.editing_items):
            # self.show_popup_window(
            #     self.pdf_window,
            #     "Error",
            #     "Error!",
            #     self.fail,
            #     "There are no active edits!",
            #     self.text_color,
            #     20,
            # )
            # return

            pdf_editor.convert_pdf_to_image_pdf(
                self.pdf, save_path, owner_pw=self.encryption_key
            )

        self.show_popup_window(
            self.pdf_window,
            "Success",
            "Success!",
            self.success,
            "Successfully Converted the PDF File.",
            self.text_color,
            20,
        )
        self.encryption_key = ""

    def add_image(self):
        loaded_logo = ct.filedialog.askopenfilename(
            initialdir=Path.cwd(),
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp")],
        )
        if not loaded_logo:
            return
        new_image = Image.open(loaded_logo).convert("RGBA")  # Ensure RGBA mode
        size = (120, int(120 * new_image.size[1] / new_image.size[0]))
        overlay_image = ct.CTkImage(
            light_image=new_image,
            size=size,
        )
        drag_panel = ct.CTkLabel(
            self.background_panel,
            image=overlay_image,
            text="",
            fg_color="#FFFFFF",
            anchor="center",
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
            "start_width": 0,
            "start_height": 0,
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
        self.calulate_relative_dimensions(item)
        self.editing_items.append(item)
        self.current_item = item["index"]
        self.update_side_panel()

    def add_text(self):
        drag_panel = ct.CTkLabel(
            self.background_panel,
            text="",
            text_color="#FFFFFF",
            fg_color="#000000",
            width=120,
            height=120,
            font=("Arial", 12),
            anchor="center",
        )
        drag_panel_clone = ct.CTkLabel(
            self.background_panel,
            text="Your text",
            text_color="#FFFFFF",
            fg_color="#000000",
            width=120,
            height=120,
            font=("Arial", 12),
            anchor="center",
        )
        drag_panel.place(x=0, y=0)
        drag_panel_clone.place(x=0, y=0)
        pywinstyles.set_opacity(drag_panel_clone, color="#000000")
        item = {
            "index": len(self.editing_items),
            "type": "text",
            "text": "Your text",
            "panel": drag_panel,
            "panel_clone": drag_panel_clone,
            "font_family": "Arial",
            "font_size": 12,
            "relative_font_size": 12,
            "x": 0,
            "y": 0,
            "is_resizing": False,
            "resize_edge": None,
            "start_x": 0,
            "start_y": 0,
            "start_width": 0,
            "start_height": 0,
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

        width = item["panel"].winfo_width()
        height = item["panel"].winfo_height()
        border = 10  # How many pixels near an edge to consider resizing.
        item["start_x"] = event.x - (width / 2)
        item["start_y"] = event.y - (height / 2)
        item["x"] = item["panel"].winfo_x()
        item["y"] = item["panel"].winfo_y()
        # Gets the correct mouse position relative to the window
        x = self.mouse_frame_position_x - item["x"]
        y = self.mouse_frame_position_y - item["y"]

        item["start_width"] = item["panel"].winfo_width()
        item["start_height"] = item["panel"].winfo_height()

        # Determine if click is near an edge based on mouse relative position.
        if x >= width - border and y >= height - border:
            item["is_resizing"] = True
            item["resize_edge"] = "bottom-right"
        elif x <= border and y <= border:
            item["is_resizing"] = True
            item["resize_edge"] = "top-left"
        elif x <= border and y >= height - border:
            item["is_resizing"] = True
            item["resize_edge"] = "bottom-left"
        elif x >= width - border and y <= border:
            item["is_resizing"] = True
            item["resize_edge"] = "top-right"
        elif x >= width - border:
            item["is_resizing"] = True
            item["resize_edge"] = "right"
        elif y <= border:
            item["is_resizing"] = True
            item["resize_edge"] = "top"
        elif y >= height - border:
            item["is_resizing"] = True
            item["resize_edge"] = "bottom"
        elif x <= border:
            item["is_resizing"] = True
            item["resize_edge"] = "left"
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
        right_side = False
        if item["resize_edge"] == "bottom":
            right_side = True
            dy = event.y - item["panel"].winfo_height()
            new_height = item["panel"].winfo_height() + dy
            self.image_frame.configure(cursor="sb_down_arrow")
        elif item["resize_edge"] == "top":
            right_side = False
            dy = event.y * -1
            new_height = item["panel"].winfo_height() + dy
            self.image_frame.configure(cursor="sb_up_arrow")
        elif item["resize_edge"] == "right":
            right_side = True
            dx = event.x - item["panel"].winfo_width()
            new_width = item["panel"].winfo_width() + dx
            self.image_frame.configure(cursor="sb_right_arrow")
        elif item["resize_edge"] == "left":
            dx = event.x * -1
            new_width = item["panel"].winfo_width() + dx
            self.image_frame.configure(cursor="sb_left_arrow")
        elif item["resize_edge"] == "bottom-right":
            right_side = True
            dx = event.x - item["panel"].winfo_width()
            new_width = item["panel"].winfo_width() + dx
            ratio = item["panel"].winfo_width() / item["panel"].winfo_height()
            if "image" in item:
                new_height = new_width / ratio
            else:
                new_height = item["panel"].winfo_height() + dx
            self.image_frame.configure(cursor="sizing")
        elif item["resize_edge"] == "top-left":
            right_side = False
            dx = event.x * -1
            new_width = item["panel"].winfo_width() + dx
            ratio = item["panel"].winfo_width() / item["panel"].winfo_height()
            if "image" in item:
                new_height = new_width / ratio
            else:
                new_height = item["panel"].winfo_height() + dx
            self.image_frame.configure(cursor="sizing")
        elif item["resize_edge"] == "bottom-left":
            right_side = False
            dx = event.x * -1
            new_width = item["panel"].winfo_width() + dx
            ratio = item["panel"].winfo_width() / item["panel"].winfo_height()
            if "image" in item:
                new_height = new_width / ratio
            else:
                new_height = item["panel"].winfo_height() + dx
            self.image_frame.configure(cursor="sizing")
        elif item["resize_edge"] == "top-right":
            right_side = False
            dx = event.x - item["panel"].winfo_width()
            new_width = item["panel"].winfo_width() + dx
            ratio = item["panel"].winfo_width() / item["panel"].winfo_height()
            if "image" in item:
                new_height = new_width / ratio
            else:
                new_height = item["panel"].winfo_height() + dx
            self.image_frame.configure(cursor="sizing")

        if "image" in item:
            item["image"].configure(size=(new_width, new_height))
        else:
            item["panel"].configure(width=new_width, height=new_height)
            item["panel_clone"].configure(width=new_width, height=new_height)

        if right_side:
            item["panel"].place(
                x=((item["x"]) + (new_width / 2)), y=(item["y"] + (new_height / 2))
            )
            item["panel_clone"].place(
                x=((item["x"]) + (new_width / 2)), y=(item["y"] + (new_height / 2))
            )
            return
        elif item["resize_edge"] == "top":
            item["panel"].place(
                x=(item["x"]) + (new_width / 2),
                y=((item["y"] + item["start_height"]) - (new_height / 2)),
            )
            item["panel_clone"].place(
                x=(item["x"]) + (new_width / 2),
                y=((item["y"] + item["start_height"]) - (new_height / 2)),
            )
            return
        elif item["resize_edge"] == "bottom-left":
            item["panel"].place(
                x=((item["x"] + item["start_width"]) - (new_width / 2)),
                y=(item["y"] + (new_height / 2)),
            )
            item["panel_clone"].place(
                x=((item["x"] + item["start_width"]) - (new_width / 2)),
                y=(item["y"] + (new_height / 2)),
            )
            return
        elif item["resize_edge"] == "top-right":
            item["panel"].place(
                x=((item["x"]) + (new_width / 2)),
                y=((item["y"] + item["start_height"]) - (new_height / 2)),
            )
            item["panel_clone"].place(
                x=((item["x"]) + (new_width / 2)),
                y=((item["y"] + item["start_height"]) - (new_height / 2)),
            )
            return

        item["panel"].place(
            x=((item["x"] + item["start_width"]) - (new_width / 2)),
            y=((item["y"] + item["start_height"]) - (new_height / 2)),
        )
        item["panel_clone"].place(
            x=((item["x"] + item["start_width"]) - (new_width / 2)),
            y=((item["y"] + item["start_height"]) - (new_height / 2)),
        )

    def stop_action(self, event, item):
        self.calulate_relative_dimensions(item)
        self.image_frame.configure(cursor="")

    def do_drag(self, event, item):
        image_position_x = item["panel"].winfo_x()
        image_position_y = item["panel"].winfo_y()
        drag_width = item["panel"].winfo_width()
        drag_height = item["panel"].winfo_height()

        # Calculate the new position
        new_x = image_position_x + (event.x - item["start_x"])
        new_y = image_position_y + (event.y - item["start_y"])

        # Optional: Constrain within image_frame bounds
        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()

        # Bind withing image_frame
        new_x = max(drag_width / 2, min(new_x, frame_width - drag_width / 2))
        new_y = max(drag_height / 2, min(new_y, frame_height - drag_height / 2))

        # Move the draggable image
        item["panel"].place(x=new_x, y=new_y, anchor="center")
        item["panel_clone"].place(x=new_x, y=new_y, anchor="center")

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

    def show_popup_window(
        self,
        parent,
        title,
        header_message,
        header_color,
        text_message,
        text_color,
        label_pading=20,
        text_pading=0,
    ):
        popup = ct.CTkToplevel(parent, fg_color=self.dark)
        popup_width = 600
        popup_height = 250
        popup.title(title)
        popup.grab_set()
        popup.configure()
        popup.minsize(popup_width, popup_height)
        popup.maxsize(popup_width, popup_height)
        popup.iconbitmap(pdf_editor.get_base_path() / "assets" / "logo.ico")

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        pos_x = parent_x + (parent_width // 2) - (popup_width // 2)
        pos_y = parent_y + (parent_height // 2) - (popup_height // 2)

        popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")

        popup_label = ct.CTkLabel(
            popup,
            text=header_message,
            wraplength=250,
            text_color=header_color,
            font=(self.global_font_family, 32, self.global_font_style),
        )
        popup_text = ct.CTkLabel(
            popup,
            text=text_message,
            wraplength=300,
            text_color=text_color,
            font=(self.global_font_family, 18, self.global_font_style),
        )

        # popup.overrideredirect(True)
        popup_label.pack(pady=label_pading)
        popup_text.pack(pady=text_pading)

        popup.after(
            200,
            lambda: popup.iconbitmap(
                pdf_editor.get_base_path() / "assets" / "logo.ico"
            ),
        )
        return popup

    def show_encrypt_window(
        self,
        parent,
        title,
        header_message,
        header_color,
        text_message,
        text_color,
        label_pading=20,
        text_pading=0,
    ):
        popup = ct.CTkToplevel(parent, fg_color=self.dark)
        popup_width = 600
        popup_height = 250
        popup.title(title)
        popup.grab_set()
        popup.configure()
        popup.minsize(popup_width, popup_height)
        popup.maxsize(popup_width, popup_height)
        popup.iconbitmap(pdf_editor.get_base_path() / "assets" / "logo.ico")

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        pos_x = parent_x + (parent_width // 2) - (popup_width // 2)
        pos_y = parent_y + (parent_height // 2) - (popup_height // 2)

        popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")

        popup_label = ct.CTkLabel(
            popup,
            text=header_message,
            wraplength=250,
            text_color=header_color,
            font=(self.global_font_family, 32, self.global_font_style),
        )
        popup_text = ct.CTkLabel(
            popup,
            text=text_message,
            wraplength=300,
            text_color=text_color,
            font=(self.global_font_family, 18, self.global_font_style),
        )

        password = ct.CTkEntry(
            popup,
            font=(
                self.global_font_family,
                self.global_font_size,
                self.global_font_style,
            ),
            text_color=self.text_color,
            placeholder_text="Type the encryption password",
            width=200,
            border_width=0,
            fg_color=self.second_dark,
        )

        button = ct.CTkButton(
            popup,
            text="Encrypt",
            height=50,
            fg_color="#111f28",
            hover_color="#213c4e",
            text_color="#e3cdb3",
            command=lambda: self.set_encryption(popup, password.get()),
            font=("Figtree", 12, "bold"),
        )

        # popup.overrideredirect(True)
        popup_label.pack(pady=label_pading)
        popup_text.pack(pady=text_pading)
        password.pack(pady=0)
        button.pack(pady=20)
        popup.protocol(
            "WM_DELETE_WINDOW", lambda: self.set_encryption(popup, password.get())
        )

        popup.after(
            200,
            lambda: popup.iconbitmap(
                pdf_editor.get_base_path() / "assets" / "logo.ico"
            ),
        )
        return popup

    def set_encryption(self, root: ct.CTkToplevel, message):
        self.encryption_key = message
        root.destroy()

    def confirm_exit(self, root: ct.CTk):
        popup = self.show_popup_window(
            self.pdf_window,
            "Confirm",
            "Warning!",
            self.fail,
            "Are you sure you want to exit?",
            self.text_color,
        )
        buttons_frame = ct.CTkFrame(popup, fg_color=self.dark, width=600)
        buttons_frame.pack(pady=20)

        confirm_button = ct.CTkButton(
            buttons_frame,
            text="Exit",
            height=50,
            fg_color="#111f28",
            hover_color="#213c4e",
            text_color="#e3cdb3",
            command=lambda: self.exit_app(),
            font=("Figtree", 12, "bold"),
        )
        cancel_button = ct.CTkButton(
            buttons_frame,
            text="Cancel",
            height=50,
            fg_color=self.success,
            hover_color=self.success_hover,
            text_color="#e3cdb3",
            command=lambda: popup.destroy(),
            font=("Figtree", 12, "bold"),
        )
        confirm_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=16)
        cancel_button.grid(row=0, column=2, columnspan=2, sticky="ew", padx=5, pady=16)

    def exit_app(self):
        self.pdf_window.destroy()
        pdf_editor.cleanup_folders()

    def set_mouse_pos(self, event):
        self.mouse_frame_position_x = (
            self.image_frame.winfo_rootx() - event.x_root
        ) * -1
        self.mouse_frame_position_y = (
            self.image_frame.winfo_rooty() - event.y_root
        ) * -1


root = ct.CTk()
app = MyGui(root)
root.mainloop()
