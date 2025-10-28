from django.db import models
from django.conf import settings

# Create your models here.
class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ("SUCCESS", "สำเร็จ"),
        ("FAILED", "ล้มเหลว"),
    ]

    student = models.ForeignKey(
        'users.Profile',
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "STUDENT"},
        related_name="payments",
        verbose_name="นิสิต"
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        verbose_name="วิชา"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="FAILED",
        verbose_name="สถานะ"
    )
    transaction_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="รหัสธุรกรรม"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course.code} ({self.status})"