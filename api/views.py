from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from api.models import Vendor, PurchaseOrder

from rest_framework.response import Response


@api_view(['GET', 'POST'])
def create_vendor(request):
    if request.method == 'GET':
        vendors = Vendor.objects.all().order_by('-id')
        if vendors:
            vendor_list = [{
                'id': vendor.id,
                'name': vendor.name,
                'contact_details': vendor.contact_details,
                'address': vendor.address,
                'vendor_code': vendor.vendor_code,
                'on_time_delivery_rate': vendor.on_time_delivery_rate,
                'quality_rating_avg': vendor.quality_rating_avg,
                'average_response_time': vendor.average_response_time,
                'fulfillment_rate': vendor.fulfillment_rate
            } for vendor in vendors]
            return Response({
                "error": False,
                "message": "Data Found",
                "vendor_list": vendor_list
            })
        else:
            data = {
                "error": False,
                "message": "No Data Found",
            }
            return Response(data, status=400)

    elif request.method == 'POST':
        name = request.data.get('name')
        phone = request.data.get('phone')
        address = request.data.get('address')
        delivery_rate = request.data.get('delivery_rate')
        rating = request.data.get('rating')
        response_time = request.data.get('response_time')
        fulfillment_rate = request.data.get('fulfillment_rate')

        vendor_id = Vendor.objects.last()

        if vendor_id is not None:
            code = int(vendor_id.vendor_code[2:]) + 1
        else:
            code = 1

        actual_code = "VN" + str(code).zfill(3)

        Vendor.objects.create(vendor_code=actual_code, name=name, contact_details=phone,
                              address=address, on_time_delivery_rate=delivery_rate,
                              quality_rating_avg=rating, average_response_time=response_time,
                              fulfillment_rate=fulfillment_rate)
        return Response({'error': False, 'success': 'Vendor Created successfully.'}, status=200)


@api_view(['GET'])
def get_vendor(request, vendor_id):
    try:
        vendor = Vendor.objects.get(id=vendor_id)
        vendor_data = {
            'id': vendor.id,
            'name': vendor.name,
            'contact_details': vendor.contact_details,
            'address': vendor.address,
            'vendor_code': vendor.vendor_code,
            'on_time_delivery_rate': vendor.on_time_delivery_rate,
            'quality_rating_avg': vendor.quality_rating_avg,
            'average_response_time': vendor.average_response_time,
            'fulfillment_rate': vendor.fulfillment_rate
        }
        return Response({'error': False, 'message': "Data found", 'vendor': vendor_data}, status=200)
    except Vendor.DoesNotExist:
        return Response({'error': True, 'message': 'Vendor does not exist'}, status=400)


@api_view(['PUT'])
def update_vendor(request, vendor_id):
    try:
        vendor = Vendor.objects.get(id=vendor_id)
        name = request.data.get('name')
        phone = request.data.get('phone')
        address = request.data.get('address')
        delivery_rate = request.data.get('delivery_rate')
        rating = request.data.get('rating')
        response_time = request.data.get('response_time')
        fulfillment_rate = request.data.get('fulfillment_rate')

        vendor.name = name
        vendor.contact_details = phone
        vendor.address = address
        vendor.on_time_delivery_rate = delivery_rate
        vendor.quality_rating_avg = rating
        vendor.average_response_time = response_time
        vendor.fulfillment_rate = fulfillment_rate
        vendor.save()

        return Response({'error': False, 'message': 'Vendor details updated successfully'}, status=200)
    except Vendor.DoesNotExist:
        return Response({'error': True, 'message': 'Vendor does not exist'}, status=404)


@api_view(['DELETE'])
def delete_vendor(request, vendor_id):
    try:
        vendor = Vendor.objects.get(id=vendor_id)
        vendor.delete()
        return Response({'error': False, 'message': 'Vendor deleted successfully'}, status=200)
    except Vendor.DoesNotExist:
        return Response({'error': True, 'message': 'Vendor Data not Found'}, status=404)


