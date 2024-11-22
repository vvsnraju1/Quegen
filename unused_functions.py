from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table, _Row
from docx.text.paragraph import Paragraph


def iter_block_items(parent):
    print('iter_block_items')
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    elif isinstance(parent, _Row):
        parent_elm = parent._tr
    else:
        raise ValueError("something's not right")
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def gettext_from_docx_old(filename, out_path):
    print('gettext_from_docx_old')
    f_1 = open(out_path, "a", encoding="utf-8")

    document = Document(filename)
    counter = 0
    for block in iter_block_items(document):
        if isinstance(block, Paragraph):
            f_1.write(block.text)
            f_1.write('\n')
        elif isinstance(block, Table):
            for row in block.rows:
                row_data = []
                for cell in row.cells:
                    counter += 1
                    for paragraph in cell.paragraphs:
                        row_data.append(paragraph.text)
                f_1.write("\n".join(row_data))
    f_1.close()

    return
