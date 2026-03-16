import requests
import json
import os
from colorama import Fore, Style, init

init(autoreset=True)

CONFIG_FILE = "config.json"


def load_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
            return config["api_key"]

    print("\nВведите ваш Steam API Key.")
    print("Получить его можно тут: https://steamcommunity.com/dev/apikey\n")

    api = input("API Key: ")

    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api}, f)

    return api


def change_api_key():
    print("\nСмена API ключа\n")
    api = input("Введите новый API Key: ")

    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api}, f)

    print(Fore.GREEN + "API ключ успешно обновлен!")


API_KEY = load_api_key()

print("\nВведите SteamID игрока.")
print("Пример: 76561198000000000\n")

STEAM_ID = input("SteamID: ")


def load_stats():
    global stats

    url = f"https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v2/?appid=730&key={API_KEY}&steamid={STEAM_ID}"

    r = requests.get(url)
    data = r.json()

    if "playerstats" not in data:
        print(Fore.RED + "\nОшибка: профиль закрыт или статистика недоступна.")
        exit()

    stats = data["playerstats"]["stats"]


load_stats()


def get_stat(name):
    for s in stats:
        if s["name"] == name:
            return s["value"]
    return 0


def line():
    print("─" * 42)


def header(title):
    line()
    print(Fore.CYAN + Style.BRIGHT + title.center(42))
    line()


def section(title):
    print(Fore.WHITE + "\n" + title)
    print("─" * len(title))


def show_stats():

    kills = get_stat("total_kills")
    deaths = get_stat("total_deaths")
    headshots = get_stat("total_kills_headshot")

    wins = get_stat("total_matches_won")
    matches = get_stat("total_matches_played")

    kd = kills / deaths if deaths != 0 else 0
    winrate = (wins / matches * 100) if matches != 0 else 0

    header("PLAYER STATISTICS")

    print(f"Kills       : {Fore.GREEN}{kills}")
    print(f"Deaths      : {Fore.RED}{deaths}")
    print(f"Headshots   : {Fore.YELLOW}{headshots}")
    print(f"K/D Ratio   : {Fore.CYAN}{round(kd,2)}")
    print(f"Winrate     : {Fore.MAGENTA}{round(winrate,1)}%")


def show_maps():

    maps = {
        "Mirage": get_stat("total_rounds_map_de_mirage"),
        "Inferno": get_stat("total_rounds_map_de_inferno"),
        "Dust2": get_stat("total_rounds_map_de_dust2"),
        "Nuke": get_stat("total_rounds_map_de_nuke"),
        "Overpass": get_stat("total_rounds_map_de_overpass"),
    }

    favorite = max(maps, key=maps.get)

    header("MAP STATISTICS")

    print("Любимая карта определяется по количеству сыгранных раундов.\n")

    for m in maps:

        rounds = maps[m]
        approx_matches = rounds // 24

        print(f"{m:<10} {rounds} rounds  (~{approx_matches} matches)")

    print("\nFavorite map:", Fore.CYAN + favorite)


def show_role():

    kills = get_stat("total_kills")
    deaths = get_stat("total_deaths")
    hs = get_stat("total_kills_headshot")

    kd = kills / deaths if deaths != 0 else 0
    hs_rate = (hs / kills * 100) if kills != 0 else 0

    if kd > 1.4 and hs_rate > 45:
        role = "Aggressive Entry Fragger"
    elif kd > 1.2:
        role = "Rifler"
    elif hs_rate > 40:
        role = "AWPer"
    else:
        role = "Support"

    header("PLAYER ROLE")

    print("Based on your statistics:")
    print("\nYour role:", Fore.CYAN + role)


def show_guns():

    guns = {
        "AK-47": get_stat("total_kills_ak47"),
        "AWP": get_stat("total_kills_awp"),
        "M4A1": get_stat("total_kills_m4a1"),
        "USP-S": get_stat("total_kills_usp_silencer"),
        "Glock": get_stat("total_kills_glock"),
    }

    header("FAVORITE WEAPONS")

    sorted_guns = sorted(guns, key=guns.get, reverse=True)

    for g in sorted_guns:
        print(f"{g:<8} {guns[g]} kills")


