class InsufficientFundsException(Exception):
    """Виняток, коли недостатньо коштів на рахунку або перевищено ліміт."""
    pass

class CashDispenserEmptyException(Exception):
    """Виняток, коли в банкоматі немає потрібних купюр або готівки загалом."""
    pass

class Card:
    def __init__(self, card_number, pin, balance, credit_limit=0.0, is_credit=False, is_foreign_bank=False):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance
        self.credit_limit = credit_limit
        self.is_credit = is_credit
        self.is_foreign_bank = is_foreign_bank

    def validate_pin(self, entered_pin):
        return self.pin == entered_pin


class ATM:
    def __init__(self, atm_id, cash_cassette):
        self.atm_id = atm_id
        self.cash_cassette = cash_cassette  # Наприклад: {500: 10, 200: 5, 100: 0}

    def authenticate(self, card, pin):
        if not card.validate_pin(pin):
            raise ValueError("Невірний PIN-код")
        return True

    def calculate_fee(self, card, amount):
        """Розрахунок комісії для кредитних карт та карт інших банків."""
        fee = 0.0
        if card.is_foreign_bank:
            fee += amount * 0.015  # 1.5% комісія іншого банку
        if card.is_credit:
            fee += 50.0  # Фіксована комісія за зняття з кредитної карти
        return fee

    def withdraw(self, card, pin, amount):
        """Зняття готівки з урахуванням номіналів та комісії."""
        self.authenticate(card, pin)

        fee = self.calculate_fee(card, amount)
        total_needed = amount + fee

        # 1. Перевірка балансу та кредитного ліміту
        available_funds = card.balance + (card.credit_limit if card.is_credit else 0.0)
        if total_needed > available_funds:
            raise InsufficientFundsException("Недостатньо коштів (враховуючи ліміт та комісію)")

        # 2. Перевірка наявності загальної суми та алгоритм видачі купюр
        total_atm_cash = sum(nom * count for nom, count in self.cash_cassette.items())
        if amount > total_atm_cash:
            raise CashDispenserEmptyException("У банкоматі недостатньо готівки в цілому")

        # Перевіряємо, чи можна набрати суму наявними номіналами
        remaining_amount = amount
        temp_dispense = {}

        for nominal in sorted(self.cash_cassette.keys(), reverse=True):
            available_notes = self.cash_cassette[nominal]
            notes_needed = remaining_amount // nominal
            notes_to_take = min(available_notes, notes_needed)

            if notes_to_take > 0:
                temp_dispense[nominal] = notes_to_take
                remaining_amount -= notes_to_take * nominal

        if remaining_amount > 0:
            raise CashDispenserEmptyException("У банкоматі немає необхідних номіналів купюр для цієї суми")

        # Якщо все успішно — видаємо купюри та списуємо з касети
        for nominal, count in temp_dispense.items():
            self.cash_cassette[nominal] -= count

        card.balance -= total_needed
        return {
            "amount": amount,
            "fee": fee,
            "dispensed_notes": temp_dispense,
            "remaining_balance": card.balance
        }

    def get_balance(self, card, pin):
        """Перегляд балансу."""
        self.authenticate(card, pin)
        return card.balance

    def change_pin(self, card, old_pin, new_pin):
        """Зміна PIN-коду."""
        self.authenticate(card, old_pin)
        if len(new_pin) != 4 or not new_pin.isdigit():
            raise ValueError("Новий PIN має складатися з 4 цифр")
        card.pin = new_pin
        return True

    def refill_cash(self, new_notes):
        """Заправка банкомату купюрами (інкасація)."""
        for nominal, count in new_notes.items():
            if nominal in self.cash_cassette:
                self.cash_cassette[nominal] += count
            else:
                self.cash_cassette[nominal] = count