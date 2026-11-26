"""ASCIIスキー：リアルタイム入力とスクロールを学ぶ教材。Windows端末用。"""
import os
import random
import sys
import time

WIDTH = 29
HEIGHT = 16
START_INTERVAL = 0.32
MIN_INTERVAL = 0.085


def get_key():
    """Windowsの非ブロッキングキー入力。通常のターミナルで動作させる。"""
    import msvcrt
    if not msvcrt.kbhit():
        return None
    key = msvcrt.getwch()
    if key in ("\x00", "\xe0"):
        special = msvcrt.getwch()
        return "left" if special == "K" else "right" if special == "M" else None
    return key.lower(  )

 def start_game():
   return {"player_x": WIDTH // 2, "direction": 1, "distance": 0,
            "speed": START_INTERVAL, "alive": True, "running": False,
            "field": [" " * WIDTH for _ in range(HEIGHT)], "score": 0, "lives": 3}


def make_row(distance):
    """障害物のある新しい行を作る。A=木、*=崖。"""
    row = [" "] * WIDTH
    chance = min(0.36, 0.10 + distance / 800)
    if random.random() < chance:
        row[random.randrange(WIDTH)] = random.choice(("A", "A", "*"))
    if random.random() < chance / 3:
        pos = random.randrange(WIDTH)
        if row[pos] == " ":
            row[pos] = "A"
        if random.random() < 0.25:          # 
            pos = random.randrange(WIDTH)
        if row[pos] == " ":
            row[pos] = "$"

    return "".join(row)


def update_game(game):
    if not game["running"] or not game["alive"]:
        return
    # プレイヤーは左右どちらかへ滑り続ける。方向を切り替えて回避する。
    nx = game["player_x"] + game["direction"]
    if nx < 0 or nx >= WIDTH:
        game["alive"] = False
            game["score"] += 10  
    game["player_x"] = nx
    game["field"].pop()
    game["field"].insert(0, make_row(game["distance"]))
    game["distance"] += 1
    game["score"] = game["distance"] * 10
    game["speed"] = max(MIN_INTERVAL, START_INTERVAL - game["distance"] * 0.001)
        cell = game["field"][HEIGHT - 1][game["player_x"]]
    if cell in ("A", "*"):
        game["lives"] -= 1
        if game["lives"] == 0:
            game["alive"] = False


def draw_game(game):
    # ANSIのカーソル移動で画面を上書きする。Windows Terminal/VS Code推奨。
    sys.stdout.write("\x1b[H")
    print("=== ASCII SKI ===".ljust(WIDTH + 2))
    for y in range(HEIGHT):
        line = list(game["field"][y])
        if y == HEIGHT - 1:
            line[game["player_x"]] = "O" if game["alive"] else "X"
        print("|" + "".join(line) + "|")
    print("+" + "-" * WIDTH + "+")
    print(f"距離 {game['distance']:<5} 得点 {game['score']:<6} 速度 {1/game['speed']:.1f}行/秒    ")
    status = ("ゲームオーバー [R]でリスタート" if not game["alive"]
              else "滑走中" if game["running"] else "[Space]でスタート")
        print(f"残りライフ {game['lives']}    ")
    print(status.ljust(WIDTH + 22))
    print("← →: 方向変更  Space: 開始/停止  R: 再開  Q: 終了".ljust(WIDTH + 22))
    sys.stdout.flush()


def main():
    if os.name != "nt":
        print("この版のスキーゲームはWindowsのVS Codeターミナル用です。")
        return
    # Windows 10/11のVS Code内蔵ターミナルを想定
    os.system("")
    game = start_game()
    sys.stdout.write("\x1b[2J\x1b[?25l")
    try:
        while True:
            key = get_key()
            if key in ("q", "\x1b"):
                break
            if key == "r":
                game = start_game()
            elif key == " ":
                if game["alive"]:
                    game["running"] = not game["running"]
            elif key in ("left", "a"):
                game["direction"] = -1
            elif key in ("right", "d"):
                game["direction"] = 1
            if game["running"]:
                update_game(game)
            draw_game(game)
            time.sleep(game["speed"] if game["running"] else 0.08)
    finally:
        sys.stdout.write("\x1b[?25h\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
