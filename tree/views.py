from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .units import get_children, get_parents, get_siblings, check_request, create_tree
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        try:
            check_request(request.data)
            create_tree(request.data)
            return Response(
                {'status': 'okey, we do that'},
                status=status.HTTP_201_CREATED
            )
        except ValueError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        parent_list = get_parents(instance, parents=[])
        children_list = get_children(serializer.data.get('children'))
        siblings_list = get_siblings(Category.objects.filter(parent=instance.parent.id).exclude(name=instance.name))
        data = {'id': serializer.data.get('id'), 'name': serializer.data.get('name'), 'parents': parent_list,
                'children': children_list, 'siblings': siblings_list}
        return Response(data, status=status.HTTP_200_OK)
