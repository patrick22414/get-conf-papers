import re
from dataclasses import dataclass, field
from typing import List, NamedTuple

from bs4 import BeautifulSoup
import csv


RE_INST = re.compile(r"\((.*)\)", re.DOTALL)


@dataclass
class Paper:
    title: str = ""
    authors: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    TLDR: str = ""
    abstract: str = ""

html_files = ['iclr2020-oral.html','iclr2020-poster.html','iclr2020-spotlight.html']

if __name__ == "__main__":
    
    for html_file in html_files:    
        with open(html_file, "r") as html:
            soup = BeautifulSoup(html, "html.parser")

        papers = []

        for item in soup.find_all("li"):
            paper = Paper()

            if item.h4 is None: continue

            for result in item.find_all('div', 'note-authors'):
                authors = [x.string or x.get_text() for x in result.children]
                paper.authors = [x for x in authors if ',' not in x]

            title = [x.string or x.get_text() for x in item.h4.children][1]
            paper.title = " ".join(title.split())
            for child in item.find_all('li'):
                field = child.strong.string.lower()
                value = child.span.string
                if 'tl;dr' in field:
                    paper.TLDR = value
                elif 'keywords' in field:
                    paper.keywords = value.split(', ')
                elif 'abstract' in field:
                    paper.abstract = value



            # for i, line in enumerate(contents):
            #     print(f"{i} {line}")

            # import ipdb; ipdb.set_trace()
            
            # paper.title = " ".join(contents[1].split())
            # if not paper.title:
            #     print("Wrong with", p)
            #     exit()

            # authors_and_insts = [s.strip() for s in contents[3].split("·")]
            # for s in authors_and_insts:
            #     res = RE_INST.search(s)
            #     if res:
            #         author = " ".join(s[: res.start()].split())
            #         inst = " ".join(res.group(1).split())

            #         paper.authors.append(author)
            #         paper.insts.append(inst)
            #     else:
            #         print("Cannot match", repr(s))
            #         exit()

            papers.append(paper)

        # for paper in papers:
        #     if "representation" in paper.title.lower():
        #         print(paper.title)

        with open(html_file.replace('html','csv'), "w") as fo:
            csv_writer = csv.writer(fo)
            for paper in papers:
                csv_writer.writerow(
                    [paper.title, "\n".join(paper.authors), "\n".join(paper.keywords), paper.TLDR]
                )
