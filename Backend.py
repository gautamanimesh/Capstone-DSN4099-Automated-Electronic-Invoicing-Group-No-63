import io
import os
import filetype as filetype
from PIL import Image
import pytesseract
from wand.image import Image as wi
import cv2
import numpy as np
from PIL import Image
import pytesseract
import filetype
import re
import csv
from fpdf import FPDF 
from config import *
from server import *
from tkinter.filedialog import askopenfilename
 

def prepro():
    img = cv2.imread(fname)

    # GraScale Image
    def get_greyscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise Removal
    def remove_noise(image):
        return cv2.medianBlur(image, 5)

    # Thresholding
    def thresholding(image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Dilation
    def dilate(image):
        kernel = np.ones((5, 5), np.unit8)
        return cv2.dilate(image, kernel, iterations=1)

    # canny edge detection
    def canny(image):
        return cv2.Canny(image, 100, 200)

    # Template Matching
    def match_template(image, template):
        return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    image = cv2.imread(pdfImg)
    gray = get_greyscale(image)
    # thresh = thresholding(image)
    canny = canny(image)


def ocr():
    im = Image.open(pdfImg)
    text = pytesseract.image_to_string(im, lang='eng')
    print(text)


def output(content):
    file = open("Invoice.txt", "a")
    file.write(content)
    file.close()

    # REGEX Part
    text_file = open('Invoice.txt', 'r')
    text = text_file.read()

    # cleaning
    words = text.split()
    words = [word.strip('.,!;()[]') for word in words]
    words = [word.replace("'s", '') for word in words]

    # finding unique words
    unique = ["GSTIN", "Name", "Address", "SAP", "Unique Id", "Customer Id", "Invoice", "Date", "State Code", "Goods",
              "SKU", "QTY", "Unit", "Rate", "Total Value", "Discount", "Taxable Value", "IGST", "Amt",
              "Total Invoice Value", "Total Value"]
    for word in words:
        if word in unique:
            # unique.append(word)
            for i in range(len(unique)):  # making regex for each unique word
                re.compile(unique[i])
                for line in open("Invoice.txt"):
                    for match in re.finditer(unique[i], line):  # finding the regex through file
                        with open('Invoice_template_output.csv', 'w') as f:
                            writer = csv.writer(f)
                            writer.writerow(line)  # extracting the words into CSV

    with open('Invoice_template_output.csv', newline='') as f:  # CSV to Pdf form
        reader = csv.reader(f)

        pdf = FPDF()
        pdf.add_page()
        page_width = pdf.w - 2 * pdf.l_margin

        pdf.set_font('Times', 'B', 14.0)
        pdf.cell(page_width, 0.0, 'ITR-4', align='C')
        pdf.ln(10)

        pdf.set_font('Courier', '', 12)

        col_width = page_width / 4

        pdf.ln(1)

        th = pdf.font_size

        for row in reader:
            # print(row)
            pdf.cell(col_width, th, str(row[0]), border=1)
            pdf.cell(col_width, th, row[1], border=1)
            pdf.cell(col_width, th, row[2], border=1)
            pdf.cell(col_width, th, row[3], border=1)
            pdf.ln(th)

        pdf.ln(10)
        pdf.set_font('Times', '', 10.0)
        pdf.cell(page_width, 0.0, '- end of report -', align='C')
        config.finalfile = "download/ITR-4.pdf"
        pdf.output('ITR-4.pdf', 'F')


fname = r"uploads/"+config.filename
f = filetype.guess(fname)
# pdf or not
# askopenfilename() #popup a window for selecting file

if f.extension == "pdf":  # if pdf converting it to jpeg

    pdf = wi(filename=fname, resolution=300)

    pdfImg = pdf.convert('jpeg')

    imgBlobs = []

    for img in pdfImg.sequence:
        page = wi(image=img)
        imgBlobs.append(page.make_blob('jpeg'))

    extracted_text = []

    for imgBlob in imgBlobs:
        im = Image.open(io.BytesIO(imgBlob))
        text = pytesseract.image_to_string(im, lang='eng')
        extracted_text.append(text)

    prepro() # calling prepro function
    ocr() # calling ocr function
    output(extracted_text[0])# calling output function to store content in a text file

elif f.extension == "jpg":  # if file is jpeg
    prepro()  # calling prepro function
    ocr()  # calling ocr function
    output()  # preparing output

else:
    print("File not supported")
