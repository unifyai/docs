import os
from pypdf import PdfReader, PdfWriter

fname = "169000-foundation-tier-sample-assessment-materials.pdf"
this_dir = os.path.dirname(__file__)
pdf_dir = os.path.join(this_dir, "pdfs")
pdf_path = os.path.join(pdf_dir, fname)
reader = PdfReader(pdf_path)
paper_cover_text = "completetheboxesabovewithyourname,centrenumberandcandidatenumber."
markscheme_cover_text = "markscheme"
paper_cover_pages = list()
markscheme_cover_pages = list()
looking_for_paper = True

for i, page in enumerate(reader.pages):
    text_stripped = page.extract_text().lower().replace(" ", "")
    if looking_for_paper and paper_cover_text in text_stripped:
        paper_cover_pages.append(i)
        looking_for_paper = False
    elif not looking_for_paper and markscheme_cover_text in text_stripped:
        markscheme_cover_pages.append(i)
        looking_for_paper = True

pdf_subdir = os.path.join(pdf_dir, fname[:-4])
os.makedirs(pdf_subdir, exist_ok=True)

left_pointer = paper_cover_pages.pop(0)
count = 1
while paper_cover_pages or markscheme_cover_pages:
    count_dir = os.path.join(pdf_subdir, str(count))
    os.makedirs(count_dir, exist_ok=True)
    # paper
    writer = PdfWriter()
    right_pointer = markscheme_cover_pages.pop(0)
    [writer.add_page(pg) for pg in reader.pages[left_pointer:right_pointer]]
    paper_fpath = os.path.join(count_dir, "paper.pdf")
    writer.write(paper_fpath)
    left_pointer = right_pointer
    # mark-scheme
    writer = PdfWriter()
    if paper_cover_pages:
        right_pointer = paper_cover_pages.pop(0)
    else:
        right_pointer = len(reader.pages) + 1
    [writer.add_page(pg) for pg in reader.pages[left_pointer:right_pointer]]
    markscheme_fpath = os.path.join(count_dir, "markscheme.pdf")
    writer.write(markscheme_fpath)
    left_pointer = right_pointer
    # count
    count += 1
