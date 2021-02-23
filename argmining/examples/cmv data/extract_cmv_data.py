from pathlib import Path
import xml.etree.ElementTree as ET
import collections
from bs4 import BeautifulSoup as bs
import lxml
import sys

v2_path = Path.cwd() / 'v2.0'


def format_text(text: str, label):
    temp = text.strip().replace('&#8710;', '').replace('\u2206', '').replace('\u2015', '').replace('\u0394',"")
    return f"{temp}\t{label}\n"


with open(str(Path.cwd().parent / "data" / "train.tsv"), "w") as train_file:
    for dir in ['negative']:
        path = v2_path / dir
        for xml_file in path.glob("0.xml"):
            print(xml_file)
            # tree = ET.parse(str(xml_path))
            # root = tree.getroot()
            # for child in root:
            #     print(child)

            premises = []
            claims = []
            # Read the XML file
            with open(str(xml_file), "r") as file:
                # Read each line in the file, readlines() returns a list of lines
                content = file.readlines()
                # Combine the lines in the list into a string
                content = "".join(content)
                soup = bs(content, "xml")
                premise_tags = soup.find_all("premise")
                claim_tags = soup.find_all("claim")
                premises = [format_text(pr.get_text().strip(), 2) for pr in premise_tags]
                claims = [format_text(cl.get_text(), 1) for cl in claim_tags]

                non_args_1 = soup.find("thread").get_text().split("\n")
                non_args_2 = list(filter(lambda a: len(a) > 0, non_args_1))
                non_args = [format_text(na, 0) for na in non_args_2]
                print(non_args)
            train_file.writelines(premises)
            train_file.writelines(claims)
            train_file.writelines(non_args)
