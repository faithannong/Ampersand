import random
from pathlib import Path
import xml.etree.ElementTree as ET
import collections
from bs4 import BeautifulSoup as bs
import lxml
import sys


def format_text_bert(a, b, label):
    a_ = a.strip().replace('&#8710;', '').replace('\u2206', '').replace('\u2015', '').replace('\u0394', "")
    b_ = b.strip().replace('&#8710;', '').replace('\u2206', '').replace('\u2015', '').replace('\u0394', "")
    return f"{a_}\t{b_}\t{str(label)}\n"


def format_text_rst(a, b, label):
    a_ = a.strip().replace('&#8710;', '').replace('\u2206', '').replace('\u2015', '').replace('\u0394', "")
    b_ = b.strip().replace('&#8710;', '').replace('\u2206', '').replace('\u2015', '').replace('\u0394', "")
    return f"{a_} {b_}"


v2_path = Path.cwd() / 'v2.0'


def get_relation_pairs_rst():
    relations = get_relation_pairs(format_text_rst)
    dir_path = Path.cwd().parent / "rst_inputs"
    for i in range(len(relations)):
        entry = relations[i]
        file_path = dir_path / f"{i}.tsv"
        # file_path.touch()
        with open(str(file_path), "w") as f:
            f.write(entry)

def get_relation_pairs_rst_mirror_bert_inputs():
    dir_path = Path.cwd().parent.parent / "rst_classifier" / "data"
    with open(str(Path.cwd().parent / "data" / "rel_bert_input.tsv"), "r") as f:
        content = f.readlines()
        for i in range(len(content)):
            entry = content[i].split("\t")
            label = entry[-1].replace("\n", "")
            text = "\n".join(entry[:-1])
            file_path = dir_path / f"{i}_l{label}.txt"
            with open(str(file_path), "w") as f:
                f.write(text)


def get_relation_pairs_rst_mirror_bert_swap_pair_order():
    dir_path = Path.cwd().parent.parent / "rst_classifier" / "data"
    with open(str(Path.cwd().parent / "data" / "rel_bert_input.tsv"), "r", encoding='ISO-8859-1') as f:
        content = f.readlines()
        for i in range(len(content)):
            entry = content[i].split("\t")
            label = entry[-1].replace("\n", "")
            text = entry[1] + "\n" + entry[0]
            file_path = dir_path / f"{i}_l{label}.txt"
            with open(str(file_path), "w") as f:
                f.write(text)


def get_relation_pairs_bert():
    relations = get_relation_pairs(format_text_bert)
    with open(str(Path.cwd().parent / "data" / " rel_bert_input.tsv"), "w") as f:
        f.writelines(relations)


def get_relation_pairs(format_t):
    relations = []

    valid_b_count = 0
    no_rel_count = 0
    rel_count = 0
    random_no_rel_count = 0
    total_rel_count = 0
    premise_count = 0

    for dir in ['negative', 'positive']:
        path = v2_path / dir

        for xml_file in path.glob("*.xml"):
            if int(str(xml_file).split(".")[0]) >= 50:
                continue
            print(xml_file)
            # print(xml_file)
            # premises = []
            claims = []
            # Read the XML file
            with open(str(xml_file), "r") as file:
                # Read each line in the file, readlines() returns a list of lines
                content = file.readlines()
                # Combine the lines in the list into a string
                content = "".join(content)
                soup = bs(content, "xml")
                # premise_tags = soup.find_all("premise")
                tags = [soup.find_all("claim", {"rel": "agreement"}), soup.find_all("claim", {"rel": "rebuttal"}),
                        soup.find_all("claim", {"rel": "undercutter"})]

                # (sentence a, sentence b, label)

                all_claims = [(cl['id'] if cl.get("id") else "title", cl.get_text()) for cl in soup.find_all("claim")]
                rel_types = ['partial_attack', 'rebuttal_attack', 'attack', 'rebuttal', 'undercutter', 'agreement']

                for a in soup.find_all("claim"):
                    b_list = []
                    rel = a.get("rel")
                    if rel is not None:
                        rel_count += 1
                        b_id = a.get("ref")
                        a_text = a.get_text()
                        if b_id is not None:
                            valid_b_count += 1
                            if 'title' in b_id:
                                b_list = [soup.find('title').find('claim')]
                            elif '_' in b_id:
                                b_ids = b_id.split("_")
                                b_list = [soup.find(attrs={'id': id_i}) for id_i in b_ids]
                            else:
                                b_list = [soup.find(attrs={"id": b_id})]
                            if len(b_list) == 0:
                                print("b is None", b_id)
                            else:
                                for b in b_list:
                                    if b.name == "premise":
                                        # print("b is premise")
                                        # print(a)
                                        # print(b)
                                        # print()
                                        premise_count += 1
                                    relations.append(format_t(a.get_text(), b.get_text(), 1))
                                    total_rel_count += 1
                                    # print((a_text, b.get_text(), 1))
                    else:
                        # relations.append((a.get_text(), a['ref'], 0))
                        # print("not rel", a)
                        no_rel_count += 1

                    # find a random pairing with an unrelated claim - can be from the same post or a different one
                    rand = random.choice(all_claims)
                    while rand[0] in b_list:
                        # print("was the same: ", a['id'], rand[0], b_id)
                        rand = random.choice(all_claims)

                    relations.append(format_t(a.get_text(), rand[1], 0))
                    random_no_rel_count += 1

                # for x in relations:
                #     print(x)
                # print()

    print("valid b count", valid_b_count)
    print("rel count", rel_count)
    print("no rel count", no_rel_count)
    print("rand no rel count", random_no_rel_count)
    print("total rel count", total_rel_count)
    print("premise count", premise_count)
    print("all claims", len(all_claims))

    return relations

# get_relation_pairs_bert()
get_relation_pairs_rst_mirror_bert_swap_pair_order()