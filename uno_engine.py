import random

COLORS = ["Red", "Yellow", "Green", "Blue"]
VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Skip", "Reverse", "+2"]
WILD_VALUES = ["Wild", "Wild +4"]

class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __str__(self):
        if self.color == "Wild":
            return f"[{self.value}]"
        return f"[{self.color} {self.value}]"

    def is_playable(self, top_card, current_color):
        """현재 바닥 카드(top_card) 및 지정 색상 위에 낼 수 있는지 판별"""
        if self.color == "Wild":
            return True
        if self.color == current_color:
            return True
        if self.value == top_card.value:
            return True
        return False


class Deck:
    def __init__(self):
        self.cards = []
        self.build_deck()
        self.shuffle()

    def build_deck(self):
        self.cards = []
        for color in COLORS:
            for val in VALUES:
                self.cards.append(Card(color, val))
                if val != "0":  # 0을 제외한 카드는 2장씩 구성
                    self.cards.append(Card(color, val))
        for _ in range(4):
            for w_val in WILD_VALUES:
                self.cards.append(Card("Wild", w_val))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, discard_pile=None):
        """덱이 비면 버린 카드 더미를 다시 섞어 보충"""
        if not self.cards:
            if discard_pile and len(discard_pile) > 1:
                top = discard_pile.pop()
                self.cards = discard_pile[:]
                discard_pile.clear()
                discard_pile.append(top)
                self.shuffle()
            else:
                self.build_deck()
                self.shuffle()
        return self.cards.pop()


class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.hand = []

    def draw_cards(self, deck, count=1, discard_pile=None):
        for _ in range(count):
            self.hand.append(deck.draw(discard_pile))

    def has_uno(self):
        return len(self.hand) == 1

    def has_won(self):
        return len(self.hand) == 0