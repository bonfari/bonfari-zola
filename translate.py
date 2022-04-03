import glob
import os
import re
from pathlib import Path

import deepl
import markdown
from bs4 import BeautifulSoup
from markdownify import markdownify

translator = deepl.Translator(os.environ.get('DEEPL_API_KEY', '')) 

def find_and_replace_link(text):
    pattern = re.compile(r'\[([^][]+)\](\(((?:[^()]+|(?2))+)\))')
    reg_dict = {}
    for idx, match in enumerate(pattern.finditer(text)):
        _, _, url = match.groups()
        reg_dict[idx] = url
        text = text.replace(url, idx)
    return text, reg_dict

def get_translation(text):
    result = translator.translate_text(text, target_lang='EN-GB') 
    return result.text
    

for p in Path().rglob("./content/**/*.md"):
    if '.en.' not in str(p):
        # TODO: compare file last edit
        # TODO: add URL conversion
        text = p.read_text(encoding='latin-1', errors='ignore')
        text_parts = text.rsplit('+++', 1)
        html = markdown.markdown(text_parts[-1])
        soup = BeautifulSoup(html,features="html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        actual_texts = list(soup.stripped_strings)
        html = str(html)
        for text in actual_texts[:1]:
            if any([char.isalnum() for char in text.split()]):
                html = html.replace(text, get_translation(text), 1)
        text_total = "+++\n".join([text_parts[0], html])
        # text = find_and_replace_link(text_parts[-1])
        p_en = p.with_suffix('').with_suffix('.en.md')
        p_en.write_text(text_total, encoding='latin-1')
        break 
    # p.with_name(p.stem+".en"+p.suffix).write_text(text)
        
