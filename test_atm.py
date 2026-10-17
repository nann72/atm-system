import unittest
from atm import ATM, Card, InsufficientFundsException, CashDispenserEmptyException

class TestATMFullRequirements(unittest.TestCase):
    def setUp(self):
        # Початковий стан банкомату: є лише по 500 і 200 грн
        self.cassettes = {500: 2, 200: 5, 100: 0} # Всього 2000 грн
        self.atm = ATM("ATM-01", self.cassettes)

        # Картки
        self.regular_card = Card("1111", "1234", balance=1000.0)
        self.foreign_credit_card = Card("2222", "0000", balance=100.0, credit_limit=2000.0, is_credit=True, is_foreign_bank=True)

    # 1. Перевірка перегляду балансу
    def test_get_balance(self):
        self.assertEqual(self.atm.get_balance(self.regular_card, "1234"), 1000.0)

    # 2. Перевірка зміни PIN-коду
    def test_change_pin(self):
        self.assertTrue(self.atm.change_pin(self.regular_card, "1234", "4321"))
        self.assertEqual(self.regular_card.pin, "4321")

    # 3. Перевірка комісії для чужих та кредитних карт
    def test_foreign_credit_card_withdrawal_fee(self):
        # Сума 500 + 1.5% (7.5) + кредитна комісія 50 = 557.5
        res = self.atm.withdraw(self.foreign_credit_card, "0000", 500)
        self.assertEqual(res["fee"], 57.5)

    # 4. Перевірка ситуації: Немає потрібних номіналів (наприклад, просять 300 грн, а є тільки 500 і 200)
    def test_missing_required_nominals(self):
        with self.assertRaises(CashDispenserEmptyException):
            self.atm.withdraw(self.regular_card, "1234", 300)

    # 5. Перевірка заправки купюрами (інкасація) та подальшого зняття
    def test_refill_and_dispense(self):
        # Заправляю банкомат сотнями (100 грн x 10)
        self.atm.refill_cash({100: 10})
        # Тепер 300 грн можна видати (200 + 100)
        res = self.atm.withdraw(self.regular_card, "1234", 300)
        self.assertEqual(res["amount"], 300)

    # 6. Перевірка винятку: Недостатньо коштів на рахунку
    def test_insufficient_funds(self):
        with self.assertRaises(InsufficientFundsException):
            self.atm.withdraw(self.regular_card, "1234", 5000)

if __name__ == "__main__":
    unittest.main()