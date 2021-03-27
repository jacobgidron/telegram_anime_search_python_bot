import json
import time
import re
import telebot

import requests

# f =open('token.txt','r')
# TOKEN = f.read()
# f.close()
TOKEN = "your token here"
bot = telebot.TeleBot(TOKEN, parse_mode=None)
ANIME_REFERENCES = {
    "i love emilia!": 'You are a cruel man, Subaru-kun.',  # Re:Zero
    'omae wa mou shindeiru': '<b>Nani?!</b>',  # meme
 #   'cactus juice': ['<i>It\'s the quenchiest!</i>', '<i>It\'ll quench ya!</i>'],  # Avatar: TLA
    'akihabara!': 'We don\'t have time to sightsee.',  # Oreimo
    "madoka": 'our lord and savior',  # madoka
    "feel free to verbally abuse me too if you'd like": 'I can\'t figure out if you\'re a nice person or a weird person.',
    # Oreimo
    'hakase da nyan': "Moe desu.."
}
REFERENCES_TREGER = "|".join(ANIME_REFERENCES.keys())


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


@bot.message_handler(commands=['help'])  # help message handler
def send_help(message):
    name = message.from_user.first_name
    bot.reply_to(message, f"ok {name} first thing DON'T PANIC")


def make_response(jason):
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
    return msg


@bot.message_handler(regexp='(?:{(.+)}|\[(.+)])')
def bot_anilist_search(message):
    match =  re.findall(r'\[(.+)]', message.text)
    if len(match) >0:
        anime_match, =match
        jason = anilist_search(anime_match, True)
        if jason is None:
            msg = f"sorry {message.from_user.first_name} , {anime_match} is not an anime"
        else:
            msg = make_response(jason)
        bot.send_message(message.chat.id, msg, parse_mode='HTML')
    match = re.findall(r'\{(.+)}', message.text)
    if len(match) >0:
        manga_match, = match
        jason = anilist_search(manga_match, False)
        if jason is None:
            bot.send_message(message.chat.id, f"sorry {message.from_user.first_name} , {manga_match} is not a manga")
        else:
            msg = make_response(jason)
        bot.send_message(message.chat.id, msg, parse_mode='HTML')


@bot.message_handler(regexp=f"/{REFERENCES_TREGER}/i")
def on_reference_match(message):
    print("reference")
    reference, = re.findall(f"/{REFERENCES_TREGER}/i", message.text)
    bot.reply_to(message, ANIME_REFERENCES[reference.lower()],)


while True:
    try:
        bot.polling(none_stop=True)
        # ConnectionError and ReadTimeout because of possible timout of the requests library
        # maybe there are others, therefore Exception
    except Exception:
        time.sleep(15)
