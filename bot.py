import json
import time
import re
import telebot

import requests

with open("Data.json") as f:
    data = json.load(f)
ANIME_REFERENCES = data["OTHER"]["ANIME_REFERENCES"]
if data["BOT DATA"]["TOKEN"] is None:
    data["BOT DATA"]["TOKEN"] = input("please enter a bot token")
    with open("Data.json", "w") as file:
        json.dump(data, file, indent=4)
        data["last_updated"] = time.ctime()

bot = telebot.TeleBot(data["BOT DATA"]["TOKEN"], parse_mode=None)
REFERENCES_TRIGGER = re.compile("|".join(ANIME_REFERENCES.keys()),
                                re.IGNORECASE)  # made to check for sentences the bot will respond to


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

@bot.message_handler(commands=['notify', "notfy"])
def notify_all(message):
    print("debug")
    members = bot.get_chat_administrators(message.chat.id)
    response = []
    for member in members:
        response.append(f"come here [{member.user.first_name} {member.custom_title if (member.custom_title is not None) else '' } {member.user.last_name}](tg://user?id={member.user.id})")
    bot.send_message(message.chat.id, "\n".join(response), parse_mode='Markdown')
    # [inline mention of a user](tg: // user?id=
    # https: // api.telegram.org / bot1307488101: AAEWL089l5csfNV4oPrK9fYZnWiYyujsqAg / getChatAdministrators?chat_id = -1001377692313

def make_response(j):
    image = j['data']['Page']['media'][0]['coverImage']['extraLarge']
    url = j['data']['Page']['media'][0]['siteUrl']
    title = j['data']['Page']['media'][0]['title'].values()
    title = " \n".join(title)
    genres = ", ".join(j['data']['Page']['media'][0]['genres'])
    description = j['data']['Page']['media'][0]['description']
    msg = f"""  <b>{title}</b>
    
                        <a href="{image}">&#8205;</a>
                        <a href="{url}">::link::</a>
                        <pre language="python">{genres}</pre>
                        {description.replace("<br>", "")}"""
    return msg


@bot.message_handler(regexp='(?:{(.+)}|\[(.+)])')
def bot_anilist_search(message):
    match = re.findall(r'\[(.+)]', message.text)  # serches for  [anime name]
    if len(match) > 0:
        anime_match, = match
        json_dict = anilist_search(anime_match, True)
        if json_dict is None:
            msg = f"sorry {message.from_user.first_name} , {anime_match} is not an anime"
        else:
            msg = make_response(json_dict)
        bot.send_message(message.chat.id, msg, parse_mode='HTML')
    match = re.findall(r'\{(.+)}', message.text)  # serches for {manga name}
    if len(match) > 0:
        manga_match, = match
        json_dict = anilist_search(manga_match, False)
        msg = make_response(json_dict) if json_dict is not None else f"sorry {message.from_user.first_name} , {manga_match} is not a manga"
        bot.send_message(message.chat.id, msg, parse_mode='HTML')


# @bot.message_handler(func=lambda x: len(REFERENCES_TREGER_set & {x}) > 0)
# @bot.message_handler(regexp=f"(?i){REFERENCES_TRIGGER}")
@bot.message_handler(func=lambda message: True if REFERENCES_TRIGGER.match(message.text) else False)
def on_reference_match(message):
    reference = REFERENCES_TRIGGER.findall(message.text)
    for ref in reference:
        bot.reply_to(message, ANIME_REFERENCES[ref.lower()], parse_mode='HTML')



while True:
    try:
        bot.polling(none_stop=True)
        # ConnectionError and ReadTimeout because of possible timout of the requests library
        # maybe there are others, therefore Exception
    except Exception:
        time.sleep(15)
    except KeyboardInterrupt:
        print("saving before exit")
        with open("Data.json", "w") as file:
            data["last_updated"] = time.ctime()
            json.dumps(data, indent=2)