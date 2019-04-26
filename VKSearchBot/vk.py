import requests
import json

VK_TOKEN = "" #vk token here


def get_id(short_name):
    try:
        info = requests.get(
            "https://api.vk.com/method/utils.resolveScreenName?screen_name={}&access_token={}&v=5.92".format(short_name,
                                                                                                             VK_TOKEN))
        data = info.json()
        return (data["response"])["object_id"]
    except:
        return None


def get_last_post(id):
    try:
        info = requests.get("https://api.vk.com/method/wall.get?owner_id={}&access_token={}&v=5.92".format(str(-id),
                                                                                                           VK_TOKEN))
        data = info.json()
        try:
            if (((data["response"])["items"])[1])["is_pinned"]:
                return (((data["response"])["items"])[0])["id"]
            else:
                return (((data["response"])["items"])[1])["id"]
        except KeyError:
            return (((data["response"])["items"])[0])["id"]
    except:
        return None


def search(last_post, word, group_id):
    info = requests.get("https://api.vk.com/method/wall.get?owner_id={}&access_token={}&v=5.92".format(str(-group_id),
                                                                                                       VK_TOKEN))
    data = info.json()
    try:
        if (((data["response"])["items"])[1])["is_pinned"]:
            current_last_post = (((data["response"])["items"])[0])["id"]
            count = -1
        else:
            current_last_post = (((data["response"])["items"])[1])["id"]
            count = 0
    except KeyError:
        current_last_post = (((data["response"])["items"])[0])["id"]
        count = -1
    if current_last_post == last_post:
        return None
    else:
        posts = []
        while current_last_post != last_post and count != len(((data["response"])["items"])):
            if word.lower() in (((data["response"])["items"])[count])["text"].lower():
                posts.append("vk.com/wall{}_{}\n".format(str(-group_id), current_last_post))
            count += 1
            current_last_post = ((((data["response"])["items"])[count])["id"])
    print(posts)
    return ''.join(posts)

print(get_last_post(78659583))
