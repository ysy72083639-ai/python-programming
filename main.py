import time
import random
from uno_engine import Deck, Player, COLORS
from database import init_db, save_result, get_rankings

def choose_color_user():
    """와일드 카드 사용 시 색상 선택 (예외 처리 포함)"""
    while True:
        print("\n변경할 색상을 선택하세요: 1.Red  2.Yellow  3.Green  4.Blue")
        choice = input("번호 입력 >> ").strip()
        color_map = {"1": "Red", "2": "Yellow", "3": "Green", "4": "Blue"}
        if choice in color_map:
            return color_map[choice]
        print("⚠️ 잘못된 입력입니다. 1~4 사이의 숫자를 입력하세요.")

def choose_color_ai(ai_player):
    """AI가 가장 많이 보유한 색상 자동 선택"""
    counts = {c: 0 for c in COLORS}
    for card in ai_player.hand:
        if card.color in counts:
            counts[card.color] += 1
    return max(counts, key=counts.get)

def play_game(nickname):
    deck = Deck()
    user = Player(nickname, is_ai=False)
    ai = Player("컴퓨터 AI", is_ai=True)

    # 초기 카드 7장씩 분배
    user.draw_cards(deck, 7)
    ai.draw_cards(deck, 7)

    # 첫 바닥 카드는 일반 숫자 카드로 설정
    discard_pile = []
    while True:
        first_card = deck.draw()
        if first_card.color != "Wild" and first_card.value.isdigit():
            discard_pile.append(first_card)
            break
        deck.cards.insert(0, first_card)

    current_color = discard_pile[-1].color
    turn = 1
    current_turn = "USER"

    print(f"\n🎮 게임을 시작합니다! ({nickname} vs 컴퓨터 AI)")
    time.sleep(1)

    while True:
        top_card = discard_pile[-1]
        print("\n" + "=" * 50)
        print(f"🔄 [Turn {turn}] 현재 바닥 카드: {top_card} (적용 색상: {current_color})")
        print(f"🤖 컴퓨터 AI 남은 카드: {len(ai.hand)}장" + (" 🔥[UNO!]" if ai.has_uno() else ""))
        print("=" * 50)

        # 1. 사용자 턴
        if current_turn == "USER":
            print(f"\n🃏 [{user.name}의 손패] (총 {len(user.hand)}장)" + (" 🔥[UNO!]" if user.has_uno() else ""))
            for idx, card in enumerate(user.hand, start=1):
                playable_mark = "✅" if card.is_playable(top_card, current_color) else "  "
                print(f"  {idx}. {playable_mark} {card}")
            print("  0. 카드 1장 뽑기 (Draw)")

            while True:
                raw = input("\n낼 카드 번호를 선택하세요 (뽑기는 0) >> ").strip()
                if not raw.isdigit():
                    print("⚠️ 숫자만 입력해 주세요.")
                    continue
                choice = int(raw)

                if choice == 0:
                    drawn = deck.draw(discard_pile)
                    user.hand.append(drawn)
                    print(f"📥 카드 1장을 뽑았습니다: {drawn}")
                    current_turn = "AI"
                    break

                if 1 <= choice <= len(user.hand):
                    selected = user.hand[choice - 1]
                    if not selected.is_playable(top_card, current_color):
                        print("⚠️ 바닥 카드와 색상 또는 숫자/기호가 일치하지 않습니다!")
                        continue

                    # 카드 제출 처리
                    user.hand.pop(choice - 1)
                    discard_pile.append(selected)
                    print(f"👉 {user.name}님이 {selected} 카드를 냈습니다!")

                    if user.has_won():
                        print(f"\n🎉 축하합니다! {turn}턴 만에 {user.name}님이 승리했습니다!")
                        save_result(nickname, is_win=True, turns=turn)
                        return

                    # 특수 카드 효과 적용
                    current_turn = apply_card_effect(selected, user, ai, deck, discard_pile, is_user=True)
                    if selected.color == "Wild":
                        current_color = choose_color_user()
                        print(f"🎨 색상이 [{current_color}]로 변경되었습니다!")
                    else:
                        current_color = selected.color
                    break
                else:
                    print(f"⚠️ 0부터 {len(user.hand)} 사이의 번호를 입력하세요.")

        # 2. 컴퓨터 AI 턴
        else:
            print("\n🤖 컴퓨터 AI가 생각 중입니다...")
            time.sleep(1.2)
            playable_cards = [c for c in ai.hand if c.is_playable(top_card, current_color)]

            if playable_cards:
                # 특수 카드가 있으면 우선 사용
                specials = [c for c in playable_cards if not c.value.isdigit()]
                selected = random.choice(specials if specials else playable_cards)
                ai.hand.remove(selected)
                discard_pile.append(selected)
                print(f"👉 컴퓨터 AI가 {selected} 카드를 냈습니다!")

                if ai.has_won():
                    print(f"\n😢 아쉽습니다! 컴퓨터 AI가 {turn}턴 만에 승리했습니다.")
                    save_result(nickname, is_win=False, turns=turn)
                    return

                current_turn = apply_card_effect(selected, ai, user, deck, discard_pile, is_user=False)
                if selected.color == "Wild":
                    current_color = choose_color_ai(ai)
                    print(f"🎨 AI가 색상을 [{current_color}]로 변경했습니다!")
                else:
                    current_color = selected.color
            else:
                drawn = deck.draw(discard_pile)
                ai.hand.append(drawn)
                print("📥 컴퓨터 AI가 낼 카드가 없어 1장을 뽑았습니다.")
                current_turn = "USER"

        turn += 1
        time.sleep(0.8)

