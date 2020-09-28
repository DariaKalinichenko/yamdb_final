from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from rest_framework.routers import DefaultRouter

from .views import (
    UsersViewSet,
    sent_email,
    YamdbTokenObtainPairView,
    CategoriesViewSet,
    GenresViewSet,
    TitlesViewSet,
    ReviewViewSet,
    CommentViewSet,
)

users_router = DefaultRouter()
users_router.register("", UsersViewSet)

router = DefaultRouter()
router.register("categories", CategoriesViewSet)
router.register("genres", GenresViewSet)
router.register("titles", TitlesViewSet)
router.register(r"titles/(?P<title_id>\d+)/reviews",
                ReviewViewSet, basename='reviews')
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet, basename='comments'
)


urlpatterns = [
    path("auth/email/", csrf_exempt(sent_email)),
    path("auth/token/", YamdbTokenObtainPairView.as_view()),
    path("users/", include(users_router.urls)),
    path("", include(router.urls)),
]
