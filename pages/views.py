from django.http import HttpResponse
from django.shortcuts import render
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


