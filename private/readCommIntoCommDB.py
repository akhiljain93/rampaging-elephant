# script used to read log-comms into databases

# reading a file with the fileinput module is more efficient for large files
import fileinput
import re
import traceback
import time
import datetime
import gc

#index stuff into python dictionaries for faster access
edges = db(db.edges.id>0).select()
dic = {} 	# n1,n2 edge to edgeid mapping
cleds = {}	# edgeid to cledgeid mapping
loceds = {} # edgeid to locedgeid mapping
for i in range(len(edges)):
	dic[(edges[i]['node1'],edges[i]['node2'])] = edges[i]['id']
	cleds[edges[i]['id']] = edges[i]['cledgeid']
	loceds[edges[i]['id']] = edges[i]['locedgeid']
	if i % 10000 == 0:
		print i

def hourify(time):
	"""floor a given timestamp to an hour"""
	t = time/3600000*3600000 + 1800000
	if t < time:
		return t
	return t - 3600000

def dayfloor(time):
	"""floor a given timestamp to a day"""
	t = time/86400000*86400000 + 66600000
	if t < time:
		return t
	return t - 86400000

def weekfloor(time):
	"""floor a given timestamp to a week"""
	t = time/604800000*604800000 + 325800000
	if t < time:
		return t
	return t - 604800000

def read(f):
	"""read the file log-comm.(f).out"""
	s = str(f)
	if f < 10:
		s = '0'+str(f)
	try:
		# try-except block to rollback changes to db if an error occurs
		c = 0
		print "Trying comm."+s+"..."
		d = fileinput.input(['D:\\web2py\\applications\\analytics\\databases\\log-comm\\log-comm.'+s+'.out'])
		for line in d:
			#extract topic, time, edge, cledge, locedge
			topic = line.split(", ")
			time = line.split(": ")[0]
			if len(re.findall("\d+", time)) == 0:
				print '"' + line + '"<-- this is the one!'
			time = hourify(long(re.findall("\d+", time)[0]))
			edge = re.findall("\d+", topic[-2])
			edge = sorted([int(edge[0]), int(edge[1])])
			edge = dic[tuple(edge)]
			topic = topic[-1].strip()
			cledge = cleds[edge]
			locedge = loceds[edge]
			# update edges with total vol += 1
			db(db.edges.id==edge).update( totalv = db.edges.totalv + 1 )
			db(db.cledges.id==cledge).update( totalv = db.cledges.totalv + 1 )
			db(db.locedges.id==locedge).update( totalv = db.locedges.totalv + 1 )
			# update record if it exists, else insert
			r = db((db.chourwise.time==time)&(db.chourwise.topic==topic)&(db.chourwise.cledge==cledge)).select().first()
			if r:
				r.update_record(volume = r['volume'] + 1)
			else:
				db.chourwise.insert(topic=topic, time=time, cledge=cledge)
			r = db((db.lhourwise.time==time)&(db.lhourwise.topic==topic)&(db.lhourwise.locedge==locedge)).select().first()
			if r:
				r.update_record(volume = r['volume'] + 1)
			else:
				db.lhourwise.insert(topic=topic, time=time, locedge=locedge)
			c += 1
			# we want feedback, but not at the cost of time
			if c % 10000 == 0:
				print "\t",c
		print "finalising comm."+s,'!'
		db.commit()
	except Exception, exc:
		print 'could not complete, rolling back..'
		db.rollback()
		try:
			d.close()
		except:
			pass
		raise exc

def croundhour():
	"""this function will be used to round the entries in chourwise, more than 10 days old, into the cdaywise"""
	# get the day of the latest entry and go 10 days back
	oldtime = dayfloor(db(db.chourwise.id>0).select(db.chourwise.time.max().with_alias('time'),limitby=(0,1)).first().time)
	oldtime -= 10*86400000
	try:
		f = open("D:\\web2py\\applications\\analytics\\databases\\croundhour.data")
		# this file stores the id to which we have already read hourwise
		readid = int(f.read())
		f.close()
	except:
		readid = 0
	old = db(db.chourwise.id>readid).select()
	i = 0
	for rec in old:
		topic = rec.topic
		time = dayfloor(rec.time)
		volume = rec.volume
		cledge = rec.cledge
		r = db((db.cdaywise.time==time)&(db.cdaywise.topic==topic)&(db.cdaywise.cledge==cledge)).select().first()
		if r:
			r.update_record(volume = r.volume + volume)
		else:
			db.cdaywise.insert(topic=topic, time=time, cledge=cledge, volume=volume)
		#delete the record if its too old
		if rec.time < oldtime:
			rec.delete_record()
		i += 1
		if i % 10000 == 0:
			print "\t",i
	db(db.chourwise.time < oldtime).delete()
	db.commit()
	fw = open("D:\\web2py\\applications\\analytics\\databases\\croundhour.data", 'w')
	fw.write(str(old[-1].id))
	fw.close()

