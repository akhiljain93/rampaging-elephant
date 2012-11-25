from math import sqrt

def mean(r):
	return sum(r)/float(len(r))

def median(r):
	r = sorted(r)
	return (r[len(r)/2] + r[(len(r)-1)/2])/2.0

def stdev(r):
	r = r[:]
	m = mean(r)
	r = map(lambda x: (x-m)*(x-m), r)
	return sqrt(mean(r))

nList = db(db.nodes.id>0).select().as_list()
nodes = {}
for n in nList:
	nodes[n['uid']] = n['id']

eList = db(db.edges.id>0).select(db.edges.node1,db.edges.node2).as_list()
adj = {}
for e in eList:
	e = [nodes[e['node1']], nodes[e['node2']]]
	try:
		adj[e[0]].append(e[1])
	except KeyError:
		adj[e[0]] = [e[1]]
	try:
		adj[e[1]].append(e[0])
	except KeyError:
		adj[e[1]] = [e[0]]

locs = sorted(list(set((map(lambda x: x['location'], db(db.nodes.id>0).select(db.nodes.location).as_list())))))
locC = {}
for n in nList:
	try:
		locC[locs.index(n['location'])].append(n['id'])
	except:
		locC[locs.index(n['location'])] = [n['id']]


def isab(C,a,b):
	n = len(C)
	if n == 0:
		return False
	bn = b*n
	an = a*n
	for v in C:
		if len(set(adj[v]).intersection(C))-0.1*n < bn:
			return False
		if len(set(adj[v]).difference(C))+0.1*n > an:
			return False
	return True

def calcab(C):
	n = len(C)
	a = 0
	b = n
	for v in C:
		bt = len(set(adj[v]).intersection(C))
		at = len(set(adj[v]).difference(C))
		if bt < b:
			b = bt
		if at > a:
			a = at
	return a/float(n),b/float(n)


def meanab(C):
	n = len(C)
	a = 0
	b = 0
	for v in C:
		b += len(set(adj[v]).intersection(C))
		a += len(set(adj[v]).difference(C))
	return a/float(n*n),b/float(n*n)

def iter(f):
	f = open('D:\\web2py\\applications\\analytics\\private\\'+f)
	clus = {}
	i = 0
	for line in f:
		try:
			int(line)
		except:
			continue
		# clus[i] = map(lambda x: int(x)+1, line.strip().split())
		i += 1
		try:
			clus[int(line)].append(i)
		except KeyError:
			clus[int(line)] = [i]
	ratios = []
	purities = []
	for c in clus:
		maxx = 0
		for l in locC:
			maxx = max(len(set(clus[c]).intersection(locC[l])), maxx)
		maxx = maxx / float(len(clus[c]))
		for n in clus[c]:
			ratios.append(len(set(adj[n]).intersection(clus[c]))/float(len(adj[n])))
			purities.append(maxx)
	ratios.sort()
	purities.sort()
	return (ratios, purities, clus)

clus = []
arr = [0.05,0.075,0.1,0.11,0.12,0.15,0.17,0.2,0.25,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.98,0.99]
arr = map(lambda x: str(x), arr)

for b in arr:
	r,p,cs = iter('mlrmcl1.2\\adj.txt.c2500.i2.0.b'+b)
	for c in cs:
		a,b = meanab(cs[c])
		print a,b
		if a < b*0.95 and b >= 0.2:
			clus.append(cs[c])

def sort(c1, c2):
	ac1, bc1 = calcab(c1)
	am1, bm1 = meanab(c1)
	ac2, bc2 = calcab(c2)
	am2, bm2 = meanab(c2)
	b1 = 0.75*bm1 + bc1*0.25
	b2 = 0.75*bm2 + bc2*0.25
	if b2 - b1 > 0:
		return 1
	elif b2 - b1 < 0:
		return -1
	else: return 0

def verisort(c1, c2):
	ac1, bc1 = calcab(c1)
	am1, bm1 = meanab(c1)
	ac2, bc2 = calcab(c2)
	am2, bm2 = meanab(c2)
	a1 = 0.75*am1 + ac1*0.25
	a2 = 0.75*am2 + ac2*0.25
	if a2 - a1 > 0:
		return -1
	elif a2 - a1 < 0:
		return 1
	else: return 0

def combosort(c1, c2):
	ac1, bc1 = calcab(c1)
	am1, bm1 = meanab(c1)
	ac2, bc2 = calcab(c2)
	am2, bm2 = meanab(c2)
	a1 = 0.75*am1 + ac1*0.25
	a2 = 0.75*am2 + ac2*0.25
	b1 = 0.75*bm1 + bc1*0.25
	b2 = 0.75*bm2 + bc2*0.25
	one = a1/b1
	two = a2/b2
	if two - one > 0:
		return -1
	elif two - one < 0:
		return 1
	else: return 0

