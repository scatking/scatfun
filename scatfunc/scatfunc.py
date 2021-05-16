import requests
from bs4 import BeautifulSoup
import re
from retrying import retry


def html2bb(data):
    data = re.sub('< *br *\/*>', "\n\n", data)
    data = re.sub('< *b *>', "[b]", data)
    data = re.sub('< *\/ *b *>', "[/b]", data)
    data = re.sub('< *u *>', "[u]", data)
    data = re.sub('< *\/ *u *>', "[/u]", data)
    data = re.sub('< *i *>', "[i]", data)
    data = re.sub('< *\/ *i *>', "[/i]", data)
    data = re.sub('< *strong *>', "[b]", data)
    data = re.sub('< *\/ *strong *>', "[/b]", data)
    data = re.sub('< *em *>', "[i]", data)
    data = re.sub('< *\/ *em *>', "[/i]", data)
    data = re.sub('< *li *>', "[*]", data)
    data = re.sub('< *\/ *li *>', "", data)
    data = re.sub(r'< *ul *class=\\*\"bb_ul\\*\" *>', "", data)
    data = re.sub('< *\/ *ul *>', "", data)
    data = re.sub('< *h2 *class=\"bb_tag\" *>', "\n[center][u][b]", data)
    data = re.sub('< *h[12] *>', "\n[center][u][b]", data)
    data = re.sub('< *\/ *h[12] *>', "[/b][/u][/center]\n", data)
    data = re.sub('\&quot;', "\"", data)
    data = re.sub('\&amp;', "&", data)
    data = re.sub('< *img *src="([^"]*)".*>', "\n", data)
    data = re.sub('< *a [^>]*>', "", data)
    data = re.sub('< *\/ *a *>', "", data)
    data = re.sub('< *p *>', "\n\n", data)
    data = re.sub('< *\/ *p *>', "", data)
    data = re.sub('', "\"", data)
    data = re.sub('', "\"", data)
    data = re.sub('  +', " ", data)
    data = re.sub('\n +', "\n", data)
    data = re.sub('\n\n\n+', '\n\n', data)
    data = re.sub('\n\n\n+', '\n\n', data)
    data = re.sub('\[\/b\]\[\/u\]\[\/align\]\n\n', "[/b][/u][/align]\n", data)
    data = re.sub('\n\n\[\*\]', "\n[*]", data)
    return data


def html2bb2(data):
    s = requests.session()
    url = 'https://html2bbcode.ru/converter/'
    cookies = requests.utils.dict_from_cookiejar(s.get(url).cookies)
    data = {'csrfmiddlewaretoken': cookies['csrftoken'], 'html': data}
    bbcode = s.post(url, data=data).text
    bbcode_soup = BeautifulSoup(bbcode, 'lxml')
    return bbcode_soup.select_one('#bbcode').text


def steam_api(game):
    if 'http' in game:
        game = re.search(r'/app/(\d+)', game).group(1)

    @retry(stop_max_attempt_number=4)
    def get_sp_data():
        return requests.get('https://store.steampowered.com/api/appdetails?appids={}'.format(game)).json()[game]['data']

    try:
        gameinfo = \
            requests.get('https://store.steampowered.com/api/appdetails?l=schinese&appids={}'.format(game)).json()[
                game][
                'data']
        ban_china = ''
    except KeyError:
        gameinfo = get_sp_data()
        ban_china = '[size=5][color=#ff0000]注意：锁国区[/color][/size=5]'
    gameinfo2 = requests.get(
        'https://api.rhilip.info/tool/movieinfo/gen?url=https://store.steampowered.com/app/{}'.format(game)).json()
    type = gameinfo['type'].upper().replace('GAME', '游戏本体')
    date = gameinfo['release_date']['date']
    year = re.search(r'\d{4}', date.split("年")[0]).group(0)
    store = 'https://store.steampowered.com/app/{}'.format(game)
    genres = ''
    for genre in gameinfo['genres']:
        genres += '{},'.format(genre['description'])
    screens = ''
    for screen in gameinfo['screenshots'][:3]:
        screen = screen['path_thumbnail'].split('?')[0]
        screens += '[img]{}[/img]\n'.format(screen)
    screens = "[center][b][u]游戏截图[/u][/b][/center]\n" + "[center]" + screens + "[/center]"
    try:
        trailer = "\n\n[center][b][u]预告欣赏[/u][/b][/center]\n[center][video]{}[/video][/center]\n".format(
            gameinfo['movies'][0]['webm']['max'].split('?')[0])
    except:
        trailer = ''
    name = gameinfo['name']
    recfield = "\n\n[center][b][u]配置要求[/u][/b][/center]\n\n [quote]\n{}[/quote]".format(gameinfo2['sysreq'][0])
    cover = "[center][img]" + gameinfo["header_image"].split("?")[0] + "[/img][/center]\n"
    about = gameinfo['about_the_game'] if gameinfo['about_the_game'] != '' else gameinfo['detailed_description']
    about = "{}[center][b][u]关于游戏[/u][/b][/center]\n [b]发行日期[/b]：${}\n\n[b]商店链接[/b]：${}\n\n[b]游戏标签[/b]：${}\n\n{}".format(
        cover, date, store, genres, html2bb(about))
    about += recfield + trailer + screens
    return {'name': name, 'year': year, 'about': about}


