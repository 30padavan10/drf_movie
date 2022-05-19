



from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Actor
from .serializers import (
    ActorsListSerializer,
    ActorDetailSerializer,
)


class ActorViewSet(viewsets.ViewSet):
    """
    viewset это еще одна абстракция которая позволяет описывать методы и к этим методам описывать http-запросы которые
    приходят с клиентской стороны.
    Например в generics классах создавали 2 отдельных класса для списка актеров и описания актера, в viewsets можно в
    одном классе описать несколько методов.
    """
    def list(self, request):
        queryset = Actor.objects.all()
        serializer = ActorsListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Actor.objects.all()
        actor = get_object_or_404(queryset, pk=pk)
        serializer = ActorDetailSerializer(actor)
        return Response(serializer.data)