fixed = [[4, 11, 15, 34, 41, 48, 65, 109, 126, 138, 149, 156, 157, 162, 169, 170, 172, 175, 176, 179, 183, 189, 190, 192, 196, 197, 198, 200, 204, 205, 207, 211, 212, 218, 220, 221, 223, 228, 230, 232, 236, 238, 240, 244, 245, 252, 253, 255, 256, 263, 264, 266, 272, 273, 278, 280, 286, 288, 289, 291, 292, 294, 296, 297, 299, 300, 302, 304, 306, 308, 311, 313, 317, 319, 320, 322, 324, 325, 329, 331, 335, 336, 338, 340, 342, 347, 348, 350, 354, 356, 360, 362, 364, 366, 371, 372, 374], [177, 181, 187, 193, 195, 209, 214, 225, 226, 234, 249, 251, 261, 269, 271, 276, 285, 303, 305, 310, 314, 318, 321, 328, 334, 341, 353, 359, 369, 375, 376, 1466, 1490, 1493, 1519, 1537, 1562, 2196, 2197, 2198, 2200, 2203, 2205, 2210, 2212, 2216, 2219, 2221, 2225, 2228, 2231, 2236, 2237, 2239, 2241, 2244, 2246, 2247, 2248, 2252, 2255, 2259, 2263, 2265, 2269, 2271, 2272, 2276, 2278, 2279, 2282, 2284, 2285, 2286, 2291, 2294, 2298, 2301, 2305, 2309, 2314, 2315, 2317, 2318, 2319, 2320, 2322, 2325, 2327, 2330, 2333, 2335, 2336, 2340, 2342, 2343, 2344, 2348, 2350, 2354, 2356, 2358, 2359], [381, 383, 384, 390, 392, 397, 401, 408, 413, 415, 420, 425, 430, 436, 438, 441, 446, 452, 458, 461, 464, 467, 472, 474, 479, 488, 490, 492, 495, 500, 505, 508, 513, 520, 525, 527, 528, 531, 535, 538, 541, 542, 544, 546, 549, 553, 554, 558, 559, 563, 565, 569, 570, 575, 579, 581, 585, 586, 587, 589, 590, 594, 596, 597, 600, 602, 605, 606, 607, 608, 612, 615, 618, 621, 625, 628, 632, 635, 637, 639, 643, 644, 1298, 1310, 1316, 1322, 1336, 1345, 1353, 1357, 1374, 1383, 1387, 1389, 1395, 1406, 1414, 1418, 1435, 1436, 1437, 1446], [519, 520, 522, 523, 524, 525, 526, 528, 529, 531, 532, 533, 534, 535, 536, 537, 540, 541, 543, 544, 545, 546, 547, 550, 551, 552, 553, 554, 555, 557, 558, 559, 560, 562, 563, 564, 566, 567, 568, 570, 571, 572, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 595, 596, 598, 599, 600, 601, 602, 603, 604, 605, 607, 608, 609, 610, 611, 613, 614, 616, 617, 618, 619, 620, 622, 624, 625, 626, 627, 628, 629, 630, 631, 633, 634, 635, 638, 639, 640, 641, 642, 643, 644, 645, 646], [521, 539, 548, 556, 561, 566, 577, 593, 599, 620, 623, 636, 984, 986, 988, 990, 992, 994, 998, 999, 1000, 1002, 1004, 1006, 1008, 1009, 1010, 1012, 1014, 1015, 1017, 1018, 1019, 1020, 1023, 1028, 1029, 1030, 1032, 1033, 1034, 1037, 1038, 1039, 1043, 1044, 1046, 1048, 1049, 1050, 1051, 1052, 1054, 1055, 1056, 1060, 1061, 1062, 1063, 1064, 1067, 1069, 1072, 1073, 1074, 1075, 1077, 1080, 1081, 1084, 1087, 1088, 1089, 1090, 1091, 1093, 1094, 1095, 1096, 1097, 1099, 1100, 1104, 1106, 1107, 1109, 1110, 1112, 1113, 1114, 1115, 1117, 1118], [648, 655, 657, 663, 664, 667, 668, 676, 684, 687, 690, 692, 693, 695, 697, 698, 703, 704, 706, 715, 716, 719, 723, 726, 728, 734, 744, 745, 753, 755, 761, 762, 768, 772, 775, 782, 787, 796, 798, 799, 803, 809, 810, 817, 824, 826, 831, 837, 838, 1630, 1631, 1639, 1640, 1643, 1646, 1649, 1654, 1659, 1660, 1663, 1666, 1668, 1669, 1678, 1681, 1689, 1690, 1694, 1696, 1708, 1716, 1717, 1725, 1727, 1731, 1745, 1748, 1749, 1755, 1756, 1766, 1773, 1780, 1781, 1784, 1785, 1791, 1792, 1793, 1796, 1809, 1816, 1817, 1827, 1828, 1837, 1838, 1848, 1852, 1856, 1857, 1859], [649, 650, 651, 653, 654, 659, 661, 662, 668, 669, 670, 671, 672, 674, 677, 678, 679, 682, 683, 686, 689, 691, 694, 696, 698, 699, 700, 701, 707, 708, 709, 710, 714, 718, 721, 722, 724, 725, 727, 729, 730, 731, 732, 736, 737, 738, 739, 741, 743, 746, 747, 750, 751, 752, 754, 756, 757, 759, 764, 765, 766, 769, 771, 774, 776, 777, 778, 779, 781, 783, 784, 785, 786, 789, 790, 792, 793, 794, 795, 797, 801, 802, 805, 806, 807, 808, 810, 812, 813, 814, 815, 819, 820, 821, 822, 823, 825, 830, 832, 833, 834, 835, 839, 841, 842, 843, 844, 845], [1468, 1469, 1470, 1476, 1478, 1479, 1485, 1492, 1495, 1496, 1506, 1508, 1514, 1521, 1522, 1530, 1531, 1539, 1547, 1556, 1558, 1564, 1579, 1584, 1585, 1591, 1597, 1600, 1606, 1612, 1615, 1620, 1625, 1626, 1627, 2202, 2204, 2208, 2209, 2211, 2215, 2217, 2220, 2222, 2223, 2227, 2230, 2233, 2234, 2240, 2242, 2245, 2249, 2250, 2253, 2254, 2257, 2258, 2260, 2261, 2266, 2268, 2270, 2273, 2274, 2277, 2280, 2287, 2288, 2290, 2296, 2299, 2300, 2303, 2306, 2307, 2310, 2311, 2323, 2324, 2331, 2332, 2337, 2338, 2346, 2352, 2353, 2360, 2362], [1632, 1634, 1636, 1637, 1638, 1641, 1645, 1647, 1650, 1651, 1652, 1657, 1664, 1667, 1670, 1672, 1673, 1675, 1676, 1677, 1679, 1682, 1683, 1687, 1688, 1692, 1695, 1698, 1699, 1700, 1701, 1704, 1706, 1709, 1710, 1714, 1715, 1723, 1728, 1733, 1735, 1737, 1739, 1740, 1742, 1746, 1747, 1752, 1753, 1754, 1757, 1761, 1763, 1764, 1765, 1767, 1768, 1774, 1775, 1777, 1778, 1779, 1782, 1788, 1789, 1790, 1799, 1801, 1802, 1803, 1804, 1805, 1806, 1808, 1810, 1811, 1812, 1813, 1814, 1815, 1819, 1822, 1823, 1825, 1826, 1831, 1835, 1836, 1839, 1840, 1844, 1846, 1849, 1850, 1855, 1860, 1861]]
fixed = map(lambda x: set(x), fixed)
clus.sort(combosort)
dels = []
for i in range(len(clus)):
	for j in range(i+1, len(clus)):
		if len(set(clus[i]).intersection(clus[j])) > 0.3*float(min(len(clus[j]), len(clus[i]))):
			dels.append(j)

dels = sorted(list(set(dels)))
len(dels)
len(clus)


def remdels():
	global clus
	for i in range(len(dels)):
		del clus[dels[i] - i]

for i in range(len(clus)):
    if len(set(clus[i]).intersection(fixed[0])) > 0.4*float(len(clus[i])):
            dels.append(i)

def rem(id):
    print clusterid[id], seclus[id]
    a = hehe[clusterid[id]][locs[id]]
    b = hehe[seclus[id]][locs[id]]
    if a > b:
            return False
    elif a < b:
            return True

for key in seclus:
	remd = rem(key)
	if remd == True:
		for f in fixed:
			if key in f:
				f.remove(key)
				break
	elif remd == False:
		for i in range(len(fixed)-1,-1,-1):
			if key in fixed[i]:
				fixed[i].remove(key)
				break
	else:
		print 'haww', key