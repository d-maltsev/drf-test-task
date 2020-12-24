from tree.models import Category
from tree.serializers import CategorySerializer


def check_request(obj, parent=None):
    serializer = CategorySerializer(data={**obj, 'parent': parent, "children": []})
    serializer.is_valid(raise_exception=True)
    children = obj.get('children')
    if children:
        for child in children:
            check_request(child)


def create_tree(obj, parent=None):
    serializer = CategorySerializer(data={'name': obj.get('name'), 'parent': parent, "children": []})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    children = obj.get('children')
    if not children:
        return
    for child in children:
        create_tree(child, serializer.data.get('id', None))


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
