from bs4 import BeautifulSoup
import urllib
import urllib2
from datetime import datetime
import time
from threading import Thread
import csv
import sys
import socket
import math 
import networkx as nx
import numpy as np

socket.setdefaulttimeout(10.0)
reload(sys)
sys.setdefaultencoding('utf-8')

comment_dict = dict()
d1 = datetime.strptime("2017-1-22", "%Y-%m-%d")
start_date = time.mktime(d1.timetuple())
matrix_dict = dict()
di_G_dict = dict()

def comment_process(url):
    result = get_comments(url,url,[])
    comment_dict[url] = result
    return 0

def get_url():
    site = urllib.urlopen("https://ierg3320.wordpress.com/links/").read()
    soup = BeautifulSoup(site,'html.parser')
    links = soup.find_all("a", class_="in-cell-link")
    urls = []
    #print(len(links))
    for link in links:
        url = link.string.strip()
        if url.find("https") == -1:
            if url.find("http") == -1:
                url = "https://" + url
            else:
                url = url.replace("http","https")
        url = url.split("//")[0] + "//" + url.split("//")[1].split("/")[0]
        if url not in " ".join(urls):
            urls.append(url)
        #else:
            #print(url)
    return urls

def get_comments(url,origin_url,checked_link):
    checked_link.append(url)
    comment_dict = dict()
    try:
        #site = urllib.urlopen(url).read()
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        soup = BeautifulSoup(response,'html.parser')
        #request.close()
        commment_lists = soup.find("ol",class_="comment-list")
        time_stamp = -1
        if commment_lists != None:
            comments = commment_lists.findAll("li")
            for comment in comments:
                content  =''
                comment_content = comment.find("div",class_="comment-content").findAll('p')
                for para in comment_content:
                    if para.text != None and para.get('class') == None:
                        content = content + para.text
                if comment.find("time") != None:
                    d = datetime.strptime(comment.find("time")['datetime'].split('T')[0], "%Y-%m-%d")
                    time_stamp = math.ceil((time.mktime(d.timetuple()) - start_date)/(86400*7))
                else:
                    print("haha")
                if comment.find("a",class_="url") == None:
                    if 'unknown' in comment_dict:
                        comment_dict["unknown"].append((content,time_stamp))
                    else:
                        comment_dict["unknown"] = [(content,time_stamp)]
                else:
                    #if comment.find("a",class_="url")['href'] == "http://mosessmng.wordpress.com":
                        #print("haha")
                        #print(content)
                    #print(content)
                    if comment.find("a",class_="url")['href'] in comment_dict:
                        old_content = comment_dict[comment.find("a",class_="url")['href']][0][0]
                        old_timestamp = comment_dict[comment.find("a",class_="url")['href']][0][1]
                        if old_timestamp < time_stamp:
                            comment_dict[comment.find("a",class_="url")['href']] = [(old_content+"\n"+content,old_timestamp)]
                        else: 
                            comment_dict[comment.find("a",class_="url")['href']] = [(old_content+"\n"+content,time_stamp)]     
                    else:
                        comment_dict[comment.find("a",class_="url")['href']] = [(content,time_stamp)]
        else:
            links = soup.find_all("a")
            links_process = [] 
            for link in links:
                if link.get('href') != None:
                    if link['href'] not in " ".join(links_process):
                        links_process.append(link['href'])
            #print(links_process)
            for link in links_process:
               if link.find(origin_url) != -1 and link not in checked_link:
                    #print(link)
                    result = get_comments(link.strip(),origin_url,checked_link)
                    for user in result:
                        if user not in comment_dict:
                            comment_dict[user] = []
                        check_content = []
                        for comment in comment_dict[user]:
                            check_content.append(comment[0])
                        for comment in result[user]:
                            if comment[0] not in " ".join(check_content):
                                #print(comment)
                                comment_dict[user].append(comment)
    #except:
        #print(url)
        #pass
    except urllib2.URLError, err:
        print(err.reason)
    return comment_dict

def matrix_process(user,commenter,week):
    for i in range(int(week),11):
        matrix_dict[i][user - 1][commenter - 1] += 1
        
