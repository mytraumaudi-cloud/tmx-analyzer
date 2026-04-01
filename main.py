from fastapi import FastAPI, UploadFile, File
import xml.etree.ElementTree as ET
import re

app = FastAPI()

def count_words(text):
    return len(re.findall(r"\b\w+\b", text))

@app.get("/")
def root():
    return {"message": "TMX Analyzer is running"}

@app.post("/analyze")
async def analyze_tmx(file: UploadFile = File(...)):
    content = await file.read()
    root = ET.fromstring(content)

    languages = set()
    source_lang = None
    tu_count = 0
    tu_word_counts = []

    header = root.find("header")
    if header is not None:
        source_lang = header.attrib.get("srclang")
        if source_lang:
            languages.add(source_lang)

    for tu in root.findall(".//tu"):
        tu_count += 1
        total_words = 0

        for tuv in tu.findall("tuv"):
            lang = tuv.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lang:
                languages.add(lang)

            seg = tuv.find("seg")
            if seg is not None and seg.text:
                total_words += count_words(seg.text)

        tu_word_counts.append(total_words)

    return {
        "source_language": source_lang,
        "languages": list(languages),
        "translation_unit_count": tu_count,
        "word_counts_per_tu": tu_word_counts
    }