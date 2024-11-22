import os
from docx2pdf import convert
import PyPDF2


def gettext_from_pdf(filepath, out_path):
    print('gettext_from_pdf')
    f_1 = open(out_path, "a", encoding="utf-8")

    file = open(filepath, 'rb')
    file_reader = PyPDF2.PdfReader(file)

    text = ''
    for page in range(file_reader.numPages):
        text_extract = file_reader.pages[page]
        text = text + '\n\n' + text_extract.extract_text()

    f_1.write(text)
    f_1.close()
    file.close()

    return text


print("get_data_paths")
input_file_name_1 = 'MFG5790.docx'

# Paths
input_path_1 = './Input/'
output_path_1 = './Output/'
temp_path_1 = './temp_files/'

input_file_1 = input_file_name_1
print("--------{}----------".format(input_file_1))

# Identify the file type
file_name_1 = "_".join(input_file_1.split('.')[:-1])
file_type_1 = str(input_file_1.split('.')[-1])

# Generate paths to save files
file_path_1 = input_path_1 + input_file_1
temp_path_1 = temp_path_1 + 'temp_files_' + file_name_1 + '/'
out_path_1 = temp_path_1 + 'output_text.txt'

if not os.path.exists(temp_path_1):
    os.makedirs(temp_path_1)

print('Extracting text from docx')
out_path = temp_path_1 + 'output_text.txt'

if 'output_text.txt' not in os.listdir(temp_path_1):
    print('gettext_from_docx')
    pdf_path = temp_path_1 + file_name_1 + '.pdf'
    print('PDF paht', pdf_path)
    convert(file_path_1, pdf_path)
    print("convertion done")
    data = gettext_from_pdf(pdf_path, out_path)