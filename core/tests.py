from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Merchant, LedgerEntry

class PayoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.merchant = Merchant.objects.create(name="Test")
        LedgerEntry.objects.create(
            merchant=self.merchant,
            amount_paise=50000,
            type='credit'
        )

    def test_idempotency(self):
        url = "/api/payouts/"
        headers = {"HTTP_IDEMPOTENCY_KEY": "abc123"}

        data = {
            "merchant_id": self.merchant.id,
            "amount_paise": 20000
        }

        res1 = self.client.post(url, data, format='json', **headers)
        res2 = self.client.post(url, data, format='json', **headers)

        self.assertEqual(res1.data["payout_id"], res2.data["payout_id"])
        # 👉 PASTE TEST 2 HERE
    def test_insufficient_balance(self):
        url = "/api/payouts/"
        headers = {"HTTP_IDEMPOTENCY_KEY": "xyz"}

        data = {
            "merchant_id": self.merchant.id,
            "amount_paise": 100000  # more than balance
        }

        res = self.client.post(url, data, format='json', **headers)

        self.assertIn("error", res.data)