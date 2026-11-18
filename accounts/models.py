from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model for POCKET E-Commerce Platform.
    Supports both customers and administrative staff.
    """
    email = models.EmailField(unique=True, verbose_name="Email Address")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Phone Number")
    is_customer = models.BooleanField(default=True, verbose_name="Is Customer")
    is_pocket_admin = models.BooleanField(default=False, verbose_name="Is Pocket Admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name} ({self.email})" if full_name else self.email


class CustomerAddress(models.Model):
    """
    Saved delivery addresses for customer checkout.
    """
    ADDRESS_TYPE_CHOICES = [
        ('HOME', 'Home (All day delivery)'),
        ('WORK', 'Work (Delivery between 10 AM - 5 PM)'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=120, verbose_name="Full Name")
    phone_number = models.CharField(max_length=15, verbose_name="Mobile Number")
    alternate_phone = models.CharField(max_length=15, blank=True, verbose_name="Alternate Phone")
    address_line_1 = models.CharField(max_length=255, verbose_name="Flat, House no., Building, Company, Apartment")
    address_line_2 = models.CharField(max_length=255, blank=True, verbose_name="Area, Street, Sector, Village")
    landmark = models.CharField(max_length=150, blank=True, verbose_name="Landmark")
    city = models.CharField(max_length=100, verbose_name="City / Town")
    state = models.CharField(max_length=100, verbose_name="State")
    pincode = models.CharField(max_length=10, verbose_name="PIN Code")
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='HOME')
    is_default = models.BooleanField(default=False, verbose_name="Default Address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Address"
        verbose_name_plural = "Customer Addresses"
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses for this user to is_default=False
            CustomerAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.pincode}"

    def to_snapshot(self):
        """Returns snapshot dictionary to store inside immutable Order records."""
        return {
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'alternate_phone': self.alternate_phone,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'landmark': self.landmark,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'address_type': self.address_type,
        }
