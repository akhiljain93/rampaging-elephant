# script used to generate an adjacency list and write it into a file. the id's as in db.nodes have been used rather than the discontinous id's in log-comm
nList = db(db.nodes.id>0).select(db.nodes.id,db.nodes.uid).as_list()
nodes = {}
for n in nList:
	nodes[n['uid']] = n['id']

print 'node uid to id mapping developed.. '

eList = db(db.edges.id>0).select(db.edges.node1,db.edges.node2).as_list()
adj = {}
en = 0
for e in range(len(eList)):
	eList[e] = tuple(sorted([nodes[eList[e]['node1']], nodes[eList[e]['node2']]]))

eList = set(eList)
for e in eList:
	if e[0] == e[1]:
		continue
	en += 1
	try:
		adj[e[0]].append(e[1])
	except KeyError:
		adj[e[0]] = [e[1]]
	try:
		adj[e[1]].append(e[0])
	except KeyError:
		adj[e[1]] = [e[0]]

fw = open('D:\\web2py\\applications\\analytics\\static\\adj.txt','w')
fw.write(str(len(nList))+' '+str(en)+'\n')
for k in adj:
	fw.write(' '.join([str(x) for x in adj[k]])+'\n')

fw.close()
print 'done!'