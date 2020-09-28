import hashlib

from django.shortcuts import get_object_or_404
from django.db.models import Avg

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.exceptions import (
    ValidationError,

)

from .models import User, Categories, Genres, Titles, Review, Comments


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role']
        model = User


class YamdbAuthTokenSerializer(serializers.Serializer):
    password = serializers.CharField(required=False)
    email = serializers.EmailField()
    conformation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password', 'conformation_code')

    def validate(self, data):
        email = self.initial_data['email']
        hash_email = hashlib.sha256(email.encode('utf-8')).hexdigest()
        conformation_code = data['conformation_code']
        if hash_email != conformation_code:
            raise serializers.ValidationError("credential doesn't match")
        user = User.objects.create_user(email=email,
                                        password=conformation_code)
        refresh = TokenObtainPairSerializer.get_token(user)
        del data['email']
        del data['conformation_code']
        data['token'] = str(refresh.access_token)
        return data


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Categories


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genres


# Custom slug relational fields for TitleSerializer
class CustomSlugRelatedField(serializers.SlugRelatedField):
    def to_representation(self, obj):
        return {'name': obj.name, 'slug': obj.slug}


# Custom slug relational fields for TitleSerializer
class GenreField(SlugRelatedField):
    def to_representation(self, value):
        serializer = GenresSerializer(value)
        return serializer.data


class TitlesSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    category = CustomSlugRelatedField(
        queryset=Categories.objects.all(),
        slug_field='slug'
    )
    genre = CustomSlugRelatedField(
        queryset=Genres.objects.all(),
        slug_field='slug', many=True
    )

    class Meta:
        fields = (
            'id', 'name', 'year',
            'rating', 'description',
            'genre', 'category'
        )
        model = Titles

    def get_rating(self, title):
        scores = Review.objects.filter(title_id=title.id).aggregate(
            Avg('score'))
        if scores:
            return scores['score__avg']
        return None


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(source='author.username')
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, attrs):
        attrs['title'] = get_object_or_404(Titles,
                                           id=self.context['view'].kwargs[
                                               'title_id'])
        attrs['author'] = self.context['request'].user
        review = Review.objects.filter(title_id=attrs['title'],
                                       author=self.context['request'].user)
        if not self.partial and review:
            raise ValidationError('Вы уже писали отзыв на это произведение')
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(source='author.username')

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        model = Comments

    def validate(self, attrs):
        attrs['review'] = get_object_or_404(
            Review, id=self.context['view'].kwargs['review_id'])
        attrs['author'] = self.context['request'].user
        return attrs
