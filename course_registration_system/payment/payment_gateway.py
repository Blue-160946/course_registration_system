import random

class FakePaymentGateway:
    """
    Mock Payment Gateway แบบง่าย ๆ
    - ทุกวิชาฟรี (fee=0) จะ fail เพื่อสาธิต regression
    - ทุกวิชาที่มีค่าใช้จ่าย (fee>0) จะ success
    """
    @staticmethod
    def charge(student, amount):
        if amount == 0:
            return {"success": False, "transaction_id": "FREE-COURSE"}
        return {"success": True, "transaction_id": "TXN-DETERMINISTIC"}

