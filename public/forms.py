from django import forms


class GuestCheckoutForm(forms.Form):
    customer_name = forms.CharField(
        label="Ad Soyad",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ad Soyad"}),
    )
    customer_phone = forms.CharField(
        label="Telefon",
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "05XX XXX XX XX"}),
    )
    customer_email = forms.EmailField(
        label="E-posta",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "ornek@email.com"}),
    )
    delivery_address = forms.CharField(
        label="Teslimat adresi",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Adres"}),
    )
    order_notes = forms.CharField(
        label="Sipariş notu (isteğe bağlı)",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Ad Soyad",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Adınız Soyadınız"}),
    )
    email = forms.EmailField(
        label="E-posta",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "ornek@email.com"}),
    )
    phone = forms.CharField(
        label="Telefon",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "05XX XXX XX XX"}),
    )
    message = forms.CharField(
        label="Mesajınız",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Mesajınızı yazın..."}),
    )
