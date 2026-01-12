from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
from decimal import Decimal

# Create your views here.

def home(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.product_id,
                p.product_name,
                p.product_price,
                p.product_image,
                p.product_slug,
                c.category_name
            FROM product p
            JOIN category_catrgory c ON p.product_category = c.id
            ORDER BY p.product_id DESC
        """)
        show_product = cursor.fetchall()

    return render (request,'home.html',{"show_product":show_product})

def store(request): 
    with connection.cursor() as cursor:
        cursor.execute("SELECT p.product_id,p.product_name,p.product_price,p.product_image,p.product_slug,c.category_name FROM product p JOIN category_catrgory c ON p.product_category = c.id WHERE p.product_available = 1 ORDER BY p.product_id DESC")
        rows = cursor.fetchall()
        show_in_store =[]
        for r in rows:
            product_id = r[0]
            product_name = r[1]
            product_price = r[2]
            product_image = r[3]
            product_slug = r[4]
            category_name = r[5]
            
            old_price = product_price*Decimal('1.20')        
            show_in_store.append((product_id,product_name,product_price,product_image,old_price,product_slug,category_name))

        # cursor.execute("SELECT count(*) FROM product WHERE product_available =1")
        product_count = len(show_in_store)
    return render(request, 'store.html',{"show_in_store":show_in_store,"product_count":product_count})


# def category_processor(request):
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT id,category_name FROM category_catrgory ORDER BY category_name ASC")
#         show_all_category = cursor.fetchall()

#         return {
#             'show_all_category':show_all_category
#             }

def all_product_under_category_of_store(request,cat_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM category_catrgory WHERE category_name=%s",[cat_name])
        cat_row = cursor.fetchone()
        cat_id_of_store = cat_row[0]

        cursor.execute("SELECT p.product_id, p.product_name, p.product_price, p.product_image, p.product_slug FROM product p WHERE p.product_available = 1 AND p.product_category = %s", [cat_id_of_store])
        rows = cursor.fetchall()

        show_in_store =[]
        for r in rows:
            product_id = r[0]
            product_name = r[1]
            product_price = r[2]
            product_image = r[3]
            product_slug = r[4]
            
            old_price = round(product_price*1.2)            
            show_in_store.append((product_id,product_name,product_price,product_image,old_price,product_slug,cat_name))
        product_count = len(show_in_store)


    return render(request, 'store.html',{"show_in_store":show_in_store,"product_count":product_count})

def single_product_details(request,cat_name,product_slug):
    with connection.cursor() as cursor:
        cursor.execute("SELECT product_id,product_name,product_description,product_price,product_stock,product_available,product_image FROM product WHERE product_slug=%s",[product_slug])
        single_product = cursor.fetchone()
       
    return render(request,'product_details.html',{'single_product':single_product})


def add_cart(request,product_id):
    cart = request.session.get('cart',{})
    # print(cart)
    # if str(product_id) in cart:
    #     cart[str(product_id)] +=1
    # else:
    #     cart[str(product_id)] =1

    pid = str(product_id)
    cart[pid] = cart.get(pid,0)+1 #If key exists → return its value
    
    request.session['cart'] = cart
    request.session.modified=True    

    return redirect('cart')

def decrease_product(request,product_id):
    cart = request.session.get('cart',{})
    pid = str(product_id)
    if pid in cart:
        cart[pid] -=1
        if  cart[pid] <=0:
            del cart[pid]
    request.session['cart'] =cart
    request.session.modified=True
    return redirect('cart')
def remove_product(request,product_id):
    cart = request.session.get('cart',{})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
    request.session['cart'] =cart
    request.session.modified=True
    return redirect('cart')

def cart(request):
    cart = request.session.get('cart',{})
    cart_items=[]
    tax_percent = Decimal('0.1')
    total = Decimal('0.00')
    if cart:
        with connection.cursor() as cursor:
            for pid,qnt in cart.items():
                cursor.execute("SELECT product_name,product_slug,product_description,product_price,product_stock,product_image FROM product WHERE product_id =%s ",[pid])
                product = cursor.fetchone()

                if product:
                    subtotal = product[3]*qnt
                    total +=subtotal 

                    cart_items.append({
                        'id':pid,
                        'name':product[0],
                        'slug':product[1],
                        'description':product[2],
                        'price':product[3],
                        'stock':product[4],
                        'image':product[5],
                        'quantity':qnt,
                        'subtotal':subtotal

                    })    
    tax = round(total*tax_percent,2)
    final_price = round(total+tax,2)  
   
    return render(request, 'cart.html', {'cart_items':cart_items,'total':total,'tax':tax,'final_price':final_price})


