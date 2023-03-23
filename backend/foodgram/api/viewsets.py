from rest_framework import mixins, viewsets


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class ListRetriveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass

class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class ListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class RetrieveViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass