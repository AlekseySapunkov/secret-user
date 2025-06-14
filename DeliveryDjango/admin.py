from django.contrib import admin

from DeliveryDjango.models import Dish, Restaurant, MenuItem, Cart, Order, Person, Review, OrderItem, Category, SecretUserReview, RestaurantReview, SecretRestaurantReview

admin.site.register(Dish)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Person)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_restaurant_name', 'review_text', 'delivery_speed_rating', 'taste_intensity_rating', 'product_quality_rating')
    list_filter = ('user',)
    search_fields = ('user__username', 'review_text')

    def get_restaurant_name(self, obj):
        if hasattr(obj, 'order'):
            return obj.order.restaurant.name
        elif hasattr(obj, 'restaurant'):
            return obj.restaurant.name
        return '-'
    get_restaurant_name.short_description = 'Ресторан'

@admin.register(SecretUserReview)
class SecretUserReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_restaurant_name', 'review_text', 'delivery_speed_rating', 'taste_intensity_rating', 
                   'product_quality_rating', 'problem_description', 'improvement_suggestions', 
                   'delivery_quality_rating', 'overall_experience_rating')
    list_filter = ('user',)
    search_fields = ('user__username', 'review_text', 'problem_description', 'improvement_suggestions')

    def get_restaurant_name(self, obj):
        if hasattr(obj, 'order'):
            return obj.order.restaurant.name
        elif hasattr(obj, 'restaurant'):
            return obj.restaurant.name
        return '-'
    get_restaurant_name.short_description = 'Ресторан'

@admin.register(RestaurantReview)
class RestaurantReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'review_text', 'interior_rating', 'service_quality_rating', 'product_quality_rating')
    list_filter = ('user', 'restaurant')
    search_fields = ('user__username', 'restaurant__name', 'review_text')

@admin.register(SecretRestaurantReview)
class SecretRestaurantReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'review_text', 'interior_rating', 'service_quality_rating', 
                   'product_quality_rating', 'sanitation_level_rating', 'problem_description', 'improvement_suggestions')
    list_filter = ('user', 'restaurant')
    search_fields = ('user__username', 'restaurant__name', 'review_text', 'problem_description', 'improvement_suggestions')

admin.site.register(OrderItem)
admin.site.register(Category)
