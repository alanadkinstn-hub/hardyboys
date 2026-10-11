import re, json
W = open('/workspace/hardyboys/src/List_of_Hardy_Boys_books.wiki', encoding='utf-8').read()
SM = open('/workspace/hardyboys/src/supermystery.wiki', encoding='utf-8').read()

def clean(t):
    t = re.sub(r'\{\{refn\|.*?\}\}(?=\s*$|\s*\|\||\s*\()', '', t)
    t = re.sub(r'\{\{refn[^}]*\}\}', '', t)
    t = re.sub(r'<ref[^>]*/>|<ref[^>]*>.*?</ref>', '', t)
    t = re.sub(r'\{\{Sort\|[^|]*\|(.*?)\}\}', r'\1', t)
    t = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', t)
    t = t.replace("''", '').replace('’', "'").replace('‘', "'").strip()
    return t

def section(text, start, end=None):
    i = text.index(start); j = text.index(end, i) if end else len(text)
    return text[i:j]

def parse_table(sec):
    """rows: list of (num, [cells])"""
    rows = []
    for block in sec.split('|-')[1:]:
        lines = [l for l in block.split('\n') if l.strip() and not l.startswith('|}')]
        if not lines: continue
        m = re.match(r'!\s*(\d+)\s*$', lines[0].strip())
        if not m: continue
        cells = [l[1:].strip() for l in lines[1:] if l.startswith('|')]
        rows.append((int(m.group(1)), cells))
    return rows

def years_in(cells):
    out = []
    for c in cells:
        c2 = re.sub(r'rowspan="?\d+"?\|?', '', c)
        m = re.search(r'\{\{Start date\|(\d{4})', c2) or re.match(r'^\s*(?:[A-Za-z]+\s+)?(?:\d{1,2},\s*)?(\d{4})\s*$', c2) or re.search(r'Date table sorting\|(\d{4})\|(\w+)', c2)
        out.append(m.group(1) if m else None)
    return out

series = []
def add(key, name, short, publisher, note, books, group='Main'):
    series.append(dict(key=key, name=name, short=short, publisher=publisher, note=note, group=group, books=books))

# --- G&D canon 1-58
gd = section(W, '===Grosset & Dunlap===', '===Simon & Schuster===')
books = []
for n, cells in parse_table(gd):
    title = clean(cells[0]); ys = years_in(cells[1:])
    pub = ys[0]; rev = next((y for y in ys[1:] if y), None) if n <= 38 else None
    b = dict(n=n, t=title, y=int(pub))
    if n <= 38: b['ry'] = int(rev)
    books.append(b)
add('gd', 'The Hardy Boys Mystery Stories (Grosset & Dunlap)', 'Original Series #1–58', 'Grosset & Dunlap, 1927–1979',
    'The "canon." Volumes 1–38 exist in both Original Text (OT) and Revised Text (RT); revisions ran 1959–1973. Year shown is first publication; "Rev." is the revised-text year. Volumes 39–58 were written in the revised era and exist in one text only.', books)

# --- digests 59-190
dig = section(W, '====Wanderer editions====', '===\'\'Nancy Drew and the Hardy Boys: Be a Detective')
books = []
for sub, imprint in [('====Wanderer editions====', 'Wanderer'), ('====Minstrel editions====', 'Minstrel'), ('===Aladdin editions===', 'Aladdin')]:
    pass
def imprint_for(n): return 'Wanderer' if n <= 85 else ('Minstrel' if n <= 170 else 'Aladdin')
for n, cells in parse_table(dig):
    books.append(dict(n=n, t=clean(cells[0]), y=int(years_in(cells[1:2])[0]), imp=imprint_for(n)))
for b in books:
    if b['n'] == 68: b['alt'] = 'Retitled Deadly Chase (1987)'
    if b['n'] == 85: b['alt'] = 'Originally advertised as Mystery of the Space Shuttle'
    if b['n'] == 150: b['alt'] = 'Originally written for the Casefiles'
add('digest', 'The Hardy Boys Mystery Stories (Simon & Schuster digests)', 'Digests #59–190', 'Wanderer 1979–85 · Minstrel 1987–2001 · Aladdin 2002–05',
    'Continuation of the main series in digest-size format. #59–85 Wanderer, #86–170 Minstrel, #171–190 Aladdin. Grosset & Dunlap reprinted #59–66 in 2005 (out of print 2013).', books)

# --- casefiles
cf = section(W, "==''The Hardy Boys Casefiles Series''", "===''Nancy Drew and Hardy Boys Super Mystery''")
books = []
for n, cells in parse_table(cf):
    d = cells[1].strip(); m = re.match(r'(\w+)\s+(\d{4})', d)
    books.append(dict(n=n, t=clean(cells[0]), y=int(m.group(2)), m=m.group(1)))
