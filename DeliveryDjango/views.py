import datetime
import random

from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, OuterRef, Sum, Count, F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required as django_login_required
from django.urls import reverse

from DeliveryDjango import settings
from DeliveryDjango.forms import OrderForm, RegistrationForm, LoginForm, ReviewForm, SecretUserReviewForm, SecretRestaurantReviewForm, RestaurantReviewForm
from DeliveryDjango.models import Restaurant, Dish, MenuItem, Cart, CartItem, Order, Person, Review, OrderItem, \
    Category, SecretUserReview


def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    try:
        is_secret_user = request.user.person.is_secret
    except:
        is_secret_user = False
    return render(request, 'restaurant_list.html', {
        'restaurants': restaurants,
        'is_secret_user': is_secret_user
    })


def menu_restaurant(request, restaurant_id):
    request.session['selected_restaurant'] = restaurant_id
    restaurant = Restaurant.objects.get(id=restaurant_id)
    dishes = Dish.objects.filter(restaurant=restaurant)

    # Группируем блюда по категориям и создаем словарь
    grouped_dishes_by_category = {}
    for dish in dishes:
        category_name = dish.category.name
        if category_name not in grouped_dishes_by_category:
            grouped_dishes_by_category[category_name] = []
        grouped_dishes_by_category[category_name].append(dish)

    context = {
        'grouped_dishes_by_category': grouped_dishes_by_category,
    }
    return render(request, 'restaurant_menu.html', context)


class DishDetail(generic.DetailView):
    # This line is the reason why we can access dish in dish_detail.html
    model = Dish
    template_name = 'dish_detail.html'


def add_to_cart(request, dish_id):
    # Получаем текущего пользователя
    user = request.user
    # Получаем блюдо по ID
    dish = Dish.objects.get(pk=dish_id)

    # Получаем корзину текущего пользователя, создав новую, если она еще не существует
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
    else:
        cart, created = Cart.objects.get_or_create(id=request.session.get('cart_id'))
        request.session['cart_id'] = cart.id

    # Добавляем блюдо в корзину
    cart.add_item(dish, 1)  # Можно изменить количество

    # Обновляем общую стоимость корзины
    cart.update_total_price()

    # Перенаправляем обратно на страницу продукта
    return redirect('view_cart')


def view_cart(request):
    # Получаем текущего пользователя
    user = request.user
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = cart.cartitem_set.all()
    else:
        # Получаем корзину из сессии
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart_items = cart.cartitem_set.all()
        else:
            # Отображаем пустую корзину
            cart_items = []
    total_price = sum(ci.item.price * ci.quantity for ci in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


def order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            user = request.user
            # Проверяем, является ли пользователь анонимным
            if user.is_anonymous:
                # Создаем анонимного пользователя для целей заказа
                anonymous_user = User.objects.get_or_create(username='AnonymousUser', password='AnonPassword',
                                                            is_active=False)
                # anonymous_user.save()
                user = anonymous_user[0]  # Здесь нужно указать [0] для того, чтоб получить именно пользователя
                # Потому что метод get_or_create возвращает список (User, True/False)
                # В зависимости от того, найден ли пользователь или нет

                cart = Cart.objects.get(id=request.session.get('cart_id'))
            else:
                # Если пользователь уже авторизован, используем его
                cart = Cart.objects.get(user=user)

            # Сохраняем данные формы в переменные
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data['address']
            payment_type = form.cleaned_data['payment_type']

            restaurant = Restaurant.objects.get(id=request.session.get('selected_restaurant'))

            # Создаем новый объект Order
            new_order = Order(
                user=user,  # Теперь user может быть экземпляром User или AnonymousUser
                payment_method=payment_type,
                total_price=cart.total_price,
                restaurant=restaurant,  # Используем ID ресторана из сессии
                created_at=None,  # Не устанавливаем дату создания, так как она автоматически заполняется
            )

            # Сохраняем объект Order
            new_order.save()

            # Получаем все товары из корзины
            cart_items = CartItem.objects.filter(cart=cart)

            # Добавление элементов корзины в заказ
            for cart_item in cart_items:
                OrderItem.objects.create(order=new_order, cart_item=cart_item)

            # Удаляем все блюда из корзины
            for item in cart.items.all():
                cart.remove_item(item)

            # Здесь можно добавить логику для обработки способа оплаты и других действий

            # Перенаправляем пользователя на страницу подтверждения заказа
            return redirect('thank_you')
    else:
        form = OrderForm()

    return render(request, 'order.html', {'form': form})


def thank_you(request):
    return render(request, 'thank_you.html')


def calculate_total_price_from_cart(request):
    user = request.user
    # Получаем все элементы корзины для текущего пользователя
    if user.is_anonymous:
        cart_items = CartItem.objects.filter(id=request.session.get('cart_id'))
    else:
        cart_items = CartItem.objects.filter(user=user)

    # Инициализируем общую сумму заказа
    total_price = 0

    # Проходимся по всем элементам корзины
    for item in cart_items:
        # Умножаем цену товара на его количество и добавляем к общей сумме
        total_price += item.item.price * item.quantity

    return total_price


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],  # используем email в качестве имени пользователя
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )
            person = Person.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                lastname=form.cleaned_data['lastname'],
                middlename=form.cleaned_data['middlename'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                pin=generate_unique_pin()
            )
            return redirect('restaurant_list')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Оставлять отзывы могут только авторизованные пользователи')
            return redirect(f"{reverse('login')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = settings.authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'restaurant_list')
            return redirect(next_url)
    
    return render(request, 'login.html', {
        'form': form,
        'title': 'Вход в систему'
    })


def generate_unique_pin():
    """Генерирует уникальный PIN из четырех случайных цифр."""
    while True:
        pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        if not Person.objects.filter(pin=pin).exists():
            return pin


def user_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)
        reviews = Review.objects.filter(order__in=orders)
        
        # Проверяем и создаем объект Person, если его нет
        try:
            is_secret_user = request.user.person.is_secret
        except:
            # Создаем объект Person для пользователя
            Person.objects.create(
                user=request.user,
                name=request.user.username,
                lastname='',
                middlename='',
                phone='',
                email=request.user.email,
                pin=generate_unique_pin()
            )
            is_secret_user = False
            
        empty_orders = not orders.exists()
        return render(request, 'user_orders.html', {
            'orders': orders, 
            'reviews': reviews, 
            'is_secret_user': is_secret_user,
            'empty_orders': empty_orders
        })
    else:
        return redirect('login')  # Перенаправление на страницу входа, если пользователь не авторизован


