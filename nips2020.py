import re
from dataclasses import dataclass, field
from typing import List, NamedTuple

from bs4 import BeautifulSoup
import csv

URL = "https://nips.cc/Conferences/2020/AcceptedPapersInitial"

RE_INST = re.compile(r"\((.*)\)", re.DOTALL)


@dataclass
class Paper:
    title: str = ""
    authors: List[str] = field(default_factory=list)
    insts: List[str] = field(default_factory=list)


if __name__ == "__main__":
    with open("nips2020.html", "r") as html:
        soup = BeautifulSoup(html, "html.parser")

    papers = []
    for p in soup.find_all("p")[2:]:
        paper = Paper()

        contents = [x.string or x.get_text() for x in p.children]
        paper.title = " ".join(contents[1].split())
        if not paper.title:
            print("Wrong with", p)
            exit()

        authors_and_insts = [s.strip() for s in contents[3].split("·")]
        for s in authors_and_insts:
            res = RE_INST.search(s)
            if res:
                author = " ".join(s[: res.start()].split())
                inst = " ".join(res.group(1).split())

                paper.authors.append(author)
                paper.insts.append(inst)
            else:
                print("Cannot match", repr(s))
                exit()

        papers.append(paper)

    count = 0
    with open("nips2020-reprlearning.csv", "w") as fo:
        csv_writer = csv.writer(fo)
        for paper in papers:
            if any(
                s in paper.title.lower()
                for s in ["represent", "multiview", "disentangl",]
            ):
                print(paper.title)
                csv_writer.writerow(
                    [paper.title, "\n".join(paper.authors), "\n".join(paper.insts)]
                )
                count += 1
    print(count)