add('casefiles', 'The Hardy Boys Casefiles', 'Casefiles #1–127', 'Archway (Simon & Schuster), 1987–1998',
    'Mass-market paperbacks for older readers. Unpublished: #128 Explosive Force; #130 The Crisscross Crime became digest #150.', books)

# --- Supermystery '88
books = []
for n, cells in parse_table(section(SM, '==Series titles==', '==See also==')):
    m = re.search(r'Date table sorting\|(\d{4})\|(\w+)', cells[1])
    books.append(dict(n=n, t=clean(cells[0]), y=int(m.group(1)), m=m.group(2)))
add('sm88', 'A Nancy Drew & Hardy Boys SuperMystery', 'SuperMystery #1–36', 'Archway (Simon & Schuster), 1988–1998',
    'Crossover series in the Casefiles / Nancy Drew Files continuity (often called "SuperMystery \'88").', books, 'Spinoffs')

# --- Ultra Thriller
add('ultra', 'Hardy Boys & Tom Swift Ultra Thriller', 'Ultra Thriller #1–2', 'Archway, 1992–1993', 'Both written by Bill McKay.',
    [dict(n=1, t='Time Bomb'), dict(n=2, t='The Alien Factor')], 'Spinoffs')

# --- Be a Detective
bad = section(W, "===''Nancy Drew and the Hardy Boys: Be a Detective", "==''The Hardy Boys Casefiles")
titles = [clean(l[1:]) for l in bad.split('\n') if l.startswith('# ')]
add('beadet', 'Nancy Drew & the Hardy Boys: Be a Detective Mystery Stories', 'Be a Detective #1–6', '1984–1985',
    'Choose-your-path books.', [dict(n=i+1, t=t) for i, t in enumerate(titles)], 'Spinoffs')

# --- Clues Brothers
cb = section(W, "==''The Clues Brothers''", "==''The Hardy Boys: Undercover Brothers''")
titles = [clean(l[1:]) for l in cb.split('\n') if l.startswith('# ')]
add('clues', 'The Hardy Boys: The Clues Brothers', 'Clues Brothers #1–17', 'Minstrel, 1997–2000',
    'For younger readers; Frank and Joe as grade-schoolers.', [dict(n=i+1, t=t) for i, t in enumerate(titles)], 'Younger readers')

# --- Undercover Brothers
ub = section(W, "==''The Hardy Boys: Undercover Brothers''", '===Super Mysteries===')
books = []; yr = None
for l in ub.split('\n'):
    m = re.match(r":'''(\d{4})'''", l)
    if m: yr = int(m.group(1)); continue
    m = re.match(r':(\d+)\.\s+(.*)', l)
    if m:
        n = int(m.group(1))
        if n == 40: continue  # cancelled before publication
        t = m.group(2)
        t = re.sub(r'\s*-\s*last book.*$', '', t)
        t = re.sub(r"\s*\((?:Murder House|Double Trouble|Deathstalker)[^)]*\)\s*$", '', t)
        t = re.sub(r"\s*\[Galaxy X trilogy\]", '', t)
        t = re.sub(r"\s*\(\[\[[^\]]*trilogy\]\](?:<ref.*?</ref>)?\)", '', t)
        t = clean(t); t = re.sub(r'\s*\(.*$', '', t)
        books.append(dict(n=n, t=t, y=yr))
add('ub', 'The Hardy Boys: Undercover Brothers', 'Undercover Brothers #1–39', 'Aladdin, 2005–2012',
    'First-person A.T.A.C. series that replaced the digests. (#40 was cancelled before publication.)', books, 'Modern')

# --- UB Super Mysteries
ubs = section(W, '===Super Mysteries===', "===''Nancy Drew and the Hardy Boys Super Mystery'' Series (2007")
books = []
for i, l in enumerate([l for l in ubs.split('\n') if l.startswith('# ')]):
    m = re.match(r'#\s*(.*?)\s*-\s*(\d{4})', re.sub(r'<ref.*?</ref>', '', l))
    t = clean(m.group(1)); t = re.sub(r'\s*\(Special.*\)$', '', t)
    books.append(dict(n=i+1, t=t, y=int(m.group(2))))
add('ubsuper', 'Undercover Brothers Super Mysteries', 'UB Super Mystery #1–3', 'Aladdin, 2006–2008', '', books, 'Modern')

# --- ND & HB Super Mystery '07
s7 = section(W, "===''Nancy Drew and the Hardy Boys Super Mystery'' Series (2007", "===''The Hardy Boys: Undercover Brothers'' Graphic")
books = []
for i, l in enumerate([l for l in s7.split('\n') if l.startswith('# ')]):
    m = re.match(r'#\s*(.*?)\s*-\s*(\d{4})', l)
    books.append(dict(n=i+1, t=clean(m.group(1)), y=int(m.group(2))))
