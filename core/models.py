from django.db import models


class ContactInquiry(models.Model):
    """
    Customer support contact inquiries submitted via Contact Us page.
    """
    STATUS_CHOICES = [
        ('NEW', 'New Inquiry'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    name = models.CharField(max_length=120, verbose_name="Your Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    subject = models.CharField(max_length=200, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    admin_response = models.TextField(blank=True, verbose_name="Admin Notes / Response")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.name} ({self.get_status_display()})"


class NewsletterSubscriber(models.Model):
    """
    Email newsletter subscriber (functional, verified).
    """
    email = models.EmailField(unique=True, verbose_name="Subscriber Email")
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
