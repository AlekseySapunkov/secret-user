import random
from datetime import datetime, timedelta

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, User

from django.db import models
from django.db.models import OneToOneField, Avg

from DeliveryDjango import settings

CATEGORY = (
    ('sweet_pancakes', 'Сладкие блины'),
    ('meet_pancakes', 'Мясные блины'),
    ('sushi', 'Суши'),
    ('desserts', 'Десерты'),
)

AVAILABILITY = (
    (0, 'Unavailable'),
    (1, 'Available'),
)


class Person(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    middlename = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    is_secret = models.BooleanField(default=False)
    pin = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return f"{self.name} {self.lastname} - {self.pin}"


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Dish(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    descr = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pic = models.FileField(upload_to='images/', max_length=200, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Сначала сохраняем модель без изменения файла

    def __str__(self):
        return self.title

    @staticmethod
    def get_display_name(value):
        """Возвращает нормальное название категории."""
        for key, display_name in CATEGORY:
            if key == value:
                return display_name
        return value  # Возвращаем значение, если не найдено соответствующего названия


class Restaurant(models.Model):
    name = models.CharField(max_length=500)
    address = models.CharField(max_length=1000)
    menu = models.ManyToManyField(Dish, through='MenuItem')

    def __str__(self):
        return f"{self.name} - {self.address}"


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price can vary per restaurant
    availability = models.IntegerField(choices=AVAILABILITY, default=1)  # Availability can vary per restaurant

    class Meta:
        unique_together = (
            'restaurant', 'dish')  # Ensures that a dish cannot appear twice in the same restaurant's menu

    def __str__(self):
        return f"{self.restaurant.name} - {self.dish.title}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ManyToManyField(Dish, through='CartItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def add_item(self, item, quantity):
        cart_item, created = CartItem.objects.get_or_create(cart=self, item=item)
        cart_item.quantity += quantity
        cart_item.save()

    def remove_item(self, item):
        CartItem.objects.filter(cart=self, item=item).delete()

    def update_total_price(self):
        self.total_price = sum(cart_item.item.price * cart_item.quantity for cart_item in self.cartitem_set.all())
        self.save()

    def __str__(self):
        return "Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.item.title} x {self.quantity}"


class Order(models.Model):
    CART_CHOICES = [
        ('card', 'Карта'),
        ('cash', 'Наличные'),
    ]
    payment_method = models.CharField(max_length=20, choices=CART_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(CartItem, through='OrderItem')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True)
    have_review = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id}"

    def calculate_total_price(self):
        order_items = CartItem.objects.filter(cart__id=self.payment_method.split('_')[1])
        self.total_price = sum(order_item.item.price * order_item.quantity for order_item in order_items)
        self.save()

    def has_review_from_user(self, user):
        return self.reviews.filter(user=user).exists()

    @classmethod
    def get_monthly_revenue(cls, year=None):
        today = datetime.now()
        start_date = today.replace(day=1) if year is None else datetime(year, 1, 1)
        end_date = start_date + timedelta(days=32) - timedelta(seconds=1)
        monthly_orders = cls.objects.filter(created_at__range=(start_date, end_date))
        return sum(order.total_price for order in monthly_orders)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('order', 'cart_item',)


class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_text = models.TextField()
    delivery_speed_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    taste_intensity_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    product_quality_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"{self.user.username}'s review for {self.order}"


class SecretUserReview(Review):
    problem_description = models.TextField(blank=True, help_text="Описание проблемы")
    improvement_suggestions = models.TextField(blank=True, help_text="Предложения по улучшению")
    delivery_quality_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True, help_text="Оценка качества доставки")
    overall_experience_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True, help_text="Общая оценка опыта")

    class Meta:
        verbose_name = "Скрытый отзыв пользователя"
        verbose_name_plural = "Скрытые отзывы пользователей"


class RestaurantReview(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_text = models.TextField()
    interior_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    service_quality_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    product_quality_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review for {self.restaurant}"


class SecretRestaurantReview(RestaurantReview):
    sanitation_level_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Оценка уровня санитарии")
    problem_description = models.TextField(blank=True, help_text="Описание проблемы")
    improvement_suggestions = models.TextField(blank=True, help_text="Предложения по улучшению")

    class Meta:
        verbose_name = "Скрытый отзыв о ресторане"
        verbose_name_plural = "Скрытые отзывы о ресторанах"
