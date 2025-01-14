import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderElement


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def validate_products_in_order(order):
    products = order.get('products')
    if not products or not isinstance(products, list):
        return False
    return True


@api_view(['POST'])
def register_order(request):
    order_request = request.data
    if not validate_products_in_order(order_request):
        return Response({'error': 'products key not presented or not list'})
    order = Order.objects.create(
        address=order_request['address'],
        firstname=order_request['firstname'],
        lastname=order_request['lastname'],
        phonenumber=order_request['phonenumber'],
    )
    for product in order_request['products']:
        OrderElement.objects.create(
            product_id=product['product'],
            order=order,
            quantity=product['quantity'],
        )

    return Response({})
