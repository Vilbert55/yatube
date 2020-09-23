from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User   #модель, с которой связана создаваемая форма
        fields = ("first_name", "last_name", "username", "email") #какие поля должны быть видны в форме и в каком порядке
