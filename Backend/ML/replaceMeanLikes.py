import json

with open('ALLDATA.json') as json_data:
    d = json.load(json_data)

json_size = len(d)

start_index = 0
likes = d[0]['likes']

for i in range(1, json_size):
    if (d[i]['meanLikes'] == d[i-1]['meanLikes']):
        likes += d[i]['likes']
    else:
        newMean = likes/((i - start_index))
        for j in range(start_index, i):
            d[j]['meanLikes'] = newMean
        start_index = i
        likes = d[i]['likes']
    if (i == json_size - 1):
        newMean = likes/((i + 1) - start_index)
        for j in range(start_index, i + 1):
            d[j]['meanLikes'] = newMean
        print newMean, likes, i, start_index

for i in range (json_size):
    print d[i]['meanLikes']

with open('newData.json', 'w') as outfile:
    json.dump(d, outfile)
