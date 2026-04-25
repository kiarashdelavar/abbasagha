class SafetyGuard:
    MAX_SINGLE_ACTION_AMOUNT = 50.00
    MAX_SWEEP_AMOUNT = 500.00

    @staticmethod
    def is_safe_amount(amount: str, max_amount: float):
        try:
            value = float(amount)
            return 0 < value <= max_amount
        except ValueError:
            return False

    @staticmethod
    def validate_sandbox_payment(amount: str):
        if not SafetyGuard.is_safe_amount(amount, SafetyGuard.MAX_SINGLE_ACTION_AMOUNT):
            return {
                "allowed": False,
                "reason": f"Amount must be between 0 and {SafetyGuard.MAX_SINGLE_ACTION_AMOUNT} EUR",
            }

        return {
            "allowed": True,
            "reason": "Sandbox payment is safe",
        }

    @staticmethod
    def validate_sweep_amount(amount: str):
        if not SafetyGuard.is_safe_amount(amount, SafetyGuard.MAX_SWEEP_AMOUNT):
            return {
                "allowed": False,
                "reason": f"Sweep amount must be between 0 and {SafetyGuard.MAX_SWEEP_AMOUNT} EUR",
            }

        return {
            "allowed": True,
            "reason": "Sweep amount is safe",
        }