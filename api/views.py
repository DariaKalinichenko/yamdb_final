import hashlib

from django.http import HttpResponse
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend

from .filters import TitlesFilter
from .models import User, Categories, Genres, Titles, Review, Comments
from .permissions import IsAdmin, IsAdminOrReadOnly, MethodPermissions, \
    IsModeratorPermission, IsOwnerPermission
from .serializers import UserSerializer, CategoriesSerializer, \
    GenresSerializer, TitlesSerializer, ReviewSerializer, CommentSerializer, \
    YamdbAuthTokenSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, ]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'username'

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self, username=None):
        try:
            usename = self.kwargs['username']
        except Exception:
            queryset = User.objects.all()
            return queryset
        if usename == 'me':
            queryset = User.objects.filter(email=self.request.user.email)
            return queryset

        queryset = User.objects.filter(username=usename)
        return queryset

    def destroy(self, request, username=None):
        if username is None or username == 'me':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def sent_email(request):
    if request.method == 'POST':
        try:
            email = request.POST['email']
            validate_email(email)
        except Exception:
            return HttpResponse('enter a valid email')
        if User.objects.filter(email=email).first():
            return HttpResponse('This email already register')
        hash_email = hashlib.sha256(email.encode('utf-8')).hexdigest()
        send_mail(
            'Confirm_registration',
            f'Your conformation code is {hash_email}',
            'yamdb@yandex.ru',
            [email, ],
            fail_silently=False, )
        return HttpResponse(
            'check your mail for conformation code and go to'
            ' /api/v1/auth/token/ for complete registration')
    return HttpResponse('please, sent email with post request')


class YamdbTokenObtainPairView(TokenObtainPairView):
    serializer_class = YamdbAuthTokenSerializer


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAdminOrReadOnly, MethodPermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]
    lookup_field = 'slug'


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAdminOrReadOnly,
                          MethodPermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]
    lookup_field = 'slug'


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        queryset = Review.objects.filter(title_id=title_id)
        return queryset.order_by('-pub_date')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [permissions.AllowAny]
        elif self.action in 'destroy':
            permission_classes = [permissions.IsAuthenticated,
                                  IsModeratorPermission]
        elif self.action in ('update', 'partial_update'):
            permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]  # noqa: E501
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def destroy(self, request, title_id, pk=None):
        review = get_object_or_404(Review, pk=pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        queryset = Comments.objects.filter(review__title_id=title_id,
                                           review_id=review_id)
        return queryset.order_by('-pub_date')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [permissions.AllowAny]
        elif self.action in ('destroy'):
            permission_classes = [permissions.IsAuthenticated,
                                  IsModeratorPermission]
        elif self.action in ('update', 'partial_update'):
            permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]  # noqa: E501
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def destroy(self, request, title_id, review_id, pk=None):
        comment = get_object_or_404(Comments, pk=pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
