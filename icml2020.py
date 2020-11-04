import csv
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup


@dataclass
class Paper:
    title: str = ""
    authors: List[str] = None
    keywords: List[str] = None
    pdf_url: str = ""


def _split_and_rejoin(s: str):
    return " ".join(s.split())


if __name__ == "__main__":
    with open("icml2020-reprlearning.html", "r") as html:
        soup = BeautifulSoup(html, "html.parser")

    papers = []
    for div in soup.find_all("div", recursive=False):
        paper = Paper()

        strings = div.stripped_strings

        paper.title = _split_and_rejoin(next(strings))

        paper.authors = [s.strip() for s in next(strings).split("•")]
        paper.authors = [_split_and_rejoin(s) for s in paper.authors]

        paper.keywords = [s.strip() for s in next(strings)[10:].split("•")]
        paper.keywords = [_split_and_rejoin(s) for s in paper.keywords]

        paper.pdf_url = div.find("a", string="PDF")["href"]

        papers.append(paper)

    count = 0
    with open("icml2020-reprlearning.csv", "w") as fo:
        csv_writer = csv.writer(fo)
        for paper in papers:
            print(paper.title)
            csv_writer.writerow(
                [
                    paper.title,
                    "\n".join(paper.authors),
                    "\n".join(paper.keywords),
                    paper.pdf_url,
                ]
            )
            count += 1
    print(count)
