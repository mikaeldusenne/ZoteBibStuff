import xml.etree.ElementTree as ET
import logging
import os
import sys

logging.basicConfig(
    filename="result/log.txt",  # Output file
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S"  # Date format
)



namespace_map = {
    'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    'z': "http://www.zotero.org/namespaces/export#",
    'dc': "http://purl.org/dc/elements/1.1/",
    'dcterms': "http://purl.org/dc/terms/",
    'bib': "http://purl.org/net/biblio#",
}

def run(xml_data):
    root = ET.fromstring(xml_data)

    def extract_references(collection):
        return dict(
            title=collection.find("dc:title", namespace_map).text.strip(),
            refs= [
                resource.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource", "").strip()
                for resource in collection.findall("dcterms:hasPart", namespace_map)
                if "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource" in resource.attrib
            ]
        )

    collections = {ee: e["title"] for e in [extract_references(e) for e in root.findall("z:Collection", namespace_map)] for ee in e["refs"]}

    for article in root.findall("bib:Article", namespace_map):
        ref = article.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about")
        if ref in collections :
            subject_element = ET.Element("{http://purl.org/dc/elements/1.1/}subject")
            subject_element.text = collections[ref] # prout prout
            article.append(subject_element)
        else:
            logging.warning(f"""No collection for {ref} : {article.find("dc:title", namespace_map).text}""")

    modified_xml = ET.tostring(root, encoding="unicode")
    return modified_xml



if __name__ == "__main__":
    file_input = sys.argv[1] # "data/Systematic review.rdf"
    
    os.makedirs("./result", exist_ok=True)
    
    with open(file_input, encoding="utf-8") as f:
        xml_data = f.read()

    modified_xml = run(xml_data)
    
    with open("result/output.rdf", "w", encoding="utf-8") as f:
        f.write(modified_xml)
    
    print("Done.\nResults saved to ./results")
