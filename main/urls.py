from django.urls import path

from .views import index, other_page, BBLoginView, profile, BBLogoutView, ChangeUserInfoView, BBPasswordChangeView, \
    RegisterUserView, RegisterDoneView, user_activate, DeleteUserView, by_rubric, detail, profile_ad_detail, \
    profile_ad_add, profile_ad_change, profile_ad_delete

app_name = 'main'
urlpatterns = [
    path('', index, name='index'),
    path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),  # accounts/login/ - путь для авторизации
    # пользователей в джанго по умолчанию
    path('accounts/profile/change/<int:pk>', profile_ad_change, name='profile_ad_change'),
    path('accounts/profile/delete/<int:pk>', profile_ad_delete, name='profile_ad_delete'),
    path('accounts/profile/add', profile_ad_add, name='profile_ad_add'),
    path('accounts/profile/<int:pk>/', profile_ad_detail, name='profile_ad_detail'),
    path('accounts/profile/', profile, name='profile'),  # accounts/profile/ - путь, по которому Django по умолчанию
    # перенаправляет пользователя при успешном входе
    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
]
