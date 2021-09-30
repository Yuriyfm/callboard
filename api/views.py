from rest_framework import generics
from django.contrib.auth.models import User
from main.models import Rubric, Ad
from .serializers import RubricSerializer, AdSerializer


class RubricList(generics.ListAPIView):
    queryset = Rubric.objects.all()
    serializer_class = RubricSerializer


class RubricDetail(generics.RetrieveAPIView):
    queryset = Rubric.objects.all()
    serializer_class = RubricSerializer


class AdList(generics.ListAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer


class AdDetail(generics.RetrieveAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
