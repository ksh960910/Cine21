import requests
from bs4 import BeautifulSoup
import pymongo
import re

actors_info_list = list()

connection = pymongo.MongoClient()
actor_db = connection.cine21
actor_collection = actor_db.actor

cine21_url = 'http://www.cine21.com/rank/person/content'
post = dict()
post['section'] = 'actor'
post['period_start'] = '2020-12'
post['gender'] = 'all'

for index in range(1,21):
    post['page'] = index

    res = requests.post(cine21_url,data=post)
    soup = BeautifulSoup(res.content, 'html.parser')
    actors = soup.select('li.people_li div.name')
    hits = soup.select('ul.num_info > li > strong')
    movies = soup.select('ul.mov_list')
    rankings = soup.select('li.people_li > span.grade')



    for index, actor in enumerate(actors):
        actor_name = re.sub('\(\w*\)','',actor.text)
        actor_hits = int(hits[index].text.replace(',',''))
        movie_titles = movies[index].select('li a span')
        movie_title_list = []
        for movie_title in movie_titles:
            movie_title_list.append(movie_title.text)

        actor_info_dict = dict()
        actor_info_dict['배우이름'] = actor_name
        actor_info_dict['흥행지수'] = actor_hits
        actor_info_dict['출연영화'] = movie_title_list
        actor_info_dict['랭킹'] = rankings[index].text

        actor_link = 'http://www.cine21.com' + actor.select_one('a').attrs['href']
        res_actor = requests.get(actor_link)
        soup_actor = BeautifulSoup(res_actor.content, 'html.parser')
        default_info = soup_actor.select_one('ul.default_info')
        actor_detail = default_info.select('li')

        for actor_item in actor_detail:
            actor_item_field = actor_item.select_one('span.tit').text
            actor_item_value = re.sub('<span.*?>.*?</span>', '',str(actor_item))
            actor_item_value = re.sub('<.*?>','',actor_item_value)
            actor_info_dict[actor_item_field] = actor_item_value
        actors_info_list.append(actor_info_dict)

actor_collection.insert_many(actors_info_list)
print(actors_info_list)

#신장이 가장 큰 사람 10명뽑기
# docs = actor_collection.find({}).sort('신장/체중', pymongo.DESCENDING).limit(10)
# for doc in docs:
#     print(doc)

#특기가 존재하는 배우의 정보들 다 불러오기
# docs = actor_collection.find({'특기':{'$exists':True}})
# for doc in docs:
#     print(doc)