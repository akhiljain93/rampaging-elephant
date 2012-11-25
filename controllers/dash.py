# Controller for all the helper pages which are loaded via ajax

import datetime
import time
from math import sqrt

# Helper Function to calculate z-score
def zscore(obs, pop):
    number = float(len(pop))
    avg = sum(pop) / number
    std = sqrt(sum(((c - avg) ** 2) for c in pop) / number)
    if std == 0 : return (obs - avg)
    return (obs - avg) / std

# Sorting helper function
def sortthis(a,b):
    if a['score'] > b['score']: return -1
    elif a['score'] == b['score']: return 0
    else: return 1

### Helper pages ###
# Topics: to laad the list of all topics from the requested table
def topics():
    try:
        table = request.args[0]
    except:
        table = 'cdaywise'
    try:
        alltrue = request.args[1]
    except:
        alltrue = "false"

    allstates = map(lambda x: x[0], db.executesql('select distinct topic from '+table+' order by topic asc;'))
    return dict(allstates=allstates, alltrue=alltrue)

# Timeline graph: takes the arguments filter the timeline 
def timeline():
    filter = "week"
    sub = "all"
    change = "false"
    try:
        filter = request.args[0]
    except:
        filter = "week"
    try:
        sub = request.args[1].replace('_',' ')
    except:
        sub = "all"

    fieldwise_id =''
    fieldwise_time =''
    fieldwise_topic =''
    sum_fieldwise_volume =''
    table =''
    if "day" in filter: # daywise timeline
        fieldwise_id = db.cdaywise.id
        fieldwise_time = db.cdaywise.time
        fieldwise_topic = db.cdaywise.topic
        sum_fieldwise_volume = db.cdaywise.volume.sum()
        table = 'cdaywise'
    elif "week" in filter:  # weekwise timeline
        fieldwise_id = db.cweekwise.id
        fieldwise_topic = db.cweekwise.topic
        fieldwise_time = db.cweekwise.time
        sum_fieldwise_volume = db.cweekwise.volume.sum()
        table = 'cweekwise'
    else: # hourwise timeline
        fieldwise_id = db.chourwise.id
        fieldwise_time = db.chourwise.time
        fieldwise_topic = db.chourwise.topic
        sum_fieldwise_volume = db.chourwise.volume.sum()
        table = 'chourwise'
        
    fetched_data = []
    if 'all'== sub:
        fetched_data = db(fieldwise_id>0).select(fieldwise_time.with_alias('date'),sum_fieldwise_volume.with_alias('price'),groupby=fieldwise_time).as_list()
    else:
        fetched_data = db(fieldwise_topic==sub).select(fieldwise_time.with_alias('date'), sum_fieldwise_volume.with_alias('price'),groupby=fieldwise_time).as_list()    
    if filter not in['day','hour','week']: 
        filter='hour'
    if len(fetched_data)==0:
        raise HTTP(404) # if no data is fetched 
    
    return dict(db_data=fetched_data, fieldwise_topic=fieldwise_topic, wise=filter)

