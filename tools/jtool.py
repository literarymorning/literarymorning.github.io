# 사용법 (목록 파일의 항목 하나만 보거나 고친다. 파일 전체를 읽지 않기 위한 도구)
#   python3 tools/jtool.py get FILE LIST_KEY FIELD VALUE           # 그 항목만 출력
#   python3 tools/jtool.py set FILE LIST_KEY FIELD VALUE 'JSON'    # 그 항목에 JSON 필드를 덮어씀
#   python3 tools/jtool.py add FILE LIST_KEY FIELD VALUE 'JSON'    # 같은 항목이 없을 때만 JSON을 덧붙임 (FIELD를 - 로 주면 확인 없이 덧붙임)
# 예: get past-winners.json entries id 2024-무등일보-단편소설 / set requests.json writers name "케이티 기타무라" '{"status":"done"}'
import json, sys, os
R = os.environ.get('R', '/home/claude/site')
cmd, fname, lk, field, val = sys.argv[1:6]
p = f'{R}/{fname}'
d = json.load(open(p))
items = d[lk]
hit = [] if field == '-' else [x for x in items if str(x.get(field)) == val]
if cmd == 'get':
    print(json.dumps(hit, ensure_ascii=False, indent=1) if hit else '없음'); raise SystemExit
patch = json.loads(sys.argv[6])
if cmd == 'set':
    if not hit: sys.exit(f'{field}={val} 항목이 없음')
    hit[0].update(patch)
elif cmd == 'add':
    if hit: sys.exit(f'{field}={val} 항목이 이미 있음')
    items.append(patch)
s = json.dumps(d, ensure_ascii=False, indent=1)
open(p, 'w').write(s + ('\n' if fname != 'requests.json' else ''))
print('ok', cmd, fname, field, val)
