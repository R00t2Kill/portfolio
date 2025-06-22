import requests
from bs4 import BeautifulSoup
from weasyprint import HTML, CSS
import base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import io
from PyPDF2 import PdfMerger
import time

def func(rollno_from=231381030001, rollno_to=231381030067, ddlCourse="1030203", course_name=None, result_type=""):
    url = "https://exam.bujhansi.ac.in/frmViewCampusCurrentResult.aspx?cd=MwA3ADkA"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Referer": url,
    }

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    response = session.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    viewstategen = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]

    css = CSS(string="""
        @page { size: A4 landscape; margin: 20px; }
        body { font-size: 12px; }
        img { max-width: 100%; display: block; margin: 10px auto; }
        table { width: 100%; border-collapse: collapse; }
        td, th { padding: 5px; border: 1px solid #ddd; }
    """)

    merger = PdfMerger()

    for i in range(int(rollno_from), int(rollno_to) + 1):
        payload = {
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategen,
            "__EVENTVALIDATION": eventvalidation,
            "txtUniqueID": i,
            "ddlCourse": ddlCourse,
            "ddlResultType": result_type,
            "btnGetResult": "View Result",
        }

        response = session.post(url, headers=headers, data=payload, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        if soup.find(string='NAME OF FATHER'):
            for img_tag in soup.find_all("img"):
                if "src" in img_tag.attrs:
                    img_url = img_tag["src"]
                    if not img_url.startswith("http"):
                        img_url = "https://exam.bujhansi.ac.in/" + img_url
                    img_response = session.get(img_url, timeout=10)
                    img_base64 = base64.b64encode(img_response.content).decode()
                    img_format = img_response.headers["Content-Type"].split("/")[-1]
                    img_tag["src"] = f"data:image/{img_format};base64,{img_base64}"

            html_content = str(soup)
            pdf_stream = io.BytesIO()
            HTML(string=html_content).write_pdf(target=pdf_stream, stylesheets=[css])
            pdf_stream.seek(0)
            merger.append(pdf_stream)
            print(f"📄 Processed: result_{i}.pdf")

        time.sleep(1)

    # Output in-memory PDF
    output_buffer = io.BytesIO()
    merger.write(output_buffer)
    merger.close()
    output_buffer.seek(0)

    print(f"✅ Merged PDF generated in memory.")

    return output_buffer