@api_view(['DELETE'])
def delete_po(request, po_id):
    try:
        po = PurchaseOrder.objects.get(id=po_id)
        po.status = 'deleted'
        po.save()
        return Response({'error': False, 'message': 'Purchase Order deleted successfully'}, status=200)
    except PurchaseOrder.DoesNotExist:
        return Response({'error': True, 'message': 'Purchase Order Data not Found'}, status=404)


@api_view(['GET', 'POST'])
def create_po(request):
    if request.method == 'GET':
        pos = PurchaseOrder.objects.all().order_by('-id')
        if pos:
            po_list = [{
                'id': po.id,
                'po_number': po.po_number,
                'vendor_id': po.vendor_id,
                'order_date': po.order_date,
                'delivery_date': po.delivery_date,
                'items': po.items,
                'quantity': po.quantity,
                'status': po.status,
                'quality_rating': po.quality_rating,
                'issue_date': po.issue_date
            } for po in pos]
            return Response({
                "error": False,
                "message": "Data Found",
                "po_list": po_list
            })
        else:
            data = {
                "error": False,
                "message": "No Data Found",
            }
            return Response(data, status=400)

    elif request.method == 'POST':
        try:
            data = request.data
            items = data.pop('items', [])

            po_id = PurchaseOrder.objects.last()
            code = 1 if po_id is None else int(po_id.po_number[2:]) + 1
            po_code = f"PO{code:03}"

            PurchaseOrder.objects.create(
                po_number=po_code,
                vendor_id=data['vendor_id'],
                order_date=data['order_date'],
                delivery_date=data['delivery_date'],
                items=', '.join(items),
                quantity=data['quantity'],
                status=data['status'],
                quality_rating=data.get('quality_rating'),
                issue_date=data['issue_date'],
                acknowledgment_date=data.get('acknowledgment_date')
            )

            return Response({'error': False, 'message': 'Purchase Order created successfully'},
                            status=200)
        except Exception as e:
            return Response({'error': True, 'message': str(e)}, status=400)


@api_view(['GET'])
def get_po(request, po_id):
    try:
        po = PurchaseOrder.objects.get(id=po_id)
        vendor_data = {
            'id': po.id,
            'po_number': po.po_number,
            'vendor_id': po.vendor_id,
            'order_date': po.order_date,
            'delivery_date': po.delivery_date,
            'items': po.items,
            'quantity': po.quantity,
            'status': po.status,
            'quality_rating': po.quality_rating,
            'issue_date': po.issue_date

        }
        return Response({'error': False, 'message': "Data found", 'vendor': vendor_data}, status=200)
    except PurchaseOrder.DoesNotExist:
        return Response({'error': True, 'message': 'Purchase Order Data not Found'}, status=400)


@api_view(['PUT'])
def update_po(request, po_id):
    try:
        po = PurchaseOrder.objects.get(id=po_id)
        order_date = request.data.get('order_date')
        delivery_date = request.data.get('delivery_date')
        items = request.data.get('items')
        quantity = request.data.get('quantity')
        status = request.data.get('status')
        quality_rating = request.data.get('quality_rating')
        issue_date = request.data.get('issue_date')

        po.order_date = order_date
        po.delivery_date = delivery_date
        po.items = items
        po.quantity = quantity
        po.status = status
        po.quality_rating = quality_rating
        po.issue_date = issue_date
        po.save()

        return Response({'error': False, 'message': 'Purchase Order details updated successfully'}, status=200)
    except Vendor.DoesNotExist:
        return Response({'error': True, 'message': 'Purchase Order Data not Found'}, status=404)


@api_view(['GET'])
def get_vendor_performance(request, vendor_id):
    try:
        vendor = Vendor.objects.get(id=vendor_id)
        performance_data = {
            'on_time_delivery_rate': vendor.on_time_delivery_rate,
            'quality_rating': vendor.quality_rating_avg,
            'response_time': vendor.average_response_time,
            'fulfilment_rate': vendor.fulfillment_rate
        }
        return Response({'success': True, 'message': 'Vendor Data found', 'performance': performance_data}, status=200)
    except Vendor.DoesNotExist:
        return Response({'success': False, 'message': 'Vendor not found'}, status=404)


def register(request):
    return render(request, 'register.html')
