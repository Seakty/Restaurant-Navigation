from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Existing Restaurant model
class Restaurant(models.Model):
    CATEGORY_CHOICES = [
        ('Chinese', 'Chinese'),
        ('French', 'French'),
        ('Khmer', 'Khmer'),
        ('Italian', 'Italian'),
        ('Japanese', 'Japanese'),
        ('Korean', 'Korean'),
        ('American', 'American'),
        ('Mexican', 'Mexican'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    location = models.CharField(max_length=200)
    google_maps_link = models.URLField(blank=True, null=True)  # New field for Google Maps link
    cuisine = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0, "Rating cannot be negative")]
    )
    image = models.ImageField(upload_to='restaurant_images/', blank=True)

    def __str__(self):
        return self.name

    def get_short_description(self):
        return self.description[:50] + "..." if len(self.description) > 50 else self.description

    def update_rating(self):
        """Recalculate the average rating from related feedbacks."""
        avg_rating = self.feedbacks.aggregate(avg_rating=Avg('rating'))['avg_rating']
        self.rating = avg_rating if avg_rating is not None else 0.0
        self.save()


# New Menu model
class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price with 2 decimal places
    image = models.ImageField(upload_to='menu_images/', blank=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


# Feedback model
class Feedback(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='feedbacks'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    comments = models.TextField(blank=True)
    rating = models.FloatField(
        validators=[
            MinValueValidator(0.0, "Rating cannot be negative"),
            MaxValueValidator(5.0, "Rating cannot exceed 5.0")
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.rating}): {self.restaurant.name}"

    def get_short_comment(self):
        return self.comments[:50] + "..." if len(self.comments) > 50 else self.comments
    
    def customer_name(self):
        return self.user.username

    customer_name.short_description = "Customer Name"

# Signals to update the restaurant rating
@receiver(post_save, sender=Feedback)
def update_restaurant_rating_on_save(sender, instance, **kwargs):
    """Update the restaurant's rating when feedback is saved."""
    instance.restaurant.update_rating()


@receiver(post_delete, sender=Feedback)
def update_restaurant_rating_on_delete(sender, instance, **kwargs):
    """Update the restaurant's rating when feedback is deleted."""
    instance.restaurant.update_rating()
