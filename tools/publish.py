# /home/claude/today/meta.json 과 sections/*.json 을 합쳐 이달 호 파일과 index.json에 넣고, 여섯 데이터 파일 문법을 확인한다.
import json, os, glob, subprocess, datetime
R = os.environ.get('R', '/home/claude/site'); T = os.environ.get('T', '/home/claude/today')
meta = json.load(open(f'{T}/meta.json'))
order = ['writer', 'calls', 'results', 'past', 'established', 'craft', 'grants', 'books', 'columns', 'issues', 'world']
secs = [json.load(open(f)) for f in glob.glob(f'{T}/sections/*.json')]
secs = [s for s in secs if s.get('items')]
bad = [s['id'] for s in secs if s['id'] not in order]
assert not bad, f'모르는 꼭지 id: {bad}'
secs.sort(key=lambda s: order.index(s['id']))
ids = [s['id'] for s in secs]
assert len(ids) == len(set(ids)), f'꼭지 id 중복: {ids}'
assert not ('writer' in ids and 'craft' in ids), 'writer와 craft가 같은 날 실림'
wd = datetime.date.fromisoformat(meta['date']).isoweekday()
assert 'craft' not in ids or wd in (1, 3, 5), '쓰는 사람은 월·수·금에만 싣는다. sections/craft.json을 빼고 다시 실행'
iss = {k: meta[k] for k in ('date', 'issue', 'generatedAt', 'quote', 'headline', 'lede') if k in meta}
iss['sections'] = secs
iss['calendar'] = sorted(meta.get('calendar', []), key=lambda c: c['date'])[:20]
d = iss['date']; size = len(json.dumps(iss, ensure_ascii=False).encode())
assert size < 200_000, f'호 크기 {size}B가 200KB를 넘음'
mp = f'{R}/issues/{d[:7]}.json'
mf = json.load(open(mp)) if os.path.exists(mp) else {'month': d[:7], 'issues': {}}
mf['issues'][d] = iss
open(mp, 'w').write(json.dumps(mf, ensure_ascii=False))
ip = f'{R}/index.json'; idx = json.load(open(ip))
ent = {'date': d, 'issue': iss['issue'], 'headline': iss['headline']}
if 'writer' in ids:
    ent['special'] = '이 작가가 궁금하다 · ' + secs[0]['items'][0]['name']
idx['issues'] = [ent] + [x for x in idx['issues'] if x['date'] != d]
idx['updatedAt'] = iss['generatedAt']
open(ip, 'w').write(json.dumps(idx, ensure_ascii=False, indent=1) + '\n')
for f in ['index.json', mp[len(R)+1:], 'past-winners.json', 'established.json', 'requests.json', 'craft-log.json']:
    if os.path.exists(f'{R}/{f}'): json.load(open(f'{R}/{f}'))
print(f"ok 제{iss['issue']}호 {d} 꼭지 {ids} 크기 {size}B, 여섯 파일 문법 확인")
