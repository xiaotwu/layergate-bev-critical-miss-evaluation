"""Read-only public-release integrity/structure checks, no model execution."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'provenance/PUBLIC_RELEASE_MANIFEST.json').read_text(encoding='utf-8'))
records=manifest['files']
assert len({r['path'] for r in records})==len(records)
for r in records:
    p=ROOT/r['path'];assert p.is_file() and not p.is_symlink()
    assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    assert p.stat().st_size<20*1024**2
    if p.suffix in {'.json','.md','.py','.csv','.tex','.bib','.cff','.yml'}:
        text=p.read_text(encoding='utf-8-sig')
        assert not re.search(r'[A-Za-z]:[\\/](?:Users|home)[\\/]|/home/[A-Za-z0-9_]+/',text),r['path']
        assert not re.search(r'gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',text),r['path']
    if p.suffix=='.json':json.loads(p.read_text(encoding='utf-8-sig'))
assert sha(ROOT/'paper/critical-miss-evaluation.pdf')=='4bf6837b1223024e2c7cc509015dfe80fb476d487e141be74f0432ca5953b715'
assert sha(ROOT/'paper/latex/main.tex')=='f0e19eedf24b9c424537ab8e47072f63ae739969bd43d13605bc50b73fbcb80a'
assert sha(ROOT/'paper/latex/references.bib')=='664b580977e311bbc41581a4e179295abac1991c16700b996b56010960eb0343'
source=json.loads((ROOT/'provenance/SOURCE_COPY_RECORD.json').read_text(encoding='utf-8'))
for r in source['source_files']:assert sha(ROOT/r['path'])==r['public_sha256'],r['path']
for p in ROOT.rglob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if target.startswith(('http:','https:','#','mailto:')):continue
        target=target.split('#')[0]
        assert (p.parent/target).exists(),(str(p.relative_to(ROOT)),target)
print(json.dumps({'status':'PUBLIC_RELEASE_INTEGRITY_AND_LINKS_PASS','files':len(records),'source_copies':len(source['source_files']),
                  'scientific_execution':0,'paper_sha256':sha(ROOT/'paper/critical-miss-evaluation.pdf')}))