def lroundhour():
	"""this function will be used to round the entries in lhourwise, more than 10 days old, into the ldaywise"""
	# get the day of the latest entry and go 10 days back
	oldtime = dayfloor(db(db.lhourwise.id>0).select(db.lhourwise.time.max().with_alias('time'),limitby=(0,1)).first().time)
	oldtime -= 10*86400000
	try:
		f = open("D:\\web2py\\applications\\analytics\\databases\\lroundhour.data")
		# this file stores the id to which we have already read hourwise
		readid = int(f.read())
		f.close()
	except:
		readid = 0
	old = db(db.lhourwise.id>readid).select()
	i = 0
	for rec in old:
		topic = rec.topic
		time = dayfloor(rec.time)
		volume = rec.volume
		locedge = rec.locedge
		r = db((db.ldaywise.time==time)&(db.ldaywise.topic==topic)&(db.ldaywise.locedge==locedge)).select().first()
		if r:
			r.update_record(volume = r.volume + volume)
		else:
			db.ldaywise.insert(topic=topic, time=time, locedge=locedge, volume=volume)
		#delete the record if its too old
		if rec.time < oldtime:
			rec.delete_record()
		i += 1
		if i % 10000 == 0:
			print "\t",i
	db(db.lhourwise.time < oldtime).delete()
	db.commit()
	fw = open("D:\\web2py\\applications\\analytics\\databases\\lroundhour.data", 'w')
	fw.write(str(old[-1].id))
	fw.close()


def croundday():
	"""this function will be used to round the entries in cdaywise, more than 9 months old, into the cweekwise"""
	# get the week of the latest entry and go 9 months back
	oldtime = weekfloor(db(db.cdaywise.id>0).select(db.cdaywise.time.max().with_alias('time'),limitby=(0,1)).first().time)
	oldtime -= 9*30.5*86400000
	try:
		f = open("D:\\web2py\\applications\\analytics\\databases\\croundday.data")
		# this file stores the id to which we have already read daywise
		readid = int(f.read())
		f.close()
	except:
		readid = 0
	old = db(db.cdaywise.id>readid).select()
	i = 0
	for rec in old:
		topic = rec.topic
		time = weekfloor(rec.time)
		volume = rec.volume
		cledge = rec.cledge
		r = db((db.cweekwise.time==time)&(db.cweekwise.topic==topic)&(db.cweekwise.cledge==cledge)).select().first()
		if r:	
			r.update_record(volume = r.volume + volume)
		else:
			db.cweekwise.insert(topic=topic, time=time, cledge=cledge, volume=volume)
		#delete the record if its too old
		if rec.time < oldtime:
			rec.delete_record()
		i += 1
		if i % 10000 == 0:
			print "\t",i
	db(db.cdaywise.time < oldtime).delete()
	db.commit()
	fw = open("D:\\web2py\\applications\\analytics\\databases\\croundday.data", 'w')
	fw.write(str(old[-1].id))
	fw.close()


def lroundday():
	"""this function will be used to round the entries in ldaywise, more than 9 months old, into the lweekwise"""
	# get the week of the latest entry and go 9 months back
	oldtime = weekfloor(db(db.ldaywise.id>0).select(db.ldaywise.time.max().with_alias('time'),limitby=(0,1)).first().time)
	oldtime -= 9*30.5*86400000
	try:
		f = open("D:\\web2py\\applications\\analytics\\databases\\lroundday.data")
		# this file stores the id to which we have already read daywise
		readid = int(f.read())
		f.close()
	except:
		readid = 0
	old = db(db.ldaywise.id>readid).select()
	i = 0
	for rec in old:
		topic = rec.topic
		time = weekfloor(rec.time)
		volume = rec.volume
		locedge = rec.locedge
		r = db((db.lweekwise.time==time)&(db.lweekwise.topic==topic)&(db.lweekwise.locedge==locedge)).select().first()
		if r:	
			r.update_record(volume = r.volume + volume)
		else:
			db.lweekwise.insert(topic=topic, time=time, locedge=locedge, volume=volume)
		#delete the record if its too old
		if rec.time < oldtime:
			rec.delete_record()
		i += 1
		if i % 10000 == 0:
			print "\t",i
	db(db.ldaywise.time < oldtime).delete()
	db.commit()
	fw = open("D:\\web2py\\applications\\analytics\\databases\\lroundday.data", 'w')
	fw.write(str(old[-1].id))
	fw.close()


# attempt to rollback any uncomitted changes
db.rollback()
try:
	# this file stores the number of log-comm files we have read so far.
	f = open("D:\\web2py\\applications\\analytics\\databases\\readComms.txt")
	readf = int(f.read())+1
	f.close()
except:
	readf = 0

while True:
	read(readf)
	# update the entry in readComms.txt
	fw = open("D:\\web2py\\applications\\analytics\\databases\\readComms.txt", 'w')
	fw.write(str(readf))
	fw.close()
	# garbage collection has been done frequently to save on the memory usage
	gc.collect()
	croundhour()
	gc.collect()
	lroundhour()
	gc.collect()
	croundday()
	gc.collect()
	lroundday()
	gc.collect()
	readf += 1
