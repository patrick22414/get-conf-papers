import csv
import os
import dataclasses
from os import path
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclasses.dataclass
class IcmlPaper:
    title: str = ""
    authors: List[str] = dataclasses.field(default_factory=list)
    pdf: str = "--"
    supp_pdf: str = "--"
    code_url: str = "--"


icml_files = ["html/icml2019-proceedings.html", "html/icml2020-proceedings.html"]

for filename in icml_files:
    conference = path.splitext(path.split(filename)[-1])[0]
    print()
    print(conference)

    with open(filename, "r") as fin:
        soup = BeautifulSoup(fin, "html.parser")

    all_papers = []
    for div in soup.find_all("div", "paper"):
        title = div.find("p", "title").get_text()

        if "adversarial" in title.lower() and "generative" not in title.lower():
            paper = IcmlPaper(title)

            paper.authors = div.find("span", "authors").get_text().split(",\xa0")

            links = div.find("p", "links")
            for a in links.find_all("a"):
                a_text = a.get_text()
                if "Download PDF" in a_text:
                    paper.pdf = a["href"]
                elif "Supplementary PDF" in a_text:
                    paper.supp_pdf = a["href"]
                elif "Code" in a_text or "Software" in a_text:
                    paper.code_url = a["href"]

            all_papers.append(paper)

    with open(f"csv/adv-{conference}.csv", "w") as fout:
        writer = csv.DictWriter(
            fout, fieldnames=["PDF", "Supplementary PDF", "Title", "Authors", "Code"]
        )

        writer.writeheader()
        for paper in all_papers:
            writer.writerow(
                {
                    "PDF": paper.pdf,
                    "Supplementary PDF": paper.supp_pdf,
                    "Title": paper.title,
                    "Authors": "\n".join(paper.authors),
                    "Code": paper.code_url,
                }
            )
