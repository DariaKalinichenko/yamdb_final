from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(
            email,
            password=password,
            **kwargs
        )
        user.role = 'admin'
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    USER_ROLES = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )
    email = models.EmailField(verbose_name='Почта',
                              max_length=255,
                              unique=True,
                              )
    first_name = models.CharField(max_length=200,
                                  blank=True,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=200,
                                 blank=True,
                                 verbose_name='Фамилия')
    username = models.SlugField(unique=True,
                                blank=True,
                                null=True,
                                verbose_name='Логин')
    bio = models.TextField(blank=True,
                           verbose_name='О себе')
    role = models.CharField(max_length=10,
                            choices=USER_ROLES,
                            default='user',
                            verbose_name='Роль')
    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class Categories(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название категории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название жанра')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название произведения')
    year = models.IntegerField(verbose_name='Год')
    category = models.ForeignKey(Categories,
                                 on_delete=models.SET_NULL,
                                 blank=True,
                                 null=True, verbose_name='Категория')
    genre = models.ManyToManyField('Genres',
                                   related_name='title',
                                   blank=True,
                                   verbose_name='Жанр')
    description = models.TextField(verbose_name='Описание')
    rating = models.IntegerField(null=True, verbose_name='Рейтинг')

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Titles, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор')
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    db_index=True,
                                    verbose_name='Дата публикации')


class Comments(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Автор')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    db_index=True,
                                    verbose_name='Дата публикации')
