import json
import time
import re
import telebot

import requests
f =open('token.txt','r')
TOKEN = f.read()
f.close()

def anilist_search(name, anime=True):
    variables = {
        'search': name,
        'page': 1,
        'perPage': 3
    }
    anime_query = '''
    query ($id: Int, $page: Int, $perPage: Int, $search: String) {
    Page(page: $page, perPage: $perPage) {
    pageInfo {
      total
      currentPage
      lastPage
      hasNextPage
      perPage
    }
    media(id: $id, search: $search,sort:SEARCH_MATCH,type:ANIME, isAdult:false) {
      id
      title {
        romaji
        native
        userPreferred
      }
      siteUrl
      description
      episodes
      isAdult
      genres
      source
      coverImage {
        extraLarge
        large
        medium
        color
      }
      
    }
    }
    }
    '''
    manga_query = '''
        query ($id: Int, $page: Int, $perPage: Int, $search: String) {
        Page(page: $page, perPage: $perPage) {
        pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
          perPage
        }
        media(id: $id, search: $search,sort:SEARCH_MATCH,type:MANGA, isAdult:false) {
          id
          title {
            romaji
            native
            userPreferred
          }
          siteUrl
          description
          episodes
          isAdult
          genres
          source
          coverImage {
            extraLarge
            large
            medium
            color
          }

        }
        }
        }
        '''
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': anime_query if anime else manga_query, 'variables': variables})
    j = response.json()
    if j['data']['Page']['pageInfo']["total"] == 0:
        print(f"{anime} is not an anime")
    else:
        print(j['data']['Page']['media'][0]['title']['romaji'])
        print(j['data']['Page']['media'][0]['id'])
        return j


bot = telebot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(regexp=r'\[(.+)]|\{(.+)}')
def bot_anilist_search(message):
    matchs = re.match(r'\[(.+)].+\{(.+)}', message.text).groups()
    anime_match, manga_match = matchs
    if anime_match is not None:
        jason = anilist_search(anime_match, True)
        if jason is None:
            bot.send_message(message.chat.id, f"sorry {message.from_user.first_name} , {manga_match} is not a manga")
        image = jason['data']['Page']['media'][0]['coverImage']['extraLarge']
        url = jason['data']['Page']['media'][0]['siteUrl']
        title = jason['data']['Page']['media'][0]['title'].values()
        title = " \n".join(title)
        genres = ", ".join(jason['data']['Page']['media'][0]['genres'])
        description = jason['data']['Page']['media'][0]['description']
        msg = f"""  <b>{title}</b>
                    
                    <a href="{image}">&#8205;</a>
                    <a href="{url}">::link::</a>
                    <pre language="python">{genres}</pre>
                    {description.replace("<br>", "")}"""
        bot.send_message(message.chat.id, msg, parse_mode='HTML')
    if manga_match is not None:
        jason = anilist_search(manga_match, False)
        if jason is None:
            bot.send_message(message.chat.id, f"sorry {message.from_user.first_name} , {manga_match} is not a manga")
        image = jason['data']['Page']['media'][0]['coverImage']['extraLarge']
        url = jason['data']['Page']['media'][0]['siteUrl']
        title = jason['data']['Page']['media'][0]['title'].values()
        title = " \n".join(title)
        genres = ", ".join(jason['data']['Page']['media'][0]['genres'])
        description = jason['data']['Page']['media'][0]['description']
        msg = f"""  <b>{title}</b>
                    
                    <a href="{image}">&#8205;</a>
                    <a href="{url}">::link::</a>
                    <pre language="python">{genres}</pre>
                    {description.replace("<br>", "")}"""
        bot.send_message(message.chat.id, msg, parse_mode='HTML')


@bot.message_handler(commands=['help'])  # help message handler
def send_welcome(message):
    name = message.from_user.first_name
    bot.reply_to(message, f"ok {name} first thing DON'T PANIC")


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
            # ConnectionError and ReadTimeout because of possible timout of the requests library
            # maybe there are others, therefore Exception
        except Exception:
            time.sleep(15)
