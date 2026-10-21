"""Payment capture validation for the medium-risk demonstration case."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


def normalize_amount(raw_amount: str) -> Decimal:
    """Parse a positive amount with two decimal places."""
    try:
        amount = Decimal(raw_amount).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("amount must be a valid decimal") from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError("amount must be greater than zero")
    return amount


def build_capture_request(account_id: str, raw_amount: str) -> dict[str, str]:
    """Build a validated capture request for the payment provider."""
    account = account_id.strip()
    if not account:
        raise ValueError("account id must not be empty")
    amount = normalize_amount(raw_amount)
    return {"account_id": account, "amount": format(amount, ".2f")}
