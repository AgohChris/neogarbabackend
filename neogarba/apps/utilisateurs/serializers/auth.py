# utilisateurs/serializers/auth.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from utilisateurs.models import Utilisateur


class ConnexionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Email ou mot de passe incorrect.")

        if not user.is_active:
            raise serializers.ValidationError("Ce compte est désactivé.")

        attrs['user'] = user
        return attrs


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = [
            'id', 'reference', 'email', 'first_name', 'last_name',
            'telephone', 'role', 'date_joined', 'is_active',
        ]
        read_only_fields = ['id', 'reference', 'email', 'role', 'date_joined', 'is_active']


class ChangerMotDePasseSerializer(serializers.Serializer):
    ancien_mot_de_passe = serializers.CharField(write_only=True)
    nouveau_mot_de_passe = serializers.CharField(write_only=True, validators=[validate_password])
    confirmer_mot_de_passe = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['nouveau_mot_de_passe'] != attrs['confirmer_mot_de_passe']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return attrs

    def validate_ancien_mot_de_passe(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect.")
        return value


class MotDePasseOublieSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Utilisateur.objects.filter(email=value).exists():
            raise serializers.ValidationError("Aucun compte associé à cet email.")
        return value


class ReinitialiserMotDePasseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code_otp = serializers.CharField(max_length=6)
    nouveau_mot_de_passe = serializers.CharField(write_only=True, validators=[validate_password])
    confirmer_mot_de_passe = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['nouveau_mot_de_passe'] != attrs['confirmer_mot_de_passe']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
