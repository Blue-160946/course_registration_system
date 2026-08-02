class FakePaymentGateway:
    """
    Payment gateway สำหรับการพัฒนาและทดสอบเท่านั้น

    ต้องตั้ง PAYMENT_GATEWAY_MODE=fake อย่างชัดเจนจึงจะถูกเรียกใช้งาน
    ห้ามใช้ผลลัพธ์หรือ transaction_id จากคลาสนี้เป็นหลักฐานการชำระเงินจริง
    """
    @staticmethod
    def charge(student, amount):
        if amount == 0:
            return {"success": False, "transaction_id": "FREE-COURSE"}
        return {"success": True, "transaction_id": "TXN-DETERMINISTIC"}

