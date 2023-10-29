import os
import pathlib

import openai

def set_apikey_from_file(file_path):
    with open(file_path, "r") as f:
        key = f.read().strip()
        os.environ["OPENAI_API_KEY"] = key

    openai.api_key = os.environ["OPENAI_API_KEY"]
    
        