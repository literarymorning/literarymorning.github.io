# 오늘 호 판단에 필요한 것만 요약해 보여 준다: 오늘 호 유무, 다음 호 번호, 최근 세 호 기사·링크, 최근 7호 해외 문학, 직전 호 달력, 오늘 실을 스페셜 요청, 쓰는 사람 최근 출처.
import json, os, subprocess
R = os.environ.get('R', '/home/claude/site')
today = subprocess.run(['date', '+%F'], env={**os.environ, 'TZ': 'Asia/Seoul'}, capture_output=True, text=True).stdout.strip()
idx = json.load(open(f'{R}/index.json'))
issues = {}
for m in sorted({i['date'][:7] for i in idx['issues'][:8]} | {today[:7]}):
    p = f'{R}/issues/{m}.json'
    if os.path.exists(p):
        issues.update(json.load(open(p))['issues'])
print('오늘', today, '| 이번 달 파일', '있음' if os.path.exists(f'{R}/issues/{today[:7]}.json') else '없음(새로 만든다)')
if any(i['date'] == today for i in idx['issues']) and today in issues:
    print('>>> 오늘 호가 이미 있음'); raise SystemExit
recent = [i for i in idx['issues'] if i['date'] != today]
print('직전 호 issue', recent[0]['issue'] if recent else 0, '→ 오늘 issue', (recent[0]['issue'] if recent else 0) + 1)
def urls(it):
    return ' '.join(x['url'] for x in it.get('sources', []) + it.get('links', []) if isinstance(x, dict) and x.get('url'))
for i in recent[:3]:
    iss = issues.get(i['date'])
    if not iss: continue
    print(f"== 최근 호 {i['date']} 제{iss['issue']}호")
    for s in iss['sections']:
        if s['id'] in ('past', 'established', 'writer', 'craft'): continue
        for it in s['items']:
            bk = [b.get('title', '') for b in it.get('books', [])] + [c.get('title', '') for c in it.get('candidates', [])]
            print(f" [{s['id']}] {it.get('title')} | {urls(it)}" + (f" | 책: {'/'.join(bk)}" if bk else ''))
print('== 최근 7호 해외 문학')
for i in recent[:7]:
    for s in issues.get(i['date'], {}).get('sections', []):
        if s['id'] == 'world':
            for it in s['items']:
                print(f" {i['date']} [{it.get('region')}] {it.get('title')} | {urls(it)}")
prev = issues.get(recent[0]['date']) if recent else None
cal = [c for c in (prev or {}).get('calendar', []) if c.get('date', '') >= today]
print('== 직전 호 calendar 중 오늘 이후', len(cal), '개')
for c in cal: print(' ', json.dumps(c, ensure_ascii=False))
rq = f'{R}/requests.json'
if os.path.exists(rq):
    w = json.load(open(rq)).get('writers', [])
    ok = [x for x in w if x.get('status') == 'pending' and x.get('notBefore', '') <= today]
    print('== 오늘 실을 수 있는 스페셜 요청', len(ok), '건')
    for x in sorted(ok, key=lambda x: x.get('requestedAt', ''))[:1]:
        print(' ', json.dumps(x, ensure_ascii=False))
cl = f'{R}/craft-log.json'
if os.path.exists(cl):
    c = json.load(open(cl))
    for side in ('국내', '해외'):
        f = [x for x in c.get('featured', []) if x.get('side') == side][-2:]
        print(f'== 쓰는 사람 {side}: 최근 outlet', [x['outlet'] for x in f])