def apply_card_effect(card, actor, opponent, deck, discard_pile, is_user):
    """특수 카드 효과 처리 및 다음 턴 반환"""
    next_turn = "AI" if is_user else "USER"
    same_turn = "USER" if is_user else "AI"

    if card.value in ["Skip", "Reverse"]:
        print(f"⏭️ [{card.value}] 효과! {opponent.name}의 턴을 건너뛰고 한 번 더 진행합니다.")
        return same_turn
    elif card.value == "+2":
        opponent.draw_cards(deck, 2, discard_pile)
        print(f"💥 [+2] 효과! {opponent.name}에게 카드 2장을 지급하고 턴을 넘깁니다.")
        return same_turn
    elif card.value == "Wild +4":
        opponent.draw_cards(deck, 4, discard_pile)
        print(f"💣 [Wild +4] 효과! {opponent.name}에게 카드 4장을 지급하고 턴을 넘깁니다.")
        return same_turn
    return next_turn

def show_rankings():
    print("\n" + "=" * 55)
    print("🏆 명예의 전당 (역대 승수 & 최단 턴 TOP 5)")
    print("=" * 55)
    rows = get_rankings()
    if not rows:
        print("아직 저장된 전적이 없습니다. 첫 게임을 플레이해 보세요!")
    else:
        print(f"{'순위':<4} {'닉네임':<12} {'승리':<6} {'패배':<6} {'최소턴':<8} {'최근플레이'}")
        print("-" * 55)
        for idx, (nick, wins, losses, min_t, updated) in enumerate(rows, start=1):
            min_str = f"{min_t}턴" if min_t < 999 else "-"
            print(f"{idx:<4} {nick:<12} {wins:<6} {losses:<6} {min_str:<8} {updated}")
    print("=" * 55)

def main():
    init_db()
    print("=" * 45)
    print("   🃏 PYTHON UNO CARD GAME (with SQLite3)   ")
    print("=" * 45)
    nickname = input("플레이어 닉네임을 입력하세요 >> ").strip() or "Player1"

    while True:
        print(f"\n[{nickname}님 환영합니다!] 메뉴를 선택하세요:")
        print("1. 게임 시작 (1:1 AI 대전)")
        print("2. 랭킹 및 전적 조회 (DB)")
        print("3. 종료")
        menu = input("선택 >> ").strip()

        if menu == "1":
            play_game(nickname)
        elif menu == "2":
            show_rankings()
        elif menu == "3":
            print("게임을 종료합니다. 감사합니다!")
            break
        else:
            print("⚠️ 1, 2, 3 중에서 선택해 주세요.")

if __name__ == "__main__":
    main()