"""Exportación Word editable de la misma memoria; herramienta documental local."""
from pathlib import Path


def export_docx(markup, browser, docs, build):
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.opc.constants import RELATIONSHIP_TYPE
    from docx.shared import Mm, Pt, RGBColor
    from lxml import html
    from PIL import Image

    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Mm(210), Mm(297)
    section.top_margin, section.bottom_margin = Mm(18), Mm(20)
    section.left_margin = section.right_margin = Mm(18)
    normal = document.styles['Normal']
    normal.font.name, normal.font.size = 'Arial', Pt(10.5)
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.18
    for style, size in [('Title', 32), ('Heading 1', 19), ('Heading 2', 12)]:
        document.styles[style].font.name = 'Arial'
        document.styles[style].font.size = Pt(size)
        document.styles[style].font.color.rgb = RGBColor.from_string('123C32')
    document.core_properties.title = 'Seller Action Plan — Memoria académica'
    document.core_properties.author = 'Pablo Rosales'
    document.core_properties.subject = 'Django, React y PostgreSQL — versión pública 97b4bff'

    def inline(paragraph, node, bold=False):
        if node.text:
            paragraph.add_run(node.text).bold = bold
        for child in node:
            if child.tag == 'a':
                link = OxmlElement('w:hyperlink')
                link.set(qn('r:id'), paragraph.part.relate_to(child.get('href'), RELATIONSHIP_TYPE.HYPERLINK, is_external=True))
                run = OxmlElement('w:r'); properties = OxmlElement('w:rPr')
                color = OxmlElement('w:color'); color.set(qn('w:val'), '176B50'); properties.append(color)
                run.append(properties); text = OxmlElement('w:t'); text.text = child.text_content(); run.append(text)
                link.append(run); paragraph._p.append(link)
            elif child.tag == 'code':
                run = paragraph.add_run(child.text_content()); run.font.name = 'Courier New'; run.font.size = Pt(8.5)
            else:
                inline(paragraph, child, bold or child.tag == 'strong')
            if child.tail:
                paragraph.add_run(child.tail)

    def blocks(parent):
        for node in parent:
            tag = node.tag
            if tag == 'div':
                blocks(node)
                if node.get('class') == 'cover':
                    document.add_page_break()
            elif tag == 'nav':
                document.add_heading('Índice de contenidos', level=1)
                for item in node.xpath('.//li'):
                    document.add_paragraph(item.text_content())
                document.add_page_break()
            elif tag in ['h1', 'h2', 'h3']:
                paragraph = document.add_paragraph(style={'h1':'Title', 'h2':'Heading 1', 'h3':'Heading 2'}[tag])
                inline(paragraph, node)
            elif tag == 'p':
                inline(document.add_paragraph(), node)
            elif tag == 'ul':
                for item in node:
                    inline(document.add_paragraph(style='List Bullet'), item)
            elif tag == 'pre':
                paragraph = document.add_paragraph()
                run = paragraph.add_run(node.text_content()); run.font.name = 'Courier New'; run.font.size = Pt(8.5)
            elif tag == 'table':
                rows = node.xpath('./thead/tr|./tbody/tr')
                table = document.add_table(rows=0, cols=len(rows[0])); table.style = 'Table Grid'
                for index, row in enumerate(rows):
                    cells = table.add_row().cells
                    for cell, content in zip(cells, row):
                        inline(cell.paragraphs[0], content, index == 0)
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.size = Pt(8.5)
                    props = table.rows[-1]._tr.get_or_add_trPr()
                    props.append(OxmlElement('w:cantSplit'))
                    if index == 0:
                        props.append(OxmlElement('w:tblHeader'))
                document.add_paragraph()
            elif tag == 'figure':
                source = Path(node.find('img').get('src').removeprefix('file://'))
                if source.suffix == '.svg':
                    image_page = browser.new_page(viewport={'width':1400,'height':1400}, device_scale_factor=2)
                    image_page.goto(source.as_uri())
                    target = build / (source.stem + '-docx.png')
                    image_page.locator('svg').screenshot(path=str(target))
                    image_page.close(); source = target
                width, height = Image.open(source).size
                factor = min(174 / width, 185 / height)
                paragraph = document.add_paragraph(); paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.add_run().add_picture(str(source), width=Mm(width*factor), height=Mm(height*factor))
                caption = document.add_paragraph(node.find('figcaption').text_content())
                caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in caption.runs:
                    run.font.size = Pt(9)

    blocks(html.fromstring('<main>'+markup+'</main>'))
    footer = section.footer.paragraphs[0]
    footer.add_run('SAP · Pablo Rosales · ')
    for field in ['PAGE', 'NUMPAGES']:
        value = OxmlElement('w:fldSimple'); value.set(qn('w:instr'), field); footer._p.append(value)
        if field == 'PAGE':
            footer.add_run(' / ')
    document.save(docs / 'memoria-pfm.docx')
    print('DOCX editable generado: '+str(docs / 'memoria-pfm.docx'))
