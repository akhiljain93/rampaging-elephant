### required 
def error(): return dict()

# Controllers for index.html, dashboard.html, motion.html
def index(): 
  redirect(URL('dashboard',' '))
  return dict()
    
def dashboard(): 
  redirect(URL('dashboard',' '))
  return dict()

def motion():
  return dict()

# Fetches the data from database to create the Network graph
def graph():
  data = {'nodes':[], 'links':[]}
  n = db(db.nodes.id>0).select(orderby=db.nodes.id)
  nodes = {}
  for N in n:
    nodes[N.uid] = N.id-1
    data['nodes'].append({'name': str(N.uid)+', '+N.location, 'group': N.clusterid})
  e = db.executesql('select node1, node2, totalv from edges;')
  for E in e:
    data['links'].append({'source': nodes[E[0]], 'target': nodes[E[1]], 'value': E[2]})
  return dict(data=data)

# To update the database: Downloads the log-comm file and Updates the database 
def update():
  import sys
  sys.path.append('D:\\web2py\\applications\\analytics\\private')
  while(True):
    try:
      f = open("D:\\web2py\\applications\\analytics\\databases\\readComms.txt")
      readf = int(f.read())+1
      f.close()
    except:
      readf = 0
    s = str(readf)
    if readf < 10:
      s = '0'+str(readf)
    print "Trying to download comm."+s+"..."
    import os
    out = os.system('wget http://www.cse.iitd.ernet.in/act4d/csp301/log-comm.'+s+'.out -O D:\\web2py\\applications\\analytics\\databases\\log-comm\\log-comm.'+s+'.out')
    print out
    if out == 0:
      out = os.system('D:\\web2py\\web2py.exe -S analytics -M -R D:\\web2py\\applications\\analytics\\private\\readCommIntoCommDB.py')
    else:
      os.system('rm D:\\web2py\\applications\\analytics\\databases\\log-comm\\log-comm.'+s+'.out')
      break
  return dict()