add('sm07', 'Nancy Drew and the Hardy Boys Super Mystery (2007)', 'Super Mystery \'07 #1–6', 'Aladdin, 2007–2012', 'Girl Detective / Undercover Brothers crossover.', books, 'Modern')

# --- Adventures
ad = section(W, "==''The Hardy Boys Adventures''", '===Trivia===')
books = []; last = None
for n, cells in parse_table(ad):
    y = None
    if len(cells) > 1:
        m = re.search(r'Start date\|(\d{4})', cells[1]) or re.search(r'(\d{4})', cells[1])
        y = int(m.group(1)) if m else None
    if y is None: y = last
    last = y
    books.append(dict(n=n, t=clean(cells[0]), y=y))
add('adv', 'Hardy Boys Adventures', 'Adventures #1–25', 'Aladdin, 2013–2023', 'Paperback, hardcover with dust jacket, and ebook.', books, 'Modern')

# --- Secret Files
sf = section(W, "==''The Hardy Boys Secret Files''", "===''The Hardy Boys Clue Book''")
books = []
for i, l in enumerate([l for l in sf.split('\n') if l.startswith('# ')]):
    m = re.search(r'\((?:\w+\s+)?(\d{4})\)', l)
    t = clean(re.sub(r'\s*\((?:\w+\s+)?\d{4}\)\s*$', '', l[1:]))
    books.append(dict(n=i+1, t=t, y=int(m.group(1)) if m else None))
add('secret', 'The Hardy Boys Secret Files', 'Secret Files #1–19', 'Aladdin, 2010–2015', 'Chapter books for younger readers.', books, 'Younger readers')

# --- Clue Book
cbk = section(W, "===''The Hardy Boys Clue Book''", "==''Nancy Drew and The Hardy Boys'' Dynamite")
books = []; last = None
for n, cells in parse_table(cbk):
    m = re.search(r'Start date\|(\d{4})', cells[1]) if len(cells) > 1 else None
    y = int(m.group(1)) if m else last; last = y
    books.append(dict(n=n, t=clean(cells[0]), y=y))
add('cluebook', 'The Hardy Boys Clue Book', 'Clue Book #1–17', 'Aladdin, 2016–2024', 'Continuation of the Secret Files.', books, 'Younger readers')

# --- Specials
sp = section(W, '==Specials==', '== Notes ==')
books = []
for i, l in enumerate([l for l in sp.split('\n') if l.startswith('* ')]):
    m = re.match(r'\*\s*(.*)\s*\((\d{4})\)', l)
    books.append(dict(n=i+1, t=clean(m.group(1)), y=int(m.group(2))))
add('specials', 'Specials & Handbooks', 'Specials', 'Various', 'The Detective Handbook (1959) is counted by many collectors as part of the G&D canon.', books, 'Spinoffs')

# --- validation
expect = {'gd':58,'digest':132,'casefiles':127,'sm88':36,'ultra':2,'beadet':6,'clues':17,'ub':39,'ubsuper':3,'sm07':6,'adv':25,'secret':19,'cluebook':17,'specials':6}
for s in series:
    ns = [b['n'] for b in s['books']]
    assert len(ns) == expect[s['key']], (s['key'], len(ns))
    assert ns == list(range(ns[0], ns[0]+len(ns))), s['key']
    for b in s['books']:
        assert b['t'] and '[' not in b['t'] and '{' not in b['t'] and '|' not in b['t'] and '<' not in b['t'], (s['key'], b)