def help_menu():

    header("CS2 TRACKER COMMANDS")

    print(" /stats   - показать общую статистику игрока")
    print(" /map     - статистика карт")
    print(" /role    - определить роль игрока")
    print(" /guns    - любимые оружия")
    print(" /apikey  - сменить API ключ")
    print(" /reload  - обновить статистику")
    print(" /help    - показать команды")
    print(" /exit    - выйти из программы")
    print(" /rank   - определить примерный ранг игрока")


help_menu()


def show_rank():

    kills = get_stat("total_kills")
    deaths = get_stat("total_deaths")
    headshots = get_stat("total_kills_headshot")

    kd = kills / deaths if deaths != 0 else 0
    hs_rate = (headshots / kills * 100) if kills != 0 else 0

    if kd > 1.4 and hs_rate > 45:
        role = "Entry Fragger"
    elif kd > 1.2:
        role = "Rifler"
    elif hs_rate > 40:
        role = "AWPer"
    else:
        role = "Support"

    if kd < 0.8:
        rank = "Silver 1"
        color = Fore.LIGHTBLACK_EX
        reason = "низкий K/D и слабая эффективность"

    elif kd < 0.9:
        rank = "Silver 2"
        color = Fore.LIGHTBLACK_EX
        reason = "K/D ниже среднего"

    elif kd < 1.0:
        rank = "Silver 3"
        color = Fore.LIGHTBLACK_EX
        reason = "средняя эффективность и низкий K/D"

    elif kd < 1.1:
        rank = "Silver 4"
        color = Fore.LIGHTBLACK_EX
        reason = "K/D близок к 1.0, но еще мало точности"

    elif kd < 1.2:
        rank = "Silver Elite"
        color = Fore.LIGHTBLACK_EX
        reason = "K/D стабилизируется около 1.0"

    elif kd < 1.3:
        rank = "Silver Elite Master"
        color = Fore.LIGHTBLACK_EX
        reason = "хороший K/D, но недостаточно headshot"

    elif kd < 1.4:
        rank = "Gold Nova 1"
        color = Fore.YELLOW
        reason = "K/D выше среднего"

    elif kd < 1.5:
        rank = "Gold Nova 2"
        color = Fore.YELLOW
        reason = "хорошая эффективность и стабильная игра"

    elif kd < 1.6:
        rank = "Gold Nova 3"
        color = Fore.YELLOW
        reason = "высокий K/D и хорошая роль в команде"

    elif kd < 1.7:
        rank = "Gold Nova Master"
        color = Fore.YELLOW
        reason = "очень стабильный K/D"

    elif kd < 1.9:
        rank = "Master Guardian"
        color = Fore.BLUE
        reason = "высокий K/D и хорошая точность"

    elif kd < 2.1:
        rank = "Distinguished Master Guardian"
        color = Fore.BLUE
        reason = "очень высокий K/D"

    elif kd < 2.3:
        rank = "Legendary Eagle"
        color = Fore.MAGENTA
        reason = "отличный K/D и высокий уровень игры"

    elif kd < 2.6:
        rank = "Legendary Eagle Master"
        color = Fore.MAGENTA
        reason = "очень высокая эффективность"

    elif kd < 3:
        rank = "Supreme Master First Class"
        color = Fore.RED
        reason = "очень высокий K/D и высокий skill"

    else:
        rank = "Global Elite"
        color = Fore.RED
        reason = "экстремально высокий K/D и отличный aim"

    header("PLAYER RANK")

    print("Your estimated rank:")
    print(color + rank)

    print("\nПочему этот ранг:")
    print(f"K/D: {round(kd,2)}")
    print(f"Headshot %: {round(hs_rate,1)}%")
    print(f"Role: {role}")

    print("\nПричина:")
    print(reason)


while True:

    cmd = input(Fore.WHITE + "\n> ")

    if cmd == "/stats":
        show_stats()

    elif cmd == "/map":
        show_maps()

    elif cmd == "/role":
        show_role()

    elif cmd == "/guns":
        show_guns()

    elif cmd == "/apikey":
        change_api_key()

    elif cmd == "/reload":
        load_stats()
        print(Fore.GREEN + "Статистика обновлена")

    elif cmd == "/rank":
        show_rank()

    elif cmd == "/help":
        help_menu()

    elif cmd == "/exit":
        print("Выход...")
        break

    else:
        print("Неизвестная команда. Напишите /help")
