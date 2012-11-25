# script used to populate the db with the nodes and edges in log-graph.out
import fileinput

for line in fileinput.input(['D:\\web2py\\applications\\analytics\\private\\log-graph.out']):
	line = line.split()
	if line[1] == 'node':
		uid = int(line[2][:-1])
		location = line[3]
		db.nodes.insert(uid=uid, location=location)
	elif line[1] == 'edge':
		enodes = line[2].split("-")
		enodes = sorted([int(enodes[0]), int(enodes[1])])
		# try-except for uniqueness
		try:
			db.edges.insert(node1 = enodes[0], node2 = enodes[1])
		except:
			pass
db.commit()