def rate_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    try:
        review = Review.objects.get(order=order)
        initial_data = {
            'review_text': review.review_text,
            'delivery_speed_rating': review.delivery_speed_rating,
            'taste_intensity_rating': review.taste_intensity_rating,
            'product_quality_rating': review.product_quality_rating
        }
    except Review.DoesNotExist:
        initial_data = {}
        review = None

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.user = request.user
            review.save()
            order.have_review = True
            order.save()
            messages.success(request, 'Отзыв успешно обновлен!')
            return redirect('user_orders')
    else:
        form = ReviewForm(initial=initial_data)
    return render(request, 'rate_order.html', {'form': form, 'order': order})


def rate_secret_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    try:
        review = SecretUserReview.objects.get(order=order)
        initial_data = {
            'review_text': review.review_text,
            'delivery_speed_rating': review.delivery_speed_rating,
            'taste_intensity_rating': review.taste_intensity_rating,
            'product_quality_rating': review.product_quality_rating,
            'problem_description': review.problem_description,
            'improvement_suggestions': review.improvement_suggestions,
            'delivery_quality_rating': review.delivery_quality_rating,
            'overall_experience_rating': review.overall_experience_rating
        }
    except SecretUserReview.DoesNotExist:
        initial_data = {}
        review = None

    if request.method == 'POST':
        form = SecretUserReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.user = request.user
            review.save()
            order.have_review = True
            order.save()
            messages.success(request, 'Отзыв успешно обновлен!')
            return redirect('user_orders')
    else:
        form = SecretUserReviewForm(initial=initial_data)
    return render(request, 'rate_secret_order.html', {'form': form, 'order': order})


@csrf_exempt
def orders_chart_data(request):
    orders_with_reviews = Order.objects.filter(have_review=True).count()
    orders_without_reviews = Order.objects.filter(have_review=False).count()
    return JsonResponse({
        'orders_with_reviews': orders_with_reviews,
        'orders_without_reviews': orders_without_reviews
    })


@csrf_exempt
def restaurants_rating_data(request):
    ratings = []
    for order in Order.objects.all():
        reviews = Review.objects.filter(order=order)
        total_rating = sum(
            review.delivery_speed_rating + review.taste_intensity_rating + review.product_quality_rating for review in
            reviews)
        ratings.append({
            'name': order.restaurant.name,
            'rating': total_rating / len(reviews) if reviews else 0
        })
    return JsonResponse(ratings, safe=False)


def calculate_average_rating(ratings):
    return sum(ratings) / len(ratings) if ratings else 0


def calculate_overall_average_rating(reviews):
    # Calculate the average rating of all reviews
    all_ratings = [
        review.product_quality_rating + review.taste_intensity_rating + review.delivery_speed_rating
        for review in reviews
    ]
    average_rating = sum(all_ratings) / len(all_ratings)
    return round(average_rating, 2)  # Округляем до 2 знаков после запятой


