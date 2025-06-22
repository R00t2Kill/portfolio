
from bs4 import BeautifulSoup
import requests

#vars
url="https://exam.bujhansi.ac.in/frmViewCampusCurrentResult.aspx?cd=MwA3ADkA"
# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    "Referer": url,
}

def func():
	page=requests.get(url,headers=headers,timeout=10)
	pagetext=page.text


	soup=BeautifulSoup(pagetext,"html.parser")
	ddl_course = soup.find("select", id="ddlCourse")


	# Extract all <option> values (skipping the first '-Select-' one)
	courses = {}
	resultType={"Main":"","Special Back":"6"}

	for option in ddl_course.find_all("option")[1:]:  # Skip '-Select-'
		ddlid = option.get("value")
		ddlcourse = option.text.strip()
		courses[ddlcourse]=ddlid
	return courses,resultType

