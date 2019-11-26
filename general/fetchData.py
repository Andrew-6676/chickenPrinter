def fetchData(cursor):
	data = []
	for r in cursor.itermap():
		d = {}
		for k in r.keys():
			# print('---', k, r[k])
			d[k] = r[k]
		data.append(d)
	return data

def fetchDataOne(cursor):
	return fetchData(cursor)[0]

def fetchDataAll(cursor):
	return fetchData(cursor)
