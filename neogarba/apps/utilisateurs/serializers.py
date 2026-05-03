from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Utilisateur, Client, CodeOTP


# serializer d'inscription
class InscriptionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)
    telephone = serializers.CharField(max_length=200)

    def validate_email(self, value):
        if Utilisateur.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet Email est déjà utilisé.")
        return value.lower()
#     AGOHCHRIS90@GMAIL.COM ===>>>> agohchris90@gmail.com

    def validate_telephone(self, value):
            if Utilisateur.objects.filter(telephone=value).exists():
                raise serializers.ValidationError("Cet numéro de téléphone est déjà utilisé.")
            return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {
                    'password_confirm': 'Les deux mots de passe ne correspondent pas',
                }
            )

        return data


    def create(self, validated_data):
        validated_data.pop('password_confirm')
        client = Client.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            telephone=validated_data['telephone'],
            is_active=False,
        )

        return client




class VerificationOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=8, min_length=6)

    def validate(self, data):
        try:
            utilisateur = Utilisateur.objects.get(email=data['email'].lower())
        except Utilisateur.DoesNotExist:
            raise serializers.ValidationError("Aucun compte n'existe avec cet email")

        code_otp = CodeOTP.objects.filter(
            utilisateur = utilisateur,
            code=data['code'],
            est_utilise=False
        ).order_by('-date_creation').first()


        if not code_otp:
            raise serializers.ValidationError("Code OTP incorrect")

        if not code_otp.est_valide():
            raise serializers.ValidationError("Le code OTP à expiré demander un autre")

        data['utilisateur'] = utilisateur
        data['code_otp'] = code_otp

        return data






