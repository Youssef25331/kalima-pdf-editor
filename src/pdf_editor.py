import math, os, sys
import io
from pypdf import PdfReader, PdfWriter
from pypdf.constants import UserAccessPermissions
import pymupdf
import cryptography
from PIL import Image
from fpdf import FPDF
from fontTools.ttLib import TTFont
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display


def get_base_path():
    return (
        Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).parent
    )


def get_exe_dir():
    return (
        Path(sys.executable).parent
        if getattr(sys, "frozen", False)
        else Path(__file__).parent
    )


def setup_temp_dir():
    temp_dir = get_exe_dir() / "Temp"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir


temp_dir = setup_temp_dir()
temp_pdf = temp_dir / "Temp.pdf"
temp_loop_pdf = temp_dir / "Loop.pdf"
temp_background = temp_dir / "Temp"
temp_text = temp_dir / "Temp_Text.png"
temp_bg = temp_dir / "Temp_bg.png"


if getattr(sys, "frozen", False):
    font_dir = get_exe_dir() / "Fonts"
else:
    font_dir = Path(__file__).parent / "Fonts"


# Construct the path to Poppler binaries
# poppler_path = os.path.join(get_base_path(), "poppler-24.08.0", "Library", "bin")


def setup_loop_file(source_file, dest_file=temp_loop_pdf):
    os.makedirs(dest_file.parent, exist_ok=True)

    with open(source_file, "rb") as src, open(dest_file, "wb") as dst:
        dst.write(src.read())


def hex_to_rgb(hex_color):
    # Convert a HEX color string (e.g., 'FF0000') to an RGB tuple.
    hex_color = hex_color.lstrip("#")  # Remove optional '#'
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def generate_modified_fonts():
    if not (font_dir / "Modified").exists():
        (font_dir / "Modified").mkdir()

    for font_path in font_dir.glob("*.ttf"):
        font = TTFont(font_path)
        font["OS/2"].fsType = 0
        font_file = (
            font_dir / "Modified" / ("_Modified_" + str(font_path).split("\\")[-1])
        )
        if not font_file.exists():
            font.save(font_file)


# For importing fonts into FPDF
def load_project_fonts(generate=True):
    # Define the "fonts" folder relative to the project root
    fonts = []
    if not font_dir.exists():
        font_dir.mkdir()
        print("Created 'Fonts' folder. Make sure to add fonts.")
        return [("Arial", None, None)]
    elif not any(font_dir.iterdir()):  # Check if directory is empty
        return [("Arial", None, None)]
    if generate:
        generate_modified_fonts()
    for font_path in (font_dir / "Modified").glob("*.ttf"):
        font_name = Path(font_path)
        font = TTFont(font_path)
        if "OS/2" in font:
            if font["OS/2"].fsType != 0:
                break
        font_name = font["name"].getDebugName(4)
        fonts.append((font_name, font_path, font_path))
    return fonts


def resize_and_save_image(
    input_path, opacity, width, height=None, bg_color=None, output_path=temp_pdf
):
    # Resize an image to a specified width and save it with an optional background color.
    try:
        img = Image.open(input_path).convert("RGBA")
        width_percentage = width / img.width
        if height:
            height_percentage = height / img.height
        else:
            height_percentage = width_percentage
        size = (
            math.floor(img.width * width_percentage),
            math.floor(img.height * height_percentage),
        )
        img = img.resize(size, Image.Resampling.LANCZOS)  # Better quality resizing

        if bg_color:
            bg_rgb = hex_to_rgb(bg_color)
            background = Image.new("RGBA", size, bg_rgb + (255,))  # Add alpha channel
            background.paste(img, (0, 0), mask=img)
            background.putalpha(int(255 * opacity))
            background.save(output_path, "PDF")
        else:
            img.save(output_path, "PDF")

        return size
    except FileNotFoundError:
        raise ValueError(f"Image file not found: {input_path}")
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")


