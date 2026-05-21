from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import re, json
root=Path('/mnt/data/fidenta_global_step6')
html_files=sorted(root.glob('*.html'))
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.imgs=[]; self.title=''; self.meta_desc=''; self.ids=set(); self._title=False; self.forms=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if 'id' in d: self.ids.add(d['id'])
        if tag=='a' and 'href' in d: self.links.append(d['href'])
        if tag=='img' and 'src' in d: self.imgs.append(d['src'])
        if tag=='title': self._title=True
        if tag=='meta' and d.get('name')=='description': self.meta_desc=d.get('content','')
        if tag=='form': self.forms.append(d)
    def handle_endtag(self, tag):
        if tag=='title': self._title=False
    def handle_data(self,data):
        if self._title: self.title += data
parsers={}
errors=[]; warnings=[]
for f in html_files:
    p=P(); p.feed(f.read_text(encoding='utf-8')); parsers[f.name]=p
    if not p.title.strip(): errors.append(f'{f.name}: нет title')
    if not p.meta_desc.strip(): errors.append(f'{f.name}: нет meta description')
    if 'index.html' not in f.read_text(encoding='utf-8') and f.name!='index.html': warnings.append(f'{f.name}: нет ссылки на index.html?')
    for src in p.imgs:
        if src.startswith(('http://','https://','data:')): continue
        target=(f.parent/src).resolve()
        if not target.exists(): errors.append(f'{f.name}: битое изображение {src}')
    for href in p.links:
        if href.startswith(('http://','https://','mailto:','tel:')): continue
        if href.startswith('#'):
            aid=href[1:]
            if aid and aid not in p.ids: errors.append(f'{f.name}: битый якорь {href}')
            continue
        url=href.split('#',1)[0]
        anchor=href.split('#',1)[1] if '#' in href else ''
        if not url: continue
        target=(f.parent/url).resolve()
        if not target.exists(): errors.append(f'{f.name}: битая ссылка {href}')
        elif anchor:
            name=Path(url).name
            if name in parsers and anchor not in parsers[name].ids: errors.append(f'{f.name}: битый якорь {href}')
# second pass external anchors in files not parsed earlier
for f in html_files:
    for href in parsers[f.name].links:
        if href.startswith(('http://','https://','mailto:','tel:','#')) or '#' not in href: continue
        url,anchor=href.split('#',1)
        target=(f.parent/url).resolve()
        if target.exists() and target.suffix=='.html':
            p=parsers.get(target.name)
            if p and anchor and anchor not in p.ids:
                errors.append(f'{f.name}: битый якорь {href}')
# nav/logo check
for f in html_files:
    text=f.read_text(encoding='utf-8')
    if 'class="brand' in text and 'href="./index.html"' not in text and f.name!='index.html': warnings.append(f'{f.name}: проверь href логотипа')
    if 'privacy.html' not in text and f.name not in ['privacy.html']:
        warnings.append(f'{f.name}: нет ссылки на privacy.html')
    if 'terms.html' not in text and f.name not in ['terms.html']:
        warnings.append(f'{f.name}: нет ссылки на terms.html')
    if 'consent.html' not in text and f.name not in ['consent.html']:
        warnings.append(f'{f.name}: нет ссылки на consent.html')
report=[]
report.append('FIDENTA GLOBAL STEP 6 — FINAL LOCAL CHECK')
report.append('')
report.append(f'HTML pages: {len(html_files)}')
for name,p in parsers.items():
    report.append(f'- {name}: title="{p.title.strip()}"; meta={"yes" if p.meta_desc.strip() else "no"}; links={len(p.links)}; images={len(p.imgs)}')
report.append('')
report.append('Internal link check: ' + ('OK, broken links not found' if not errors else 'ISSUES'))
if errors:
    report += ['Errors:'] + ['- '+e for e in sorted(set(errors))]
report.append('')
report.append('Warnings / notes:')
report += ['- '+w for w in sorted(set(warnings))] if warnings else ['- No warnings']
report.append('')
report.append('Publication structure: index.html, investors.html, objects.html, object-detail.html, account.html, privacy.html, terms.html, consent.html, 404.html, styles.css, app.js, .nojekyll.')
report.append('Repository was not changed. This archive is intended for manual upload/replacement in GitHub Pages root.')
(root/'SITE_CHECK_STEP6.txt').write_text('\n'.join(report),encoding='utf-8')
print('\n'.join(report))
print('\nERROR_COUNT',len(set(errors)))
