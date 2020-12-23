from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        try:
            bulk = create_bulk_from_tree(request.data)
            Category.objects.bulk_create(bulk)
            return Response(
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


def create_bulk_from_tree(obj, parent=None):
    serializer = CategorySerializer(data={**obj, 'parent': parent, "children": []})
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    bulk = [Category(name=data['name'], parent=parent)]
    children = obj.get('children')
    if children:
        for child in children:
            bulk += create_bulk_from_tree(child, serializer.data.get('id', None))
    return bulk



def get_parents(instance, parents):
    if instance.parent:
        current_parent = Category.objects.get(pk=instance.parent.id)
        serializer = CategorySerializer(current_parent)
        parents.append({'id': serializer.data.get('id'), 'name': serializer.data.get('name')})
        get_parents(current_parent, parents)
    return parents


def get_children(id_list):
    children_list = []
    for item in id_list:
        current_user = Category.objects.get(pk=item)
        serializer = CategorySerializer(current_user)
        children_list.append({'id': serializer.data.get('id'), 'name': serializer.data.get('name')})
    return children_list


def get_siblings(queryset):
    siblings_list = []
    for item in queryset:
        current_sibling = Category.objects.get(pk=item.id)
        serializer = CategorySerializer(current_sibling)
        siblings_list.append({'id': serializer.data.get('id'), 'name': serializer.data.get('name')})
    return siblings_list