def create_text_pdf(
    text,
    dimensions,
    opacity,
    text_color="000000",
    bg_color=None,
    font_family="arial",
    font_size=None,
    output_path=temp_pdf,
    bg_opacity=1,
):
    # Create a PDF with text at specified dimensions, with optional text and background colors.
    pdf = FPDF("P", "pt", dimensions)
    pdf.set_margins(0, 0)
    pdf.set_auto_page_break(False)
    pdf.add_page()

    text_rgb = hex_to_rgb(text_color)
    reshaped_text = arabic_reshaper.reshape(text)  # Connects letters
    normalized_text = get_display(reshaped_text)
    pdf.set_text_color(*text_rgb)
    fonts = load_project_fonts(False)
    for font_name, font_path, _ in fonts:
        if font_path:
            pdf.add_font(font_name, "", str(font_path), uni=True)

    if not font_size:
        font_size = int(dimensions[0] * 0.09)

    bg_rgb = hex_to_rgb(bg_color)
    pdf.set_fill_color(*bg_rgb)
    pdf.set_font(font_family, size=int(math.floor(font_size)))

    if opacity == 1 and bg_opacity == 1:
        pdf.rect(
            0, 0, 9999, 9999, style="F"
        )  # I don't remember why I set those to 9999 but im sure there was a good reason.
        pdf.cell(
            dimensions[0],
            dimensions[1],
            txt=normalized_text,
            align="C",
            ln=0,
            border=0,
        )
        pdf.output(output_path)

    elif opacity == 0:
        pdf.output(output_path)

    else:
        pdf.rect(
            0, 0, 9999, 9999, style="F"
        )  # I don't remember why I set those to 9999 but im sure there was a good reason.
        pdf.output(output_path)
        convert_pdf_page(output_path, 1, temp_bg)

        text_pdf = FPDF("P", "pt", dimensions)
        text_pdf.set_margins(0, 0)
        text_pdf.set_auto_page_break(False)
        text_pdf.add_page()
        text_pdf.set_text_color(*text_rgb)
        text_pdf.set_font(font_family, size=int(math.floor(font_size)))
        text_pdf.cell(
            dimensions[0],
            dimensions[1],
            txt=normalized_text,
            align="C",
            ln=0,
            border=0,
        )
        text_pdf.output(output_path)
        convert_pdf_page(temp_pdf, 1, temp_text)

        img = Image.open(temp_text).convert("RGBA")
        img = img.resize((dimensions[0], dimensions[1]), Image.Resampling.LANCZOS)

        bg_img = Image.open(temp_bg).convert("RGBA")
        bg_img = bg_img.resize((dimensions[0], dimensions[1]), Image.Resampling.LANCZOS)
        bg_img.putalpha(int(255 * bg_opacity * opacity))

        layer = Image.new("RGBA", bg_img.size, (0, 0, 0, 0))
        layer.paste(img, (0, 0))
        layer2 = layer.copy()
        layer2.putalpha(int(255 * opacity))
        layer.paste(layer2, (0, 0), layer)
        result = Image.alpha_composite(bg_img, layer)
        result.save(temp_pdf, "PDF")


def convert_pdf_page(pdf_path, page_number, output, alpha=True):
    try:
        setup_temp_dir()
        doc = pymupdf.open(pdf_path)
        page = doc[page_number - 1]
        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(200 / 72, 200 / 72), alpha=alpha
        )  # DPI 200, with alpha
        pix.pil_save(output, format="PNG", optimize=True)
        return PdfReader(pdf_path).get_num_pages()
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def convert_pdf_to_image_pdf(
    input_pdf_path="./output.pdf",
    output_pdf_path="./THE_output.pdf",
    dpi=150,  # Reduced DPI for smaller file size
    quality=75,  # JPEG quality (0-100, lower means smaller size)
    owner_pw=None,
):
    pdf_doc = pymupdf.open(input_pdf_path)
    img_pdf = pymupdf.open()

    for page_num in range(pdf_doc.page_count):
        page = pdf_doc[page_num]
        # Lower DPI to reduce resolution
        pix = page.get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72), alpha=False)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        img_buffer = io.BytesIO()
        img.save(img_buffer, format="JPEG", quality=quality)

        new_page = img_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=img_buffer.getvalue())

    # Save the new PDF
    if owner_pw:
        img_pdf.save(
            output_pdf_path,
            garbage=4,
            deflate=True,
            owner_pw=owner_pw,
            permissions=0,
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
        )
    else:
        img_pdf.save(
            output_pdf_path,
            garbage=4,
            deflate=True,
        )

    pdf_doc.close()
    img_pdf.close()