def epic_api(game):
    def markdown2bb(str):
        if str == '':
            return str
        str = re.sub(r"!\[.*?\.(?:jpg|png)\)\n\n", '', str)
        return str

    if 'http' in game:
        game = re.search('/p/({.+})').group(1)
    gameInfo = requests.get(
        'https://store-content.ak.epicgames.com/api/zh-CN/content/products/{}'.format(game)).json()
    for i in gameInfo['pages']:
        if i['_title'] == "home" or '主页' or 'Home':
            gameInfo = i
            break
    about = gameInfo['data']['about']['description'] if gameInfo['data']['about']['description'] != "" else \
        gameInfo['data']['about']['shortDescription']
    date = gameInfo['data']['meta']['releaseDate']
    about = "[center][b][u]关于游戏[/u][/b][/center]\n [b]发行日期[/b]：{}\n\n {}".format(date, markdown2bb(about))
    screens = ''
    try:
        for screen in gameInfo["data"]["gallery"]["galleryImages"]:
            screens += "[img]" + screen["src"] + "[/img]\n"
    except:
        for screen in gameInfo['_images']:
            screens += "[img]" + screen["src"] + "[/img]\n"
    screens = "[center][b][u]游戏截图[/u][/b][/center]\n" + "[center]" + screens + "[/center]"
    name = "[center][size=6]{}[/size6][/center]\n".format(gameInfo["productName"])
    minimum = '[b]最低配置[/b]\n'
    recommended = '[b]推荐配置[/b]\n'
    for rec in gameInfo["data"]["requirements"]["systems"]:
        if rec['systemType'] == 'Windows':
            recfield = rec['details']
            break
    for rec in recfield:
        minimum += '[b]{}[/b]: {}\n'.format(rec['title'], rec['minimum'])
        recommended += '[b]{}[/b]: {}\n'.format(rec['title'], rec['recommended'])
    recfield = "\n\n[center][b][u]配置要求[/u][/b][/center]\n\n[quote]\n{}\n{}[/quote]\n".format(minimum, recommended)
    age_rate = "[center][b][u]游戏评级[/u][/b][/center]\n"
    pics = ''
    try:
        for pic in gameInfo["data"]["requirements"]["legalTags"]:
            pics += "[img]" + pic["src"] + "[/img]\n"
        age_rate += '[center]${pics}[/center]'.format(pics=pics)
    except:
        age_rate = ''
    cover = "[center][img]" + gameInfo["data"]["about"]["image"]["src"] + "[/img][/center]"
    return [name + cover + about + recfield + age_rate + screens, game]


def indie_nova_api(game_url):
    if 'http' not in game_url:
        game_url = 'https://indienova.com/game/' + game_url
    api_url = 'https://api.rhilip.info/tool/movieinfo/gen'
    try:
        game_info = requests.get(api_url, params={'url': game_url}).json()
    except:
        api_url = 'https://autofill.scatowl.workers.dev'
        game_info = requests.get(api_url, params={'url': game_url}).json()
    cover = "[center][img]" + game_info['cover'] + "[/img][/center]"
    date = game_info['release_date']
    year = date.split('-')[0]
    store = game_url
    genres = ''
    for i in game_info['cat']:
        genres += '{},'.format(i)
    intro = re.search('【基本信息】.+(?=【游戏简介】)', game_info['format'], re.S).group(0).strip()
    about = intro + game_info['descr']
    chinese_name = game_info['chinese_title']
    screenshots = '\n'
    for screen in game_info['screenshot'][:6]:
        screenshots += '[img]{}[/img]\n'.format(screen)
    screenshots = "[center][b][u]游戏截图[/u][/b][/center]\n" + "[center]" + screenshots + "[/center]"
    about = "{}[center][b][u]关于游戏[/u][/b][/center]\n [b]发行日期[/b]：${}\n\n[b]相关链接[/b]：${}\n\n[b]游戏标签[/b]：${}\n\n{}".format(
        cover, date, store, genres, about + screenshots)
    return {"chinese_name": chinese_name, 'year': year, 'about': about}


def cookie2dict(cookie):
    cookies = dict([l.split("=", 1) for l in cookie.split("; ")])
    return cookies


def cookie_to_cookiejar(cookies: str):
    if not hasattr(cookies, "startswith"):
        raise TypeError
    import requests
    cookiejar = requests.utils.cookiejar_from_dict(
        {cookie[0]: cookie[1] for cookie in
         [cookie.split("=", maxsplit=1) for cookie in cookies.split(";")]})
    return cookiejar


def back0day(name, title):
    """该函数用来为猫站游戏区获取去除掉游戏名后的资源
        name为游戏名，而title为种子资源的名称"""
    raw_name = re.sub(r'[+:._–\-\s&]', '', name)
    pattern = '.*?'.join(raw_name)
    pattern = re.compile(pattern, re.I)
    raw_title = re.sub(pattern, '', title)
    raw_title = raw_title.replace('.', ' ').replace('_', ' ').strip()
    raw_title = re.sub(r'(?<=\d) (?=\d)', '.', raw_title)
    return raw_title


if __name__ == '__main__':
    pass
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #     'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    #     'Connection': 'keep-alive',
    #     'Upgrade-Insecure-Requests': '1',
    #     'Pragma': 'no-cache',
    #     'Cache-Control': 'no-cache',
    # }
    #
    # params = (
    #     ('l', 'schinese'),
    #     ('appids', '1034140'),
    # )
    #
    # res = requests.get('https://store.steampowered.com/api/appdetails', headers=headers, params=params).json()
    # data = res['1034140']['data']['about_the_game']
    # data = html2bb(data)
    #
    # print(data)
    # a = back0day('The Sealed Ampoule',' The Sealed Ampoule x64 v1.00')
    # print(a)
    # a = requests.get('https://store.steampowered.com/api/appdetails?l=schinese&appids=1307550').json()['1307550']['data']['about_the_game']
    # a = html2bb2(a)
    # print(a)
