from rest_framework import mixins
from rest_framework import viewsets

class CreateDeleteViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    '''Миксин для создания и удаления объектов.'''

    pass 