# Percentage In the case the values where being sent by the GUI
def percentage_converter(
    pdf_path, dimensions, location, font_percetage=None, edit_page=1
):
    edit_page -= 1
    pdf = PdfReader(pdf_path)

    if pdf.pages[edit_page].rotation % 180 == 90:
        converted_dimensions = (
            math.floor(pdf.pages[edit_page].mediabox[3] * dimensions[0]),
            math.floor(pdf.pages[edit_page].mediabox[2] * dimensions[1]),
        )

        # In my testing this formula was the most accurate to what the user sees.
        converted_location = (
            math.floor(pdf.pages[edit_page].mediabox[3] * location[0]),
            math.floor(pdf.pages[edit_page].mediabox[2] * location[1]),
        )
        if font_percetage:
            converted_font_size = pdf.pages[edit_page].mediabox[2] * font_percetage
            return [converted_dimensions, converted_location, converted_font_size]
    else:
        converted_dimensions = (
            math.floor(pdf.pages[edit_page].mediabox[2] * dimensions[0]),
            math.floor(pdf.pages[edit_page].mediabox[3] * dimensions[1]),
        )

        # In my testing this formula was the most accurate to what the user sees.
        converted_location = (
            math.floor(pdf.pages[edit_page].mediabox[2] * location[0]),
            math.floor(pdf.pages[edit_page].mediabox[3] * location[1]),
        )

        if font_percetage:
            converted_font_size = pdf.pages[edit_page].mediabox[3] * font_percetage
            return [converted_dimensions, converted_location, converted_font_size]

    return [converted_dimensions, converted_location]


def merge_pdfs(
    output_path,
    overlay_height,
    is_final,
    start_loc=(0, 0),
    exclude_pages=None,
    overlay_pdf_path=temp_pdf,
    base_pdf_path=temp_loop_pdf,
    invert=False,
    owner_pw=None,
):
    # Merge an overlay PDF onto a base PDF at a specified location, excluding certain pages.
    exclude_pages = exclude_pages or []
    overlay_pdf_path = Path(overlay_pdf_path).resolve()

    try:
        base_pdf = PdfReader(base_pdf_path)
        overlay_pdf = PdfReader(overlay_pdf_path)
        writer = PdfWriter()

        for page_num, page in enumerate(base_pdf.pages, start=1):
            page.transfer_rotation_to_content()
            if invert:
                if page_num in exclude_pages:
                    page.merge_translated_page(
                        overlay_pdf.pages[0],
                        start_loc[0],
                        page.mediabox[3]
                        - overlay_height
                        - start_loc[
                            1
                        ],  # Removes the overlay and the Y start locatin to be inserted in the correct spot since the Y starts from the bottom.
                    )
            else:
                if page_num not in exclude_pages:
                    page.merge_translated_page(
                        overlay_pdf.pages[0],
                        start_loc[0],
                        page.mediabox[3]
                        - overlay_height
                        - start_loc[
                            1
                        ],  # Removes the overlay and the Y start locatin to be inserted in the correct spot since the Y starts from the bottom.
                    )
            writer.add_page(page)

        with open(temp_loop_pdf, "wb") as out:
            writer.write(out)
        if is_final and True:
            convert_pdf_to_image_pdf(temp_loop_pdf, output_path, owner_pw=owner_pw)
        elif is_final and False:
            writer.write(output_path)

    except FileNotFoundError:
        raise ValueError(f"PDF file not found: {base_pdf_path} or {overlay_pdf_path}")
    except Exception as e:
        raise ValueError(f"Error merging PDFs: {e}")


if __name__ == "__main__":
    # The cli option for the script
    output_pdf = "output.pdf"
    temp_path = "temp.pdf"
    while True:
        mode = input('please choose mode "text" or "logo" : ')
        if mode.lower() == "logo":
            logo_path = input("Enter logo path: ")
            pdf_path = input("Enter PDF path: ")
            width = int(input("Enter width: "))
            bg_color = input("Enter background color in HEX (optional): ") or None
            start_loc = tuple(
                map(float, input("Enter insert location (e.g., 20,300): ").split(","))
            )
            exclude = list(
                map(int, input("Enter excluded pages (e.g., 1,2): ").split(","))
            )
            size = resize_and_save_image(logo_path, temp_path, width, bg_color)
            merge_pdfs(
                pdf_path, "testing2.pdf", output_pdf, size[1], start_loc, exclude, True
            )
            break

        elif mode.lower() == "text":
            temp_path = "temp_text.pdf"
            input_pdf = input("please enter pdf path: ")
            input_loc = tuple(
                map(int, input("Enter insert location (e.g., 20,300): ").split(","))
            ) or (0, 0)

            text = input("please enter text : ") or "John Doe"
            text_color = (
                input("please enter text color in HEX (optional): ") or "000000"
            )
            bg_color = (
                input("please enter background color in HEX (optional): ") or "FFFFFF"
            )

            dims = tuple(
                map(int, input("Enter dimensions (e.g., 200,50): ").split(","))
            )

            exclusion = (
                list(
                    map(
                        int,
                        input(
                            "Enter excluded pages separated by commas (optional): "
                        ).split(","),
                    )
                )
                or []
            )
            create_text_pdf(text, dims, temp_path)
            break
