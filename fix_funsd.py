import requests, zipfile, io, json, os

GT = 'd:/work/new/ocr-benchmarks/ground_truth'

FUNSD_URL = 'https://guillaumejaume.github.io/FUNSD/dataset.zip'
print('Downloading FUNSD zip...')
r = requests.get(FUNSD_URL, timeout=120)
z = zipfile.ZipFile(io.BytesIO(r.content))

# Filter OUT __MACOSX metadata files
annotations = sorted([
    n for n in z.namelist()
    if 'testing_data/annotations/' in n and n.endswith('.json') and '__MACOSX' not in n
])

print(f'Found {len(annotations)} real annotation files')

for i, ann_path in enumerate(annotations[:5], 1):
    raw = z.read(ann_path)
    txt = raw.decode('utf-8', errors='ignore').strip()
    if txt.startswith('\ufeff'):
        txt = txt[1:]

    try:
        data = json.loads(txt)
        texts = [item['text'] for item in data.get('form', []) if item.get('text', '').strip()]
        out = os.path.join(GT, f'en_form_{i:03d}.txt')
        with open(out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(texts))
        print(f'OK en_form_{i:03d}.txt ({len(texts)} text segments)')
    except json.JSONDecodeError as e:
        print(f'FAIL {ann_path}: {e}')

z.close()
print('\nDone!')