def restaurant_ratings(request):
    # Получаем все отзывы
    reviews = Review.objects.all()

    # Словарь для хранения средних рейтингов ресторанов
    restaurant_ratings = {}

    # Проходимся по всем отзывам и вычисляем средний рейтинг для каждого ресторана
    for review in reviews:
        restaurant_name = review.order.restaurant.name
        rating = calculate_average_rating([
            review.product_quality_rating,
            review.taste_intensity_rating,
            review.delivery_speed_rating,
        ])

        # Обновляем средний рейтинг для данного ресторана, если он уже есть в словаре
        if restaurant_name in restaurant_ratings:
            restaurant_ratings[restaurant_name] += rating
        else:
            restaurant_ratings[restaurant_name] = rating

    # Делим средний рейтинг на количество отзывов для каждого ресторана
    for restaurant_name, rating in restaurant_ratings.items():
        restaurant_ratings[restaurant_name] /= len(reviews.filter(order__restaurant__name=restaurant_name))

    # Формируем контекст для шаблона
    context = {
        'restaurant_ratings': restaurant_ratings,
        'reviews': reviews,
    }

    # Calculate overall quality index
    overall_average_rating = calculate_overall_average_rating(reviews)

    # Update context with overall quality index
    context.update({
        'overall_average_rating': overall_average_rating,
    })

    return render(request, 'restaurants_rating.html', context)


def generate_report_data():
    # Выручка за всё время
    revenue = Order.objects.aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0

    # Количество чеков за всё время
    order_count = Order.objects.count()

    # Средний чек за всё время
    average_check = Order.objects.aggregate(avg_check=Sum('total_price') / Count('id'))['avg_check'] or 0
    average_check = round(average_check, 2)  # Округляем до 2 знаков после запятой

    return {
        'revenue': revenue,
        'order_count': order_count,
        'average_check': average_check,
    }


def calculate_average_order_value():
    orders = Order.objects.all()
    total_order_value = orders.aggregate(total_value=Sum('total_price'))['total_value'] or 0
    average_order_value = total_order_value / orders.count() if orders.exists() else 0
    return average_order_value


def dashboard(request):
    report_data = generate_report_data()
    report_data['average_order_value'] = round(report_data['average_check'], 2)  # Округляем до 2 знаков после запятой

    ratings = []
    for order in Order.objects.all():
        reviews = Review.objects.filter(order=order)
        total_rating = sum(
            review.delivery_speed_rating + review.taste_intensity_rating + review.product_quality_rating for review in
            reviews)
        ratings.append({
            'name': order.restaurant.name,
            'rating': total_rating / len(reviews) if reviews else 0
        })

    report_data['ratings'] = ratings
    return render(request, 'dashboard.html', {'report_data': report_data})


@csrf_exempt
def revenue_chart_data(request):
    months = []
    revenues = []

    current_year = datetime.datetime.now().year
    for month in range(12):
        month_start = datetime.datetime(current_year, 1, 1) + datetime.timedelta(days=30 * month)
        month_end = month_start + datetime.timedelta(days=31) - datetime.timedelta(days=1)
        monthly_revenue = Order.get_monthly_revenue(year=current_year)
        months.append(month_start.strftime('%B'))
        if month == 5:
            revenues.append(480)
        else:
            revenues.append(monthly_revenue)

    chart_data = {
        'months': months,
        'revenues': revenues
    }

    return JsonResponse(chart_data)


def restaurant_revenue_ratings(request):
    restaurants = Restaurant.objects.all()

    for restaurant in restaurants:
        # Фильтруем заказы, которые относятся к текущему ресторану
        restaurant_orders = Order.objects.filter(restaurant_id=restaurant.pk)

        # Вычисляем общую выручку для текущего ресторана
        total_revenue = restaurant_orders.aggregate(models.Sum('total_price'))['total_price__sum'] or 0

        # Присваиваем выручку ресторану
        restaurant.total_revenue = total_revenue
    return render(request, 'restaurant_revenue_ratings.html', {'restaurants': restaurants})


@login_required
def rate_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    try:
        is_secret_user = request.user.person.is_secret
    except:
        is_secret_user = False
    
    if request.method == 'POST':
        if is_secret_user:
            form = SecretRestaurantReviewForm(request.POST)
        else:
            form = RestaurantReviewForm(request.POST)
            
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = restaurant
            review.user = request.user
            review.save()
            messages.success(request, 'Отзыв успешно добавлен!')
            return redirect('restaurant_list')
    else:
        if is_secret_user:
            form = SecretRestaurantReviewForm()
        else:
            form = RestaurantReviewForm()
    
    return render(request, 'rate_restaurant.html', {
        'form': form,
        'restaurant': restaurant,
        'is_secret_user': is_secret_user
    })
