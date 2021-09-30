from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import RubricList, RubricDetail, AdList, AdDetail

urlpatterns = [
    path('rubrics/', RubricList.as_view()),
    path('rubrics/<int:pk>/', RubricDetail.as_view()),
    path('ads/all', AdList.as_view()),
    path('ads/<int:pk>/', AdDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
