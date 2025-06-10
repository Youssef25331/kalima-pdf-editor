#  PDF Editor

A Tool for editing PDF's for quickly  the Kalima Platform.


---

## Requirements

To run this project, ensure you have the following dependencies installed:

### Python Packages
- `pypdf` - For PDF manipulation
- `pdf2image` - For converting PDFs to images
- `fpdf` - For creating PDFs
- `PIL` (Pillow) - For image processing
- `customtkinter` - For the graphical user interface
- `CTkColorPicker` - For a custom color picker
- `arabic_reshaper` and `bidi` For Arabic suppport
- `fontTools` For fonts import.

Install these packages using `pip`. For example:
```bash
pip install pypdf pdf2image fpdf Pillow customtkinter CTkColorPicker python-bidi arabic-reshaper fonttools pymupdf pywinstyles
```
### External Dependency
- **Poppler**: Required for PDF-to-image conversion  
  Download [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows) (or the appropriate version for your OS) and place the `bin` folder in the project's root directory.

---
## Usage
1. Launch the app with `python GUI.py`.
2. Choose a PDF file to edit.
3. Make the desired changed from the sidebar.
4. Click convert and and select location. 
5. Ouput will appear in the selected locatoin.

