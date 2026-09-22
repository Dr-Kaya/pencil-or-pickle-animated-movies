"""Publish the revised movies unchanged, with captions and an offline download."""
from pathlib import Path
import sys,shutil,zipfile,json,hashlib,re
source=Path(__file__).resolve().parents[1]
target=Path(sys.argv[1] if len(sys.argv)>1 else '_site'); target.mkdir(parents=True,exist_ok=True)
for name in ['index.html','README.md','movies.json']:shutil.copy2(source/name,target/name)
shutil.copy2(source/'favicon.svg',target/'favicon.svg')
for archive in sorted((source/'assets').glob('*.zip')):
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            p=Path(name)
            assert not p.is_absolute() and '..' not in p.parts and p.parts[0]=='media',name
        z.extractall(target)
movies=json.loads((source/'movies.json').read_text())
assert len(movies)==6 and len(list((target/'media').glob('*.mp4')))==6
for movie in movies:
    assert hashlib.sha256((target/'media'/movie['file']).read_bytes()).hexdigest()==movie['sha256']
bundle=target/'Pencil_or_Pickle_animated_movies.zip'
with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    offline=(target/'index.html').read_text().replace('../favicon.svg','favicon.svg')
    offline=re.sub(r'<a class="all-movies"[^>]*>.*?</a>','',offline)
    z.writestr('index.html',offline)
    z.write(target/'favicon.svg','favicon.svg')
    z.write(target/'README.md','README.md')
    for p in sorted((target/'media').iterdir()):z.write(p,'media/'+p.name)
for ref in re.findall(r'(?:href|src)="([^"]+)"',(target/'index.html').read_text()):
    if not ref.startswith(('https:','#')):assert (target/ref).exists(),ref
print('Ready: six byte-identical revised movies, captions, posters, and the offline bundle.')
