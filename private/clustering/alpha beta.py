nList = db(db.nodes.id>0).select(db.nodes.id,db.nodes.uid).as_list()
nodes = {}
for n in nList:
	nodes[n['uid']] = n['id']

eList = db(db.edges.id>0).select(db.edges.node1,db.edges.node2).as_list()
adj = {}
for e in eList:
	e = [nodes[e['node1']], nodes[e['node2']]]
	try:
		adj[e[0]].add(e[1])
	except KeyError:
		adj[e[0]] = set([e[1]])
	try:
		adj[e[1]].append(e[0])
	except KeyError:
		adj[e[1]] = set([e[0]])

print "got mr. adjler's List!"

def isab(C,a,b):
	n = len(C)
	if n == 0:
		return False
	bn = b*n
	an = a*n
	for v in C:
		if len(adj[v].intersection(C))-0.1*n < bn:
			return False
		if len(adj[v].difference(C))+0.1*n > an:
			return False
	return True

def calcab(C):
	n = len(C)
	a = 0
	b = n
	for v in C:
		bt = len(adj[v].intersection(C))
		at = len(adj[v].difference(C))
		if bt < b:
			b = bt
		if at > a:
			a = at
	return a/float(n),b/float(n)


a = 0.5
r = 0.4
b = 0.5*(1 + a)
print 'beta = ', b

clus = []

s = s2 = 2
was = True
thresh = 0
while s < 650:
	s2 += 1
	if not was:
		s2 += s/20
	was = False
	thresh2 = s2*(2*b - 1)
	if int(thresh2) != int(thresh) or int(r*s) != int(r*s2):
		thresh = thresh2
		s = s2
	else:
		continue
	print 'thresh =', thresh, 'started..'
	for c in range(1,2501):
		C = []
		tray = set([]).union(adj[c])
		for u in adj[c]:
			tray = tray.union(adj[u])
		tray.remove(c)
		for u in tray:
			if c != u and len(adj[u].intersection(adj[c])) >= thresh:
				C.append(u)
		n = len(C)
		if isab(C,a,b):
			clus.append(C)
			if not was:
				print 'yay!'
				was = True
	print 'size', s, 'completed'


def siz(s):
	thresh = s*(2*b - 1)
	print 'thresh =', thresh, 'started..'
	clus = []
	for c in range(1,2501):
		C = []
		tray = set([]).union(adj[c])
		for u in adj[c]:
			tray = tray.union(adj[u])
		tray.remove(c)
		for u in tray:
			if c != u and len(adj[u].intersection(adj[c])) >= thresh:
				C.append(u)
		n = len(C)
		if isab(C,a,b):
			clus.append(C)
			if not was:
				print 'yay!'
				was = True
	print 'size', s, 'completed'
	return clus

def chalbc(s):
	a = 0.3
	b = 0.7
	print 'beta = ', b
	clus = []
	thresh = 0.6
	for k in range(10000):
		C = set([])
		while len(C) < s:
			C.add(random.randint(1,2500))
		doit = True
		for v in range(1,2501):
			if v not in C and len(C.intersection(adj[v])) > len(C)*thresh:
				C.add(v)
				if len(C) >= 2*s:
					break
		if k % 100 == 0:
			print k
		if isab(C,a,b):
			clus.append(C)
			print 'pulleez!!'
	return clus