# Top 10 list: returns the list of top 10 topics
def top10():
    start_year = 2012
    start_month = 8
    start_day = 1
    end_year = 2013
    end_month = 12
    end_day = 31
    cluswise = True
    filt = None

    if len(request.args) > 5: # if starting date and ending date is given
        start_year = int(request.args[0])
        start_month = int(request.args[1])
        start_day = int(request.args[2])
        end_year = int(request.args[3])
        end_month = int(request.args[4])
        end_day = int(request.args[5])
        if len(request.args) > 6: # if fliter is also provided 
            try:
                filt = int(request.args[6])
            except ValueError:
                filt = request.args[6]
                cluswise = False
    elif len(request.args) > 0: # if only filter is provided
        try:
            filt = int(request.args[0])
        except ValueError:
            filt = request.args[0]
            cluswise = False
    start_stamp = int(time.mktime(datetime.date(start_year, start_month,start_day).timetuple()))
    end_stamp = int(time.mktime(datetime.date(end_year, end_month, end_day).timetuple()))
    if not filt: # if no filter is applied
        data = db((db.cweekwise.time>start_stamp*1000)&(db.cweekwise.time<end_stamp*1000)).select(db.cweekwise.topic.with_alias('topic'),db.cweekwise.volume.sum().with_alias('volsum'),groupby='cweekwise.topic',orderby='~volsum',limitby=(0,10))
    elif cluswise: # if cluster id is provided
        data = db((db.cweekwise.time>start_stamp*1000)&(db.cweekwise.time<end_stamp*1000))(db.cweekwise.cledge==db.cledges.id)((db.cledges.cluster1==filt)|(db.cledges.cluster2 == filt)).select(db.cweekwise.topic.with_alias('topic'),db.cweekwise.volume.sum().with_alias('volsum'),groupby='cweekwise.topic',limitby=(0,10),orderby='~sum(cweekwise.volume)')
    else: # if location is provided
        data = db((db.lweekwise.time>start_stamp*1000)&(db.lweekwise.time<end_stamp*1000))(db.lweekwise.locedge==db.locedges.id)((db.locedges.loc1==filt)|(db.locedges.loc2 == filt)).select(db.lweekwise.topic.with_alias('topic'),db.lweekwise.volume.sum().with_alias('volsum'),groupby='lweekwise.topic',limitby=(0,10),orderby='~sum(lweekwise.volume)')
    return dict(db_data=data, start_date=[start_year,start_month,start_day], end_date=[end_year,end_month,end_day])

# Trending Topics: returns the list of trending topic
def t_topics():
    import time
    filt=None
    table = db.chourwise
    cluswise = True
    if len(request.args) > 0:
        try:
            filt = int(request.args[0])
        except ValueError:
            cluswise = False
            filt = request.args[0]
            table = db.lhourwise
    if not filt: # if filter is not applied
        latest = db(table.id>0).select(table.time.max().with_alias('time'),limitby=(0,1)).first().time - 2*3600*1000
        day1 = db(table.time>=latest)(table.time < latest+2*3600*1000).select(table.topic.with_alias('topic'),table.volume.sum().with_alias('volumesum'), groupby=str(table)+'.topic')
        dayhist = db(table.time>=(latest-3*60*60*24*1000))(table.time<latest).select(table.topic.with_alias('topic'),table.time.with_alias('time'),table.volume.sum().with_alias('volumesum'), groupby=str(table)+'.topic,'+str(table)+'.time', orderby=table.time)
    elif cluswise: # if cluster id is provided
        latest = db(table.cledge==db.cledges.id)((db.cledges.cluster1==filt)|(db.cledges.cluster2 == filt)).select(table.time.max().with_alias('time'),limitby=(0,1)).first().time - 2*3600*1000
        day1 = db(table.time>=latest)(table.time < latest+2*3600*1000)(table.cledge==db.cledges.id)((db.cledges.cluster1==filt)|(db.cledges.cluster2 == filt)).select(table.topic.with_alias('topic'), table.volume.sum().with_alias('volumesum'), groupby=str(table)+'.topic')
        dayhist = db(table.time>=(latest-3*60*60*24*1000))(table.time<latest)(table.cledge==db.cledges.id)((db.cledges.cluster1==filt)|(db.cledges.cluster2 == filt)).select(table.topic.with_alias('topic'),table.time.with_alias('time'),table.volume.sum().with_alias('volumesum'), groupby=str(table)+'.topic,'+str(table)+'.time', orderby=table.time)
    else: # if location is provided
        latest = db(table.locedge==db.locedges.id)((db.locedges.loc1==filt)|(db.locedges.loc2==filt)).select(table.time.max().with_alias('time'),limitby=(0,1)).first().time - 2*3600*1000
        day1 = db(table.time>=latest)(table.time < latest+2*3600*1000)(table.locedge==db.locedges.id)((db.locedges.loc1==filt)|(db.locedges.loc2==filt)).select(table.topic.with_alias('topic'), table.volume.sum().with_alias('volumesum'), groupby=str(table)+'.topic')
        dayhist = db(table.time>=(latest-3*60*60*24*1000))(table.time<latest)(table.locedge==db.locedges.id)((db.locedges.loc1==filt)|(db.locedges.loc2==filt)).select(table.topic.with_alias('topic'),table.time.with_alias('time'),table.volume.sum().with_alias('volumesum'), groupby=str(table)+'.topic,'+str(table)+'.time', orderby=table.time)
    score = []
    for x in day1:
        arr = []
        currentdate = latest-3*60*60*24*1000
        for y in dayhist:
            if (x.topic==y.topic):
                for z in range((y.time - currentdate)/(60*60*1000)):
                    arr.append(0)
                arr.append(y.volumesum)
                currentdate = y.time + 60*60*1000
        while len(arr) < 72:
            arr.append(0)
        arrnew = []
        for i in range(0,len(arr),2):
            arrnew.append(arr[i] + arr[i+1])
        arrnew.append(x.volumesum)
        if len(arrnew) > 0:
            score.append({'topic':x.topic, 'score':int(zscore(x.volumesum, arrnew[:-1])*100)/100.0, 'diff': sum(arrnew[-12:])-sum(arrnew[-24:-12])})
    score.sort(sortthis)
    diffsortedTopics = map(lambda x: x[1], sorted(map(lambda x: (x['diff'], x['topic']),score),reverse=True))
    sortedScores = map(lambda x: x['score'], score)
    return dict(topics = diffsortedTopics, scores = sortedScores, latest = latest)

