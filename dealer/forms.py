from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import BankTransferNotice, DealerProfile, MailOrderRequest, OrderItem, Product


class DealerRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=50, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "company_name", "phone", "address", "password1", "password2")


class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True), empty_label="Select product"
    )

    class Meta:
        model = OrderItem
        fields = ("product", "quantity")


OrderItemFormSet = forms.formset_factory(OrderItemForm, extra=1, min_num=1, validate_min=True)


class MailOrderRequestForm(forms.ModelForm):
    expiry_mmyy = forms.CharField(
        max_length=5,
        required=True,
        label="Son kullanma tarihi (AA/YY)",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Örn: 12/28", "maxlength": "5"}),
    )

    class Meta:
        model = MailOrderRequest
        fields = ("card_holder_name", "card_number", "expiry_mmyy", "cvv", "amount", "phone", "note")
        widgets = {
            "card_holder_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Kartın üzerindeki isim"}),
            "card_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "16 haneli kart numarası", "maxlength": "19", "autocomplete": "cc-number"}),
            "cvv": forms.TextInput(attrs={"class": "form-control", "placeholder": "CVV", "maxlength": "4", "autocomplete": "off"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "İletişim telefonu (isteğe bağlı)"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "İsteğe bağlı not"}),
        }
        labels = {
            "card_holder_name": "Kart üzerindeki isim",
            "card_number": "Kart numarası",
            "cvv": "CVV",
            "amount": "Ödenecek tutar (₺)",
            "phone": "Telefon",
            "note": "Not",
        }

    def clean_expiry_mmyy(self):
        import re
        value = (self.cleaned_data.get("expiry_mmyy") or "").strip()
        if not value:
            raise forms.ValidationError("Son kullanma tarihi gerekli (AA/YY).")
        if not re.match(r"^(0[1-9]|1[0-2])/\d{2}$", value):
            raise forms.ValidationError("Geçerli format: AA/YY (örn: 12/28).")
        return value

    def clean_card_number(self):
        value = (self.cleaned_data.get("card_number") or "").replace(" ", "")
        if not value or not value.isdigit():
            raise forms.ValidationError("Geçerli bir kart numarası girin.")
        if len(value) < 13 or len(value) > 19:
            raise forms.ValidationError("Kart numarası 13–19 rakam olmalıdır.")
        return value


class BankTransferNoticeForm(forms.ModelForm):
    class Meta:
        model = BankTransferNotice
        fields = ("amount", "transfer_date", "note", "receipt")
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
            "transfer_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "İsteğe bağlı not"}),
            "receipt": forms.FileInput(attrs={"class": "form-control", "accept": "image/*,.pdf"}),
        }
        labels = {
            "amount": "Tutar (₺)",
            "transfer_date": "Havale tarihi",
            "note": "Not",
            "receipt": "Dekont (görsel veya PDF)",
        }


class CheckoutForm(forms.Form):
    delivery_address = forms.CharField(
        label="Teslimat adresi",
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        required=True,
    )
    order_notes = forms.CharField(
        label="Sipariş notu",
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        required=False,
    )

