from django.shortcuts import render
from django.http import HttpResponse
from googleapiclient.discovery import build
# Create your views here.
import json
import sklearn
import joblib
from sklearn.cluster import KMeans, MiniBatchKMeans
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import requests

from .hits import hits

subscription_key = "7ba2665d89574bed9b0e887c41b882a5"
assert subscription_key

search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
search_term = ""

def getClimateData(request):
    hits.get_url_map()
    hits.get_adj_lis()
    return render(request, 'Climate_App/climate.html')

def getGoogleResults(request):
     my_api_key = "AIzaSyDbiy21NBP13V3FzvRe1LaF5E0UmwwfuPo"
     my_cse_id = "014871123708314990102:5dujllnfiee"
     service = build("customsearch", "v1", developerKey=my_api_key)
     res = service.cse().list(q=search_term, cx=my_cse_id).execute()
     return render(request, 'Climate_App/googleResults.html', {"google": json.dumps(res)})
    #return render(request, 'Climate_App/googleResults.html')

def getCustomResults(request):
    url = "http://ec2-35-171-122-69.compute-1.amazonaws.com:8983/solr/nutch/select?q=content:\"" + str(
        search_term) + "\" OR title:\"" + str(search_term) + "\" OR id:\"" + str(search_term) + "\""
    response = requests.get(url)
    search_results = response.json()

    return render(request, 'Climate_App/customResults.html', {"results": search_results})

def getBingResults(request):
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    y = json.dumps(search_results)
    return render(request, 'Climate_App/bingResults.html', {"bing": y})

def getClusterResults(request):
    return render(request, 'Climate_App/clusterResults.html')

def getQueryExpansionResults(request):
    return render(request, 'Climate_App/queryExpansionResults.html')


def getSearchQuery(request):
    global search_term
    # hits.get_url_map()
    # hits.get_adj_lis()
    search_term = request.GET['search']
    return render(request, 'Climate_App/climate.html', {"search_term" : search_term})

def getHitsResults(request):
    global search_term
    url = "http://ec2-35-171-122-69.compute-1.amazonaws.com:8983/solr/nutch/select?q=content:\"" + str(
        search_term) + "\" OR title:\"" + str(search_term) + "\" OR id:\"" + str(search_term) + "\""
    response = requests.get(url)
    results = response.json()
    print(len(results))
    search_results = hits.get_hits(results)
    return render(request, 'Climate_App/hitsResults.html', {"results": search_results})

def getClusteringResults(request):
    global search_term
    search_term=request.GET['search']
    model=joblib.load('clustering_model.pkl')
    vectorizer=joblib.load('vectorizer.pkl')
    search=vectorizer.transform([search_term])
    results=model.predict(search)
    print(results)
    return render(request,'Climate_App/clusteringResults.html',{"results":results})

    
