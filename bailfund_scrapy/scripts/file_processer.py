import os
import sys

from pathlib import Path
from pdfminer.high_level import extract_text

if len(sys.argv) < 2: sys.exit(1)

directory = Path(sys.argv[1])
if not directory.is_dir(): 
    print("Please add pdf directory as argument")
    sys.exit(1)

f = []

pathlist = directory.glob('*.pdf')

for path in pathlist:
    txt = extract_text(path)
    if "Bail" in txt:
        print(f"{path} contains bail information")
    else:
        print(f"Deleting {path}")
        os.remove(path)
