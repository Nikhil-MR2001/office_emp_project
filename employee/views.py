import stripe
from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import EmployeeForm
from .models import Employee, Role, Department, Shop, CartItem
from datetime import datetime
from django.db.models import Q


# Create your views here.


def index(request):
    return render(request, 'index.html')


def all_emp(request):
    emps = Employee.objects.all()
    # context = {
    #     'emps': emps
    # }
    return render(request, 'all_emp.html', {'emps': emps})


def remove_emp(request, id=0):
    if id:
        try:
            emp_to_be_removed = Employee.objects.get(id=id)
            emp_to_be_removed.delete()
            return HttpResponse("Employee Removed Successfully")
        except:
            return HttpResponse("Please Enter A Valid EMP ID")
    emps = Employee.objects.all()

    return render(request, 'remove_emp.html', {'emps': emps})


def filter_emp(request):
    if request.method == 'POST':
        name = request.POST['name']
        dept = request.POST['dept']
        role = request.POST['role']
        emps = Employee.objects.all()
        if name:
            emps = emps.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
        if dept:
            emps = emps.filter(dept__name__icontains=dept)
        if role:
            emps = emps.filter(role__name__icontains=role)

        return render(request, 'all_emp.html', {'emps': emps})

    elif request.method == 'GET':
        return render(request, 'filter_emp.html')
    else:
        return HttpResponse('An Exception Occurred')


def msg(request):
    return render(request, 'msg.html')


def add_emp(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        salary = int(request.POST['salary'])
        bonus = int(request.POST['bonus'])
        phone = int(request.POST['phone'])
        dept_id = int(request.POST['dept'])  # Get the department ID from the form
        role_id = int(request.POST['role'])  # Get the role ID from the form

        dept = Department.objects.get(id=dept_id)  # Retrieve the department object based on the ID
        role = Role.objects.get(id=role_id)  # Retrieve the role object based on the ID

        new_emp = Employee(
            first_name=first_name,
            last_name=last_name,
            salary=salary,
            bonus=bonus,
            phone=phone,
            dept=dept,  # Assign the department object to the employee
            role=role,  # Assign the role object to the employee
            hire_date=datetime.now()
        )
        new_emp.save()
        return HttpResponse('Employee Added Successfully....!')
    elif request.method == 'GET':
        departments = Department.objects.all()  # Retrieve all departments to pass to the template
        roles = Role.objects.all()  # Retrieve all roles to pass to the template
        return render(request, 'add_emp.html', {'departments': departments, 'roles': roles})
    else:
        return HttpResponse("An Exception Occurred! Employee Has Not Been Added")


def login(request):
    if request.method == 'POST':
        username = request.POST['uname']
        password = request.POST['psswrd']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login()
            messages.info(request, 'user added')
        else:
            messages.error(request, ' not valid')

    return render(request, "login.html")


def register(request):
    if request.method == 'POST':
        uname = request.POST['username']
        email = request.POST['email']
        pword = request.POST['password']
        cpword = request.POST['confirm']

        if pword == cpword:
            if User.objects.filter(username=uname).exists():
                messages.info(request, 'Username already taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email already taken')
                return redirect('register')
            else:
                User.objects.create_user(username=uname, password=pword, email=email)
                # Redirect to a success page or login page
                return redirect('/')  # Replace 'success' with the appropriate URL or view name

        else:
            messages.info(request, 'Passwords do not match')
            return redirect('register')

    return render(request, 'register.html')


def update_emp(request, id=0):
    if request.method == 'POST':
        emp = Employee.objects.get(id=id)
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        emp = Employee.objects.get(id=id)
        form = EmployeeForm(instance=emp)
        return render(request, 'update.html', {'form': form})


def shop(request):
    obj = Shop.objects.all()

    return render(request, 'shop.html', {'obj': obj})


def shopdetail(request, id):
    obj = Shop.objects.get(id=id)
    return render(request, 'shopdetail.html', {'obj': obj})


def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for cart_item in cart_items:
        cart_item.subtotal = cart_item.item.price * cart_item.quantity
    total_price = sum(cart_item.subtotal for cart_item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


def add_to_cart(request, id):
    item = Shop.objects.get(id=id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


def remove_from_cart(request, id):
    cart_item = CartItem.objects.get(id=id)
    cart_item.delete()
    return redirect('cart')


# CHECKOUT
stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout_view(request):
    cart_item = CartItem.objects.filter(user=request.user).first()
    cart_item_name = cart_item.item if cart_item else None

    context = {
        'cart_item_name': cart_item_name,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'checkoutview.html', context)

@csrf_exempt
def create_checkout_session(request):
    try:
        currency = request.POST.get('currency', 'USD')
        shipping_address_country = request.POST.get('shipping_address_country')

        if currency != 'INR':
            if shipping_address_country == 'IN':
                return JsonResponse({'error': 'Non-INR transactions require a shipping address outside India. Please provide a shipping address outside India.'})
            else:
                cart_item = CartItem.objects.filter(user=request.user).first()
                cart_item_name = cart_item.item if cart_item else None

                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[
                        {
                            'price_data': {
                                'currency': currency,
                                'unit_amount': cart_item.item.price * 100,  # Amount in cents
                                'product_data': {
                                    'name': cart_item.item.name,
                                },
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    success_url=request.build_absolute_uri('/success'),
                    cancel_url=request.build_absolute_uri('/cancel'),
                )
                return JsonResponse({'sessionId': session.id})
        else:
            return JsonResponse({'error': 'INR transactions are not supported for checkout.'})

    except Exception as e:
        return JsonResponse({'error': str(e)})