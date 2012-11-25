# script used to generate an edge list representation of log-graph and write it into a file.
nList = db(db.nodes.id>0).select(db.nodes.id,db.nodes.uid).as_list()
nodes = {}
for n in nList:
	nodes[n['uid']] = n['id'] - 1

print 'node uid to id mapping developed.. '

eList = db(db.edges.id>0).select(db.edges.node1,db.edges.node2).as_list()
edges = []
for e in eList:
	if e['node1'] != e['node2']:
		edges.append(tuple(sorted([nodes[e['node1']], nodes[e['node2']]])))
edges = list(set(edges))
edges.sort()

fw = open('D:\\web2py\\applications\\analytics\\static\\edgew.txt','w')
for i in range(len(edges)):
	fw.write(str(edges[i][0]) + ' ' + str(edges[i][1]) + '\n')
fw.close()
print 'done!'