# cross-check revision years vs hardyboysonline.net timeline
tl = {1959:[1,2],1961:[14],1962:[3,4,11],1963:[5],1964:[6,7,19],1965:[9,12,16],1966:[8,17,24,27,37],1967:[10,13],1968:[15,29,30],1969:[18,25,31,32],1970:[20,21,23,26,28],1971:[22,33,34],1972:[35,36],1973:[38]}
rev = {n:y for y,ns in tl.items() for n in ns}
gdb = {b['n']:b for b in series[0]['books']}
bad = [(n, gdb[n].get('ry'), rev.get(n)) for n in range(1,39) if gdb[n].get('ry') != rev.get(n)]
print('revision mismatches (#, wiki, hbo):', bad)
json.dump(series, open('/workspace/hardyboys/tools/data.json','w'), ensure_ascii=False, indent=0)
for s in series: print(s['key'], len(s['books']), s['books'][0]['t'], '...', s['books'][-1]['t'], s['books'][-1].get('y'))
# post-fixes (documented)
gdb[7]['q'] = 'Revised-text year: 1965 per Wikipedia and hardyboys.us; hardyboysonline.net lists 1964.'
sp = next(s for s in series if s['key']=='specials')
sp['books'][0]['ry'] = 1972; sp['books'][0]['q'] = 'Revised 1972 per hardyboys.us revision history.'
json.dump(series, open('/workspace/hardyboys/tools/data.json','w'), ensure_ascii=False, separators=(',',':'))
print('total titles', sum(len(s['books']) for s in series))
# --- ghostwriters (v1.7): Wikipedia "List of Hardy Boys books" G&D table, cross-checked vs hardyboys.us (src/hbos.html author tables)
HA = 'Harriet Adams'
GW = {1:'Leslie McFarlane',2:'Leslie McFarlane',3:'Leslie McFarlane',4:'Leslie McFarlane',5:'Leslie McFarlane',6:'Leslie McFarlane',7:'Leslie McFarlane',8:'Leslie McFarlane',9:'Leslie McFarlane',10:'Leslie McFarlane',11:'Leslie McFarlane',12:'Leslie McFarlane',13:'Leslie McFarlane',14:'Leslie McFarlane',15:'Leslie McFarlane',16:'Leslie McFarlane',
 17:'John Button',18:'John Button',19:'John Button',20:'John Button',21:'John Button',22:'Leslie McFarlane',23:'Leslie McFarlane',24:'Leslie McFarlane',25:HA,26:'Amy McFarlane',27:'George Waller, Jr.',28:'Andrew E. Svenson',29:'Andrew E. Svenson',30:'Andrew E. Svenson',
 31:'William Hallstead and William Dougherty',32:'Richard Cohen',33:'William Dougherty',34:'Charles S. Strong',35:'John Almquist',36:'John Almquist',37:'James Duncan Lawrence',38:'James Duncan Lawrence',39:'James Duncan Lawrence',40:'James Buechler',41:'James Buechler',42:'Alistair Hunter',43:HA,44:'David Grambs',45:'Andrew E. Svenson',
 46:'Tom Mulvey',47:'Jerrold Mundis',48:'Andrew E. Svenson',49:'Vincent Buranelli',50:'Andrew E. Svenson',51:'Vincent Buranelli',52:'Andrew E. Svenson',53:'Andrew E. Svenson',54:'Andrew E. Svenson',55:'Vincent Buranelli',56:'Vincent Buranelli',57:'Vincent Buranelli',58:'James Duncan Lawrence'}
RB = {1:HA,2:HA,3:'Alistair Hunter',4:'James Buechler',5:'Alistair Hunter',6:'David Grambs',7:'Andrew E. Svenson',8:'Anne Shultes, Andrew E. Svenson and Harriet Adams',9:'Tom Mulvey',10:'Tom Mulvey',11:'James Buechler',12:'David Grambs',13:'Tom Mulvey',14:'James Buechler',15:'Tom Mulvey',16:'James Duncan Lawrence',17:'James Duncan Lawrence',18:'Tom Mulvey',19:'James Duncan Lawrence',
 20:'Vincent Buranelli',21:'Richard Deming',22:'Vincent Buranelli',23:'Andrew E. Svenson',24:'David Grambs',25:'Priscilla Baker-Carr',26:'Priscilla Baker-Carr',27:'David Grambs',28:'Priscilla Baker-Carr',29:'David Grambs, June Dunn and Priscilla Baker-Carr',30:'Priscilla Baker-Carr',31:'Priscilla Baker-Carr',32:'Priscilla Baker-Carr',33:'Priscilla Baker-Carr',34:'Priscilla Baker-Carr',35:'Priscilla Baker-Carr',36:'Priscilla Baker-Carr',37:'Priscilla Baker-Carr',38:'Priscilla Baker-Carr'}
GQ = {12:"Wikipedia notes McFarlane's credit for this title is disputed (style differences).",
 17:'Wikipedia credits Leslie McFarlane and John Button (McFarlane credit disputed); hardyboys.us credits John Button.',
 27:'Wikipedia credits George Waller, Jr. and Harriet Adams; hardyboys.us credits George Waller Jr.',
 30:'Wikipedia credits Andrew E. Svenson and Harriet Adams; hardyboys.us credits Andrew Svenson.',
 31:'hardyboys.us credits Hallstead, Adams and Dougherty.',
 46:'Wikipedia credits Tom Mulvey, Harriet Adams and Grace Grote; hardyboys.us credits Tom Mulvey.',
 24:'Revised text: Wikipedia credits David Grambs; hardyboys.us credits Priscilla Baker-Carr.',
 29:'Revised text: hardyboys.us credits Grambs and Dunn.'}
d = json.load(open('/workspace/hardyboys/tools/data.json'))
for b in d[0]['books']:
    n = b['n']; b['gw'] = GW[n]
    if n in RB: b['rb'] = RB[n]
    if n in GQ: b['gq'] = GQ[n]
json.dump(d, open('/workspace/hardyboys/tools/data.json','w'), ensure_ascii=False, separators=(',',':'))
print('ghostwriters added', sum(1 for b in d[0]['books'] if b.get('gw')))
