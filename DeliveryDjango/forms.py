from django import forms

from DeliveryDjango.models import Person, Review, SecretUserReview, RestaurantReview, SecretRestaurantReview


class LoginForm(forms.Form):
    email = forms.EmailField(label='Почта', max_length=65)
    password = forms.CharField(label='Пароль', max_length=65, widget=forms.PasswordInput)


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)
    email = forms.EmailField(label='Почта', required=True)
    phone = forms.CharField(label='Номер телефона', max_length=200, required=True)
    name = forms.CharField(label='Имя', max_length=200, required=True)
    lastname = forms.CharField(label='Фамилия', max_length=200, required=True)
    middlename = forms.CharField(label='Отчество', max_length=200, required=True)

    class Meta:
        model = Person
        fields = ['email', 'password1', 'password2', 'phone', 'name', 'lastname', 'middlename']


class OrderForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=200, required=True)
    last_name = forms.CharField(label='Фамилия', max_length=200, required=True)
    phone_number = forms.CharField(label='Номер телефона', max_length=200, required=True)
    address = forms.CharField(label='Адрес для доставки', max_length=200, required=True)
    payment_type = forms.ChoiceField(label='Способ оплаты', choices=[
        ('card', 'Карта'),
        ('cash', 'Наличные'),
    ], required=True)


class ReviewForm(forms.Form):
    review_text = forms.CharField(
        label='Ваш отзыв',
        widget=forms.Textarea(attrs={'rows': 4}),
        required=True
    )
    delivery_speed_rating = forms.IntegerField(
        label='Скорость доставки',
        min_value=1,
        max_value=5,
        required=True
    )
    taste_intensity_rating = forms.IntegerField(
        label='Интенсивность вкуса',
        min_value=1,
        max_value=5,
        required=True
    )
    product_quality_rating = forms.IntegerField(
        label='Качество продукта',
        min_value=1,
        max_value=5,
        required=True
    )

    def save(self, commit=True):
        review = Review(**self.cleaned_data)
        if commit:
            review.save()
        return review


class SecretUserReviewForm(forms.ModelForm):
    class Meta:
        model = SecretUserReview
        fields = ['review_text', 'delivery_speed_rating', 'taste_intensity_rating', 'product_quality_rating',
                  'problem_description', 'improvement_suggestions', 'delivery_quality_rating', 'overall_experience_rating']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
            'delivery_speed_rating': forms.NumberInput(),
            'taste_intensity_rating': forms.NumberInput(),
            'product_quality_rating': forms.NumberInput(),
            'delivery_quality_rating': forms.NumberInput(),
            'overall_experience_rating': forms.NumberInput(),
            'problem_description': forms.Textarea(),
            'improvement_suggestions': forms.Textarea(),
        }
        labels = {
            'review_text': 'Ваш отзыв',
            'delivery_speed_rating': 'Скорость доставки',
            'taste_intensity_rating': 'Интенсивность вкуса',
            'product_quality_rating': 'Качество продукта',
            'problem_description': 'Описание проблемы',
            'improvement_suggestions': 'Предложения по улучшению',
            'delivery_quality_rating': 'Оценка качества доставки',
            'overall_experience_rating': 'Общая оценка опыта',
        }


class RestaurantReviewForm(forms.ModelForm):
    class Meta:
        model = RestaurantReview
        fields = ['review_text', 'interior_rating', 'service_quality_rating', 'product_quality_rating']
        widgets = {
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'interior_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'service_quality_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'product_quality_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }


class SecretRestaurantReviewForm(forms.ModelForm):
    class Meta:
        model = SecretRestaurantReview
        fields = ['review_text', 'interior_rating', 'service_quality_rating', 'product_quality_rating', 
                 'sanitation_level_rating', 'problem_description', 'improvement_suggestions']
        widgets = {
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'interior_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'service_quality_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'product_quality_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'sanitation_level_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'problem_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'improvement_suggestions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
