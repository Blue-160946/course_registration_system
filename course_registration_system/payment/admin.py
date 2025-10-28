from django.contrib import admin
from .models import PaymentTransaction
# Register your models here.

@admin.register(PaymentTransaction)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'amount', 'status', 'transaction_id', 'created_at')
