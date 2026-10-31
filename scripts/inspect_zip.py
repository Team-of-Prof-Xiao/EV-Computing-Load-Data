"""List the contents of a downloaded archive without extracting it, and print any README or licence text.

Usage: python3 -I scripts/inspect_zip.py path/to/archive.zip
Flags members with absolute paths or '..' components, which must not be extracted as they are.
"""
import sys
import zipfile
from collections import Counter
from pathlib import PurePosixPath

with zipfile.ZipFile(sys.argv[1]) as z:
    infos = z.infolist()
    total = sum(i.file_size for i in infos)
    print(f'members: {len(infos)}, uncompressed {total / 1e9:.2f} GB')
    unsafe = [i.filename for i in infos if i.filename.startswith('/') or '..' in PurePosixPath(i.filename).parts]
    print('unsafe paths:', unsafe[:5] or 'none')
    print('by extension:', Counter(PurePosixPath(i.filename).suffix.lower() for i in infos).most_common(10))
    tops = Counter(PurePosixPath(i.filename).parts[0] for i in infos)
    print('top-level entries:', tops.most_common(15))
    for i in sorted(infos, key=lambda i: i.file_size, reverse=True)[:8]:
        print(f'  {i.file_size / 1e6:9.1f} MB  {i.filename}')
    for i in infos:
        name = PurePosixPath(i.filename).name.lower()
        if any(k in name for k in ('readme', 'license', 'licence', 'metadata')) and i.file_size < 200_000:
            print(f'\n===== {i.filename}')
            print(z.read(i).decode('utf-8', errors='replace')[:6000])
