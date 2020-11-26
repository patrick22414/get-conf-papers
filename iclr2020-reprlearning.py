from dataclasses import dataclass, field
from typing import List

from bs4 import BeautifulSoup
import csv


def _split_and_rejoin(s: str):
    return " ".join(s.split())


@dataclass
class Paper:
    title: str = ""
    authors: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    tldr: str = ""
    abstract: str = ""
    pdf_url: str = ""
    code_url: str = ""


if __name__ == "__main__":
    html_files = [
        "iclr2020-oral.html",
        "iclr2020-spotlight.html",
        "iclr2020-poster.html",
    ]

    papers = []

    for html_file in html_files:
        print()
        print(html_file)
        with open("html/" + html_file, "r") as html:
            soup = BeautifulSoup(html, "html.parser")

        for item in soup.ul.find_all("li", recursive=False):
            paper = Paper()

            if item.h4 is None:
                continue

            for author in item.find("div", "note-authors").find_all("a"):
                # authors = [x.string or x.get_text() for x in result.children]
                paper.authors.append(next(author.stripped_strings))

            # title = [x.get_text() for x in item.h4.children][1]
            paper.title = " ".join(item.h4.get_text().split())
            print(paper.title)

            for child in item.find_all("li"):
                field = child.strong.string.lower()
                value = child.span.string or ""
                if "tl;dr" in field:
                    paper.tldr = _split_and_rejoin(value)
                elif "keywords" in field:
                    paper.keywords = [s.strip() for s in value.split(",")]
                    paper.keywords = [_split_and_rejoin(kw) for kw in paper.keywords]
                elif "abstract" in field:
                    paper.abstract = value
                elif "pdf" in field:
                    paper.pdf_url = "https://openreview.net" + child.span.a["href"]
                elif "code" in field:
                    paper.code_url = value

            papers.append(paper)

    count = 0
    with open("csv/iclr2020-reprlearning.csv", "w") as fo:
        csv_writer = csv.writer(fo, delimiter="|")
        for paper in papers:
            if any(
                (s in paper.title.lower() or s in "".join(paper.keywords).lower())
                for s in [
                    "representation learning",
                    "learning representation",
                    "multiview",
                    "disentangle",
                    "contrastive",
                ]
            ):
                csv_writer.writerow(
                    [
                        paper.title,
                        "\n".join(paper.authors),
                        "\n".join(paper.keywords).lower(),
                        paper.tldr.lower(),
                        paper.pdf_url,
                        paper.code_url,
                    ]
                )
                count += 1

    print(count)
