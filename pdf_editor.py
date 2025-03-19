import math
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path
from fpdf import FPDF
from PIL import Image
from pathlib import Path


def hex_to_rgb(hex_color):
    # Convert a HEX color string (e.g., 'FF0000') to an RGB tuple.
    hex_color = hex_color.lstrip("#")  # Remove optional '#'
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def resize_and_save_image(input_path, output_path, width, bg_color=None):
    # Resize an image to a specified width and save it with an optional background color.
    try:
        img = Image.open(input_path).convert("RGBA")
        percentage = width / img.width
        size = (math.floor(img.width * percentage), math.floor(img.height * percentage))
        img = img.resize(size, Image.Resampling.LANCZOS)  # Better quality resizing

        if bg_color:
            bg_rgb = hex_to_rgb(bg_color)
            background = Image.new("RGBA", size, bg_rgb + (255,))  # Add alpha channel
            background.paste(img, (0, 0), mask=img)
            background.save(output_path, "PDF")
        else:
            img.save(output_path, "PDF")

        return size
    except FileNotFoundError:
        raise ValueError(f"Image file not found: {input_path}")
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")


def create_text_pdf(text, dimensions, output_path, text_color="000000", bg_color=None):
    """Create a PDF with text at specified dimensions, with optional text and background colors."""
    pdf = FPDF("P", "pt", dimensions)
    pdf.set_margins(0, 0)
    pdf.set_auto_page_break(False)
    pdf.add_page()

    text_rgb = hex_to_rgb(text_color)
    pdf.set_text_color(*text_rgb)

    if bg_color:
        bg_rgb = hex_to_rgb(bg_color)
        pdf.set_fill_color(*bg_rgb)
        pdf.rect(
            0, 0, 9999, 9999, style="F"
        )  # I don't remember why I set those to 9999 but im sure there was a good reason.

    pdf.set_font("helvetica", size=int(dimensions[0] * 0.09))
    pdf.multi_cell(0, 22, txt=text, align="C", border=0)
    pdf.output(output_path)


# def get_num_of_lines_in_multicell(pdf, message):
#     # divide the string in words
#     words = message.split(" ")
#     line = ""
#     n = 1
#     for word in words:
#         line += word + " "
#         line_width = pdf.get_string_width(line)
#         # In the next if it is necessary subtract 1 to the WIDTH
#         if line_width > 200 - 1:
#             # the multi_cell() insert a line break
#             n += 1
#             line = word + " "
#     print(n)
#     return n


# converts a page to a PNG to be loaded in GUI
def convert_pdf_page(pdf_path, page_number):
    try:
        # Convert specific page to image
        images = convert_from_path(
            pdf_path,
            first_page=page_number,  # Convert to 1-based
            last_page=page_number,  # Only convert one page
            dpi=200,
            poppler_path=r"poppler-24.08.0\Library\bin",
        )

        if images:
            images[0].save("temp_pdf.png", "PNG")
            print(f"Successfully converted page {page_number} to temp_pdf.png")

            return PdfReader(pdf_path).get_num_pages()
        else:
            print("Conversion failed: No image generated")
            return False

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def merge_pdfs(
    base_pdf_path,
    overlay_pdf_path,
    output_path,
    overlay_height,
    start_loc=(0, 0),
    exclude_pages=None,
    percentage=False,
):
    # Merge an overlay PDF onto a base PDF at a specified location, excluding certain pages.
    exclude_pages = exclude_pages or []
    base_pdf_path = Path(base_pdf_path).resolve()
    overlay_pdf_path = Path(overlay_pdf_path).resolve()
    output_path = Path(output_path).resolve()

    try:
        base_pdf = PdfReader(base_pdf_path)
        overlay_pdf = PdfReader(overlay_pdf_path)
        writer = PdfWriter()
        # Percentage In the case the values where being sent by the GUI
        if percentage:
            # In my testing this formula was the most accurate to what the user sees.
            start_loc = (
                math.floor(base_pdf.pages[0].mediabox[2] * start_loc[0]) - 1,
                math.floor(base_pdf.pages[0].mediabox[3] * start_loc[1]) - 1,
            )
            print(start_loc)

        for page_num, page in enumerate(base_pdf.pages, start=1):
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

        with open(output_path, "wb") as f:
            writer.write(f)
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
