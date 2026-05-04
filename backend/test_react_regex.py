import re
p = re.compile(r'(?<![A-Za-z0-9])React(?![A-Za-z0-9])', re.IGNORECASE)
tests = [
    'Few-shot、CoT、ReAct 等',
    '熟悉 React 框架',
    'React.js 前端开发',
    'ReAct pattern',
]
for t in tests:
    m = p.search(t)
    print(f'{t!r} => {"match" if m else "no match"}')
