import glob
import os

import requests
import math

urlMap = dict()
urlMapId = dict()
adjList = dict()
cwd = os.getcwd()


def get_url_map():
    file_path = cwd + "/Climate_App/hits/urlMap"
    file = open(file_path, "r")
    for urlReads in file:
        urlDetails = urlReads[1:].split('=')
        if(len(urlDetails) > 1):
            urlMap[urlDetails[0].strip()] = urlDetails[1].replace('\n', '')
            urlMapId[urlDetails[1].replace('\n', '')] = urlDetails[0].strip()

def get_adj_lis():
    file_path = cwd + "/Climate_App/hits/adjList"
    file = open(file_path, "r")
    for urlArray in file:
        arrayList = urlArray[1:].split('=')
        if(len(arrayList) > 1):
            arrayList[1] = arrayList[1].replace('\n', '')
            adjList[arrayList[0]] = arrayList[1].split(' ')

def add_to_map(map, key, val):
    if(map.get(urlMap[key])):
        map.get(urlMap[key]).append(urlMap[val])
    else:
        map[urlMap[key]] = [urlMap[val]]
    return map

def make_graph(inlinks, outlinks):
    global adjList
    for key in adjList:
        url_list = adjList[key]
        for url in url_list:
            outlinks = add_to_map(outlinks, key.strip(), url.strip())
            inlinks = add_to_map(inlinks, url.strip(), key.strip())
    return inlinks, outlinks

def get_query(results):
    global urlMap
    jsonMap = dict()
    input_urls_id = list()
    input_urls = list()
    docs = results['response']['docs']
    doc_len = min(len(docs), 10)
    for i in range(0, doc_len):
        jsonMap[docs[i]['url']] = docs[i]
        input_urls.append(docs[i]['url'])

    for url in input_urls:
        if(urlMap.get(url)):
            id = urlMap[url]
            input_urls_id.append(id)
    return input_urls_id, jsonMap


def initalize_ranking(union_url_ids):
    hub_score, auth_score = dict(), dict()
    for key in union_url_ids:
        hub_score[key] = 1
        auth_score[key] = 1
    return hub_score, auth_score

def isConverged(new_rank, old_rank):
    converged = True
    tolerance = 0.01
    for key in new_rank:
        a=(new_rank[key])
        c=a-(old_rank[key])
        if ((abs(c)) > (tolerance)):
            converged = False
            break
    return converged

def compute_score(hub_score, auth_score, inlinks, outlinks, union_url_ids):
    newAuthRank = calcAuthscore(hub_score, auth_score, inlinks, union_url_ids)
    calcHubScore(hub_score, auth_score, outlinks, union_url_ids)
    while not isConverged(newAuthRank, auth_score):
        newAuthRank = calcAuthscore(hub_score, auth_score, inlinks, union_url_ids)
        newHubRank = calcHubScore(hub_score, auth_score, outlinks, union_url_ids)
        hub_score = newHubRank
        auth_score = newAuthRank



def calcHubScore(hub_score, auth_score, outlinks, union_url_ids):
    temp_rank = dict()
    norm = 0
    for key in hub_score:
        temp_rank[key] = 0.0
        if(outlinks.get(key) != None):
            tempList = outlinks[key]
        else:
            continue
        hubScore = 0.0
        for dest in tempList:
            if (dest in union_url_ids):
                hubScore += auth_score[dest]
        norm += math.pow(hubScore, 2)
        temp_rank[key] = hubScore
    norm = math.sqrt(norm)
    for key in temp_rank:
        temp_rank[key] = temp_rank[key] / norm

    return temp_rank

def calcAuthscore(hub_score, auth_score, inlinks, union_url_ids):
    temp_rank = dict()
    norm = 0
    for key in auth_score:
        temp_rank[key] = 0.0
        if(inlinks.get(key) != None):
            tempList = inlinks[key]
        else:
            continue
        authScore = 0.0
        for dest in  tempList:
            if (dest in union_url_ids ):
                authScore += hub_score[dest]
        norm += math.pow(authScore, 2)
        temp_rank[key]= authScore
    norm = math.sqrt(norm)
    for key in temp_rank:
        temp_rank[key] = temp_rank[key] / norm
    return temp_rank

def get_hits(results):
    input_urls_id, jsonMap = get_query(results)
    inlinks, outlinks = dict(), dict()
    inlinks, outlinks = make_graph(inlinks, outlinks)
    union_url_ids = list()
    required_auth_score = dict()
    sorted_auth_score = dict()

    for key in input_urls_id:
        if (key == None):
            continue
        union_url_ids.append(key)
        outs = outlinks.get(key)
        if outs == None:
            continue
        else :
            for i in range(0, len(outs)):
                union_url_ids.append(outs[i])

        ins = inlinks.get(key)
        if ins == None:
            continue
        else:
            for i in range(0, len(ins)):
                union_url_ids.append(ins[i])

    hub_score, auth_score = initalize_ranking(union_url_ids)

    compute_score(hub_score, auth_score, inlinks, outlinks, union_url_ids)
    response = []
    for id in input_urls_id:
        score = auth_score[id]
        required_auth_score[id] = score
    for k in sorted(required_auth_score, key=required_auth_score.__getitem__, reverse=True):
        sorted_auth_score[k] = required_auth_score[k]
    for key in sorted_auth_score:
        url = urlMapId[key]
        response.append(jsonMap[url])

    return response


