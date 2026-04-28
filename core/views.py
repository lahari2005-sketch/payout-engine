from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Sum
from .models import Merchant, Payout, LedgerEntry

@api_view(['POST'])
def create_payout(request):
    merchant_id = request.data.get('merchant_id')
    amount = int(request.data.get('amount_paise'))
    key = request.headers.get('Idempotency-Key')

    # Check idempotency
    existing = Payout.objects.filter(
        merchant_id=merchant_id,
        idempotency_key=key
    ).first()

    if existing:
        return Response({
            "message": "Already created",
            "payout_id": existing.id
        })

    with transaction.atomic():
        merchant = Merchant.objects.select_for_update().get(id=merchant_id)

        balance = LedgerEntry.objects.filter(
            merchant=merchant
        ).aggregate(total=Sum('amount_paise'))['total'] or 0

        if balance < amount:
            return Response({"error": "Insufficient balance"})

        payout = Payout.objects.create(
            merchant=merchant,
            amount_paise=amount,
            idempotency_key=key
        )

        LedgerEntry.objects.create(
            merchant=merchant,
            amount_paise=-amount,
            type='hold'
        )

        return Response({
            "message": "Payout created",
            "payout_id": payout.id
        })