# Motion Chart Helper Page: returns data required to create motion chart
def motion():
  topic = request.args[0].replace('_',' ')
  cluswise = True
  if len(request.args) > 1:
    cluswise = False
  def addto(arr, time, value):
    for element in arr:
      if element[0] == time:
        element[1] += value
        t = element[1]
        break
    else:
      arr.append([time,value])
      t = value
      arr.sort()
    return t
  mint = 9999999999999
  maxt = 0
  maxv = 0
  mintimediff = 24*3600*1000 # assumed daywise!
  if cluswise:
    csizes = db(db.nodes.id>0).select(db.nodes.id.count().with_alias('count'), groupby=db.nodes.clusterid, orderby=db.nodes.clusterid)
    table = db.cdaywise
    comm = db(table.topic == topic)(table.cledge == db.cledges.id).select(db.cledges.cluster1.with_alias('c1'), db.cledges.cluster2.with_alias('c2'), table.time, table.volume)
    data = [{'id': i, 'size': csizes[i-1].count, 'comm': []} for i in range(1,17)]
    for entry in comm:
      t = entry[str(table)].time + mintimediff / 2  # because the value for an hour is best to be taken at the middle of the hour
      v = entry[str(table)].volume
      maxv = max(maxv, addto(data[entry.c1 - 1]['comm'], t, v))
      maxv = max(maxv, addto(data[entry.c2 - 1]['comm'], t, v))
      mint = min(mint, t)
      maxt = max(maxt, t)
  else:
    csizes = db(db.nodes.id>0).select(db.nodes.id.count().with_alias('count'), db.nodes.location.with_alias('loc'), groupby=db.nodes.location, orderby=db.nodes.location)
    table = db.ldaywise
    comm = db(table.topic == topic)(table.locedge == db.locedges.id).select(db.locedges.loc1.with_alias('c1'), db.locedges.loc2.with_alias('c2'), table.time, table.volume)
    data = [{'id': i, 'size': csizes[i-1].count, 'comm': [], 'loc': csizes[i-1].loc} for i in range(1,20)]
    def getEle(loc):
      for ele in data:
        if ele['loc'] == loc:
          return ele
    for entry in comm:
      t = entry[str(table)].time + mintimediff / 2  # because the value for an hour is best to be taken at the middle of the hour
      v = entry[str(table)].volume
      maxv = max(maxv, addto(getEle(entry.c1)['comm'], t, v))
      maxv = max(maxv, addto(getEle(entry.c2)['comm'], t, v))
      mint = min(mint, t)
      maxt = max(maxt, t)
  cumumax = 0
  for clus in data:
    clus['cumu'] = clus['comm'][:]
    for i in range(1, len(clus['cumu'])):
      clus['cumu'][i] = [clus['cumu'][i][0], clus['cumu'][i-1][1]+clus['cumu'][i][1]]
    if len(clus['cumu']):
      cumumax = max(cumumax, clus['cumu'][-1][1])
  return dict(data = data, mint = mint, maxt = maxt, maxv = maxv, mintimediff = mintimediff, cumumax = cumumax, cluswise=cluswise)