def NetworkX(user,commenter,week):
    for i in range(int(week),11):
        di_G_dict[i].add_edge(commenter,user)

if __name__ == '__main__':
    group_id = []
    for i in range(1,11):
        matrix_dict[i] = np.zeros((78,78))
        di_g = nx.DiGraph()
        for k in range(1,79):
            di_g.add_node(k)
        di_G_dict[i] = di_g
    urls = get_url()
    #two special links without in-cell-link class
    urls.append("https://ierg3320socialmediaandhumaninformationinteraction.wordpress.com")
    urls.append("https://journey1001.wordpress.com")
    #result = get_comments("https://lanselott.wordpress.com","https://lanselott.wordpress.com",[])
    for url in urls:
        if url == "https://lanselott.wordpress.com" or url == "https://wangyingling.wordpress.com" or url == "https://ierg3320tonykang.wordpress.com" or url == "https://ierg33201155029092.wordpress.com" or url == "https://amazinghoran.wordpress.com":
            group_id.append(urls.index(url))
    #print(result)
    #i = 0
    #for key in result:
        #for content in result[key]:
            #i = i + 1
    #print(i)

    #print(comment_dict["https://lanselott.wordpress.com/"]) 
    #print(comment_dict["http://gravatar.com/ierg3320tina"])
    print("start to get data........")
    threads = []
    for url in urls:
        #t = Thread(target=comment_process, args=[url])
        #t.start()
        #threads.append(t)
        result = get_comments(url,url,[])
        comment_dict[url] = result
    #for t in threads:
        #t.join()
    print("get data finished.......")
    #print(comment_dict)
    csvfile = file('csv_test.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(['Target', 'Source', 'week','comment','Weight'])
    for key in comment_dict:
        for key1 in comment_dict[key]:
            for comment in comment_dict[key][key1]:
                data = []
                key_id = urls.index(key)
                key1_id = -1
                if key1 != "unknown":
                    key1 = key1.strip()
                    if key1.find('https') == -1:
                        key1 = key1.replace('http','https')
                    url = key1.split("//")[0] + "//" + key1.split("//")[1].split("/")[0]
                    if url not in " ".join(urls):
                        if key1.find("gravatar") != -1:
                            match = False
                            for user_url in urls:
                                if user_url.find(key1.split("/")[-1]) != -1:
                                    key1_id = urls.index(user_url)
                                    match = True
                            if not match:
                                print("no match")
                                print(key)
                                print(key1)
                        else:
                            print("not gravatar")
                            print(key)
                            print(key1)
                    else:
                        key1_id = urls.index(url)
                    if key_id in group_id or key1_id in group_id:
                        data = [(key_id, key1_id, comment[1],comment[0],1.5)]
                    else:
                        data = [(key_id, key1_id, comment[1],comment[0],1.0)]
                    if key_id != key1_id and key1_id != -1:
                        writer.writerows(data)
                        matrix_process(key_id,key1_id,comment[1])
                        NetworkX(key_id,key1_id,comment[1])
    for i in range(1,11):
        print("week " + str(i) + " socialMatrix is: ")
        print(matrix_dict[i])
        np.savetxt('socialMatrix_week'+str(i)+'.txt',matrix_dict[i],fmt='%.2f')
        print("week " + str(i) + " density is " + str(nx.density(di_G_dict[i])))
        for group_member in group_id: 
            print("week " + str(i) + " : "+str(group_member) + " indgree is " + str(di_G_dict[i].in_degree()[group_member]))
            print("week " + str(i) + " : "+str(group_member) + " outdgree is "+ str(di_G_dict[i].out_degree()[group_member]))
            print("week " + str(i) + " : "+str(group_member) + " betweeness is " + str(nx.betweenness_centrality(di_G_dict[i])[group_member]))
            print("week " + str(i) + " : "+str(group_member) + " closeness is " + str(nx.closeness_centrality(di_G_dict[i])[group_member]))    
                #else:
                    #data = [(key_id, key1, comment[1],comment[0])]
                    #writer.writerows(data)
