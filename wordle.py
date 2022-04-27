import random
import socket
import sys
import time
import requests

from redis_db.session import write_stats, read_stats, cache_exist, write_cache

url = "https://raw.githubusercontent.com/charlesreid1/five-letter-words/master/sgb-words.txt"
try :
    with open(r"docs\words.txt", "r") as f:
        data = f.read()
except FileNotFoundError:
    file_data = requests.get(url)
    with open(r"docs\words.txt", "wb") as f1:
        f1.write(file_data.content)
    with open(r"docs\words.txt", "r") as f2:
        data = f2.read()
word_list = data.split("\n")

def game(user_word, random_word):
    green = []
    word_col = {}
    for i, j in zip(range(5), range(5)):
        if user_word[i] == random_word[j] :
            green.append(i)
    grey = [i for i, j in enumerate(user_word) if j not in random_word]
    yellow = [i for i in range(5) if i not in green+grey]
    print(green, grey, yellow)
    word_col["green"] = [user_word[i] for i in green]
    word_col["yellow"] = [user_word[i] for i in yellow]
    word_col["grey"] = [user_word[i] for i in grey]
    return word_col

def wordle():
    random_index = random.randint(0, len(word_list)-1)
    random_word = word_list[random_index]
    return random_word

def validate_user_word(user_word):
    if user_word not in word_list:
        raise Exception("not a dictionary word")
    if len(user_word) != 5:
        raise Exception("invalid length")

def get_ip():
    host = socket.gethostname()
    ip_add = socket.gethostbyname(host)
    return str(ip_add)

def create_stats(win, attempt = 0, prev_stats=None):
    if prev_stats:
        win_step = prev_stats.get("win_step")
        prev_stats["total_played"]+=1
        if win == 1:
            prev_stats["win"] += 1
            prev_stats["current_streak"] += 1
            if prev_stats["current_streak"] > prev_stats["max_streak"] :
                prev_stats["max_streak"] = prev_stats.get("current_streak")
            win_step[str(attempt)] = win_step.get(str(attempt)) + 1
        else :
            prev_stats["current_streak"] = 0
        prev_stats["win_%"] = (prev_stats["win"] / prev_stats["total_played"]) * 100
        return prev_stats

    win_step = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0}
    if win == 0:
        win_perc = 0
    else :
        win_perc = 100
        win_step[str(attempt)] = win_step.get(str(attempt)) + 1
    current_stats = {
        "win" : win,
        "total_played" : 1,
        "win_%" : win_perc,
        "current_streak" : 1,
        "max_streak" : 1,
        "win_step" : win_step
    }
    return current_stats

if __name__ == '__main__':
    ip = get_ip()
    exists, ttl = cache_exist(ip)
    if exists:
        rem = time.gmtime(ttl)
        res = time.strftime("%H:%M:%S", rem)
        print(f"Next wordle in {res}")
        sys.exit(1)
    random_word = wordle()
    i = 0
    win = 0
    attempt = 0
    prev_stats = read_stats(ip)
    while i < 6:
        user_word = input("Enter Word : ")
        try :
            validate_user_word(user_word)
        except Exception as e:
            print(e.__str__())
            continue
        if user_word == random_word:
            win = 1
            attempt = i+1
            break
        i += 1
        word_col = game(user_word, random_word)
        print(word_col)
    write_cache(ip)
    stats = create_stats(win, attempt, prev_stats=prev_stats)
    print(stats)
    write_stats(ip, stats)

