from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from decimal import Decimal
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.template.loader import render_to_string
from django.http import JsonResponse
from ipware import get_client_ip
import random
import requests
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import os, re
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse


def validate_user_input(
    first_name=None, last_name=None, user_email=None, user_phone=None, city=None
):
    errors = []
    # First name
    if not first_name or len(first_name) < 2 or len(first_name) > 20:
        errors.append("Enter a valid first name")

    # Last name
    if not last_name or len(last_name) < 2 or len(last_name) > 20:
        errors.append("Enter a valid last name")

    # Email
    if not user_email:
        errors.append("Enter email address")
    else:
        try:
            validate_email(user_email)
        except ValidationError:
            errors.append("Enter a valid email address")

    # Mobile number
    if not user_phone:
        errors.append("Enter mobile number")
    elif not re.fullmatch(r"\d{11}", user_phone):
        errors.append("Mobile number must be exactly 11 digits.")

    # City
    if city:
        if len(city) < 2 or len(city) > 50:
            errors.append("Enter a valid city name")

    # Duplicate Email
    if user_email:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM customer_user WHERE email=%s LIMIT 1", [user_email]
            )
            if cursor.fetchone():
                errors.append(f"Email {user_email} already exists.")

    # Duplicate Phone
    if user_phone:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM customer_user WHERE phone=%s LIMIT 1", [user_phone]
            )
            if cursor.fetchone():
                errors.append(f"Mobile number {user_phone} already exists.")

    return errors


def get_products(query=None, page=1, per_page=6):
    with connection.cursor() as cursor:
        if query:
            cursor.execute(
                """
                SELECT p.product_id, p.product_name, p.product_price,
                       p.product_image, p.product_slug, c.category_name
                FROM product p
                JOIN category_catrgory c ON p.product_category = c.id
                WHERE p.product_available = 1
                  AND (p.product_name LIKE %s OR p.product_description LIKE %s)
                ORDER BY p.product_id DESC
                """,
                [f"%{query}%", f"%{query}%"],
            )
        else:
            cursor.execute(
                """
                SELECT p.product_id, p.product_name, p.product_price,
                       p.product_image, p.product_slug, c.category_name
                FROM product p
                JOIN category_catrgory c ON p.product_category = c.id
                WHERE p.product_available = 1
                ORDER BY p.product_id DESC
                """
            )

        rows = cursor.fetchall()

    products = [
        (
            r[0],
            r[1],
            r[2],
            r[3],
            r[2] * Decimal("1.20"),
            r[4],
            r[5],
        )
        for r in rows
    ]

    paginator = Paginator(products, per_page)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj, paginator.count

def home(request):
    if 'cust_user_inactive' in request.session:
                return redirect('cust_change_password_for_activation')
    
        # If user is active, block this page → send them home
        


    with connection.cursor() as cursor:
        cursor.execute(
            """
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
        """
        )
        show_product = cursor.fetchall()

    return render(request, "home.html", {"show_product": show_product})


def store(request):

    if 'cust_user_inactive' in request.session:
        return redirect('cust_change_password_for_activation')
    page = request.GET.get("page", 1)
    show_in_store, product_count = get_products(page=page)

    return render(
        request,
        "store.html",
        {
            "show_in_store": show_in_store,
            "product_count": product_count,
        },
    )


def all_product_under_category_of_store(request, cat_name):
    if 'cust_user_inactive' in request.session:
            return redirect('cust_change_password_for_activation')
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM category_catrgory WHERE category_name=%s", [cat_name]
        )
        cat_row = cursor.fetchone()
        cat_id_of_store = cat_row[0]

        cursor.execute(
            "SELECT p.product_id, p.product_name, p.product_price, p.product_image, p.product_slug FROM product p WHERE p.product_available = 1 AND p.product_category = %s",
            [cat_id_of_store],
        )
        rows = cursor.fetchall()
        discount = Decimal("1.2")
        show_in_store = []
        for r in rows:
            product_id = r[0]
            product_name = r[1]
            product_price = r[2]
            product_image = r[3]
            product_slug = r[4]

            old_price = round(product_price * discount)
            show_in_store.append(
                (
                    product_id,
                    product_name,
                    product_price,
                    product_image,
                    old_price,
                    product_slug,
                    cat_name,
                )
            )
        product_count = len(show_in_store)

    return render(
        request,
        "store.html",
        {"show_in_store": show_in_store, "product_count": product_count},
    )


def single_product_details(request, cat_name, product_slug):
    if 'cust_user_inactive' in request.session:
            return redirect('cust_change_password_for_activation')
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT product_id,product_name,product_description,product_price,product_stock,product_available,product_image FROM product WHERE product_slug=%s",
            [product_slug],
        )
        single_product = cursor.fetchone()
        cart = request.session.get("cart", {})

    return render(
        request,
        "product_details.html",
        {"single_product": single_product, "cart": cart},
    )


def add_cart(request, product_id):
    if 'cust_user_inactive' in request.session:
            return redirect('cust_change_password_for_activation')
    cart = request.session.get("cart", {})
    # print(cart)
    # if str(product_id) in cart:
    #     cart[str(product_id)] +=1
    # else:
    #     cart[str(product_id)] =1

    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1  # If key exists → return its value

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def decrease_product(request, product_id):
    if 'cust_user_inactive' in request.session:
            return redirect('cust_change_password_for_activation')
    cart = request.session.get("cart", {})
    pid = str(product_id)
    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            del cart[pid]
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")


def remove_product(request, product_id):
    if 'cust_user_inactive' in request.session:
            return redirect('cust_change_password_for_activation')
    cart = request.session.get("cart", {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")


def cart(request):
    if 'cust_user_inactive' in request.session:
            return redirect('cust_change_password_for_activation')
    cart = request.session.get("cart", {})
    cart_items = []
    tax_percent = Decimal("0.1")
    total = Decimal("0.00")

    if cart:
        with connection.cursor() as cursor:
            for pid, qnt in cart.items():
                cursor.execute(
                    """
                    SELECT 
                        p.product_name,
                        p.product_slug,
                        p.product_description,
                        p.product_price,
                        p.product_stock,
                        p.product_image,
                        c.category_name
                    FROM product p
                    JOIN category_catrgory c ON p.product_category = c.id
                    WHERE p.product_id = %s
                """,
                    [pid],
                )

                product = cursor.fetchone()

                if product:
                    subtotal = product[3] * qnt
                    total += subtotal

                    cart_items.append(
                        {
                            "id": pid,
                            "name": product[0],
                            "slug": product[1],
                            "description": product[2],
                            "price": product[3],
                            "stock": product[4],
                            "image": product[5],
                            "category": product[6],  # ✅ IMPORTANT
                            "quantity": qnt,
                            "subtotal": subtotal,
                        }
                    )

    tax = round(total * tax_percent, 2)
    final_price = round(total + tax, 2)

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "total": total,
            "tax": tax,
            "final_price": final_price,
        },
    )

def product_search(request):
    query = request.GET.get("q", "").strip()
    page = request.GET.get("page", 1)

    show_in_store, product_count = get_products(query=query, page=page)
    # print(product_count)

    html = render_to_string(
        "includes/product_results.html",
        {
            "show_in_store": show_in_store,
            "product_count": product_count,
        },
        request=request,
    )

    return JsonResponse({"html": html})


def register(request):
    if 'cust_user_inactive' in request.session:
        return redirect('cust_change_password_for_activation')
    if 'cust_first_name' in request.session:
        return redirect('home')

    country_list = [
        {"code": "AF", "name": "Afghanistan"},
        {"code": "AL", "name": "Albania"},
        {"code": "DZ", "name": "Algeria"},
        {"code": "AD", "name": "Andorra"},
        {"code": "AO", "name": "Angola"},
        {"code": "AG", "name": "Antigua and Barbuda"},
        {"code": "AR", "name": "Argentina"},
        {"code": "AM", "name": "Armenia"},
        {"code": "AU", "name": "Australia"},
        {"code": "AT", "name": "Austria"},
        {"code": "AZ", "name": "Azerbaijan"},
        {"code": "BS", "name": "Bahamas"},
        {"code": "BH", "name": "Bahrain"},
        {"code": "BD", "name": "Bangladesh"},
        {"code": "BB", "name": "Barbados"},
        {"code": "BY", "name": "Belarus"},
        {"code": "BE", "name": "Belgium"},
        {"code": "BZ", "name": "Belize"},
        {"code": "BJ", "name": "Benin"},
        {"code": "BT", "name": "Bhutan"},
        {"code": "BO", "name": "Bolivia"},
        {"code": "BA", "name": "Bosnia and Herzegovina"},
        {"code": "BW", "name": "Botswana"},
        {"code": "BR", "name": "Brazil"},
        {"code": "BN", "name": "Brunei"},
        {"code": "BG", "name": "Bulgaria"},
        {"code": "BF", "name": "Burkina Faso"},
        {"code": "BI", "name": "Burundi"},
        {"code": "CV", "name": "Cabo Verde"},
        {"code": "KH", "name": "Cambodia"},
        {"code": "CM", "name": "Cameroon"},
        {"code": "CA", "name": "Canada"},
        {"code": "CF", "name": "Central African Republic"},
        {"code": "TD", "name": "Chad"},
        {"code": "CL", "name": "Chile"},
        {"code": "CN", "name": "China"},
        {"code": "CO", "name": "Colombia"},
        {"code": "KM", "name": "Comoros"},
        {"code": "CG", "name": "Congo"},
        {"code": "CD", "name": "Congo (Democratic Republic)"},
        {"code": "CR", "name": "Costa Rica"},
        {"code": "HR", "name": "Croatia"},
        {"code": "CU", "name": "Cuba"},
        {"code": "CY", "name": "Cyprus"},
        {"code": "CZ", "name": "Czech Republic"},
        {"code": "DK", "name": "Denmark"},
        {"code": "DJ", "name": "Djibouti"},
        {"code": "DM", "name": "Dominica"},
        {"code": "DO", "name": "Dominican Republic"},
        {"code": "EC", "name": "Ecuador"},
        {"code": "EG", "name": "Egypt"},
        {"code": "SV", "name": "El Salvador"},
        {"code": "GQ", "name": "Equatorial Guinea"},
        {"code": "ER", "name": "Eritrea"},
        {"code": "EE", "name": "Estonia"},
        {"code": "SZ", "name": "Eswatini"},
        {"code": "ET", "name": "Ethiopia"},
        {"code": "FJ", "name": "Fiji"},
        {"code": "FI", "name": "Finland"},
        {"code": "FR", "name": "France"},
        {"code": "GA", "name": "Gabon"},
        {"code": "GM", "name": "Gambia"},
        {"code": "GE", "name": "Georgia"},
        {"code": "DE", "name": "Germany"},
        {"code": "GH", "name": "Ghana"},
        {"code": "GR", "name": "Greece"},
        {"code": "GD", "name": "Grenada"},
        {"code": "GT", "name": "Guatemala"},
        {"code": "GN", "name": "Guinea"},
        {"code": "GW", "name": "Guinea-Bissau"},
        {"code": "GY", "name": "Guyana"},
        {"code": "HT", "name": "Haiti"},
        {"code": "HN", "name": "Honduras"},
        {"code": "HU", "name": "Hungary"},
        {"code": "IS", "name": "Iceland"},
        {"code": "IN", "name": "India"},
        {"code": "ID", "name": "Indonesia"},
        {"code": "IR", "name": "Iran"},
        {"code": "IQ", "name": "Iraq"},
        {"code": "IE", "name": "Ireland"},
        {"code": "IL", "name": "Israel"},
        {"code": "IT", "name": "Italy"},
        {"code": "JM", "name": "Jamaica"},
        {"code": "JP", "name": "Japan"},
        {"code": "JO", "name": "Jordan"},
        {"code": "KZ", "name": "Kazakhstan"},
        {"code": "KE", "name": "Kenya"},
        {"code": "KI", "name": "Kiribati"},
        {"code": "KW", "name": "Kuwait"},
        {"code": "KG", "name": "Kyrgyzstan"},
        {"code": "LA", "name": "Laos"},
        {"code": "LV", "name": "Latvia"},
        {"code": "LB", "name": "Lebanon"},
        {"code": "LS", "name": "Lesotho"},
        {"code": "LR", "name": "Liberia"},
        {"code": "LY", "name": "Libya"},
        {"code": "LI", "name": "Liechtenstein"},
        {"code": "LT", "name": "Lithuania"},
        {"code": "LU", "name": "Luxembourg"},
        {"code": "MG", "name": "Madagascar"},
        {"code": "MW", "name": "Malawi"},
        {"code": "MY", "name": "Malaysia"},
        {"code": "MV", "name": "Maldives"},
        {"code": "ML", "name": "Mali"},
        {"code": "MT", "name": "Malta"},
        {"code": "MH", "name": "Marshall Islands"},
        {"code": "MR", "name": "Mauritania"},
        {"code": "MU", "name": "Mauritius"},
        {"code": "MX", "name": "Mexico"},
        {"code": "FM", "name": "Micronesia"},
        {"code": "MD", "name": "Moldova"},
        {"code": "MC", "name": "Monaco"},
        {"code": "MN", "name": "Mongolia"},
        {"code": "ME", "name": "Montenegro"},
        {"code": "MA", "name": "Morocco"},
        {"code": "MZ", "name": "Mozambique"},
        {"code": "MM", "name": "Myanmar"},
        {"code": "NA", "name": "Namibia"},
        {"code": "NR", "name": "Nauru"},
        {"code": "NP", "name": "Nepal"},
        {"code": "NL", "name": "Netherlands"},
        {"code": "NZ", "name": "New Zealand"},
        {"code": "NI", "name": "Nicaragua"},
        {"code": "NE", "name": "Niger"},
        {"code": "NG", "name": "Nigeria"},
        {"code": "KP", "name": "North Korea"},
        {"code": "MK", "name": "North Macedonia"},
        {"code": "NO", "name": "Norway"},
        {"code": "OM", "name": "Oman"},
        {"code": "PK", "name": "Pakistan"},
        {"code": "PW", "name": "Palau"},
        {"code": "PA", "name": "Panama"},
        {"code": "PG", "name": "Papua New Guinea"},
        {"code": "PY", "name": "Paraguay"},
        {"code": "PE", "name": "Peru"},
        {"code": "PH", "name": "Philippines"},
        {"code": "PL", "name": "Poland"},
        {"code": "PT", "name": "Portugal"},
        {"code": "QA", "name": "Qatar"},
        {"code": "RO", "name": "Romania"},
        {"code": "RU", "name": "Russia"},
        {"code": "RW", "name": "Rwanda"},
        {"code": "KN", "name": "Saint Kitts and Nevis"},
        {"code": "LC", "name": "Saint Lucia"},
        {"code": "VC", "name": "Saint Vincent and the Grenadines"},
        {"code": "WS", "name": "Samoa"},
        {"code": "SM", "name": "San Marino"},
        {"code": "ST", "name": "Sao Tome and Principe"},
        {"code": "SA", "name": "Saudi Arabia"},
        {"code": "SN", "name": "Senegal"},
        {"code": "RS", "name": "Serbia"},
        {"code": "SC", "name": "Seychelles"},
        {"code": "SL", "name": "Sierra Leone"},
        {"code": "SG", "name": "Singapore"},
        {"code": "SK", "name": "Slovakia"},
        {"code": "SI", "name": "Slovenia"},
        {"code": "SB", "name": "Solomon Islands"},
        {"code": "SO", "name": "Somalia"},
        {"code": "ZA", "name": "South Africa"},
        {"code": "KR", "name": "South Korea"},
        {"code": "SS", "name": "South Sudan"},
        {"code": "ES", "name": "Spain"},
        {"code": "LK", "name": "Sri Lanka"},
        {"code": "SD", "name": "Sudan"},
        {"code": "SR", "name": "Suriname"},
        {"code": "SE", "name": "Sweden"},
        {"code": "CH", "name": "Switzerland"},
        {"code": "SY", "name": "Syria"},
        {"code": "TW", "name": "Taiwan"},
        {"code": "TJ", "name": "Tajikistan"},
        {"code": "TZ", "name": "Tanzania"},
        {"code": "TH", "name": "Thailand"},
        {"code": "TL", "name": "Timor-Leste"},
        {"code": "TG", "name": "Togo"},
        {"code": "TO", "name": "Tonga"},
        {"code": "TT", "name": "Trinidad and Tobago"},
        {"code": "TN", "name": "Tunisia"},
        {"code": "TR", "name": "Turkey"},
        {"code": "TM", "name": "Turkmenistan"},
        {"code": "TV", "name": "Tuvalu"},
        {"code": "UG", "name": "Uganda"},
        {"code": "UA", "name": "Ukraine"},
        {"code": "AE", "name": "United Arab Emirates"},
        {"code": "GB", "name": "United Kingdom"},
        {"code": "US", "name": "United States"},
        {"code": "UY", "name": "Uruguay"},
        {"code": "UZ", "name": "Uzbekistan"},
        {"code": "VU", "name": "Vanuatu"},
        {"code": "VA", "name": "Vatican City"},
        {"code": "VE", "name": "Venezuela"},
        {"code": "VN", "name": "Vietnam"},
        {"code": "YE", "name": "Yemen"},
        {"code": "ZM", "name": "Zambia"},
        {"code": "ZW", "name": "Zimbabwe"},
    ]
    ips = [
        "103.48.16.1",
        "8.34.92.17",
        "43.244.0.5",
        "24.114.72.9",
        "13.54.201.3",
        "51.140.88.12",
    ]

    # client_ip, is_routable = get_client_ip(request)
    # # if client_ip:
    # #     print(f"Your IP is: {client_ip},{is_routable}")
    # if client_ip=='127.0.0.1':
    #     client_ip = 'BD'

    # print(client_ip)
    selected_ip = random.choice(ips)
    # print(selected_ip)
    res = requests.get(f"https://ipwho.is/{selected_ip}")
    data = res.json()

    country = {"code": data.get("country_code"), "name": data.get("country")}

    # print(country['code'])
    country_name = country["name"]
    # print(country_name)
    country_map = {c["code"]: c["name"] for c in country_list}
    # print(country_map)
    # print (country_map.get(country['code']))
    all_country_list = list(country_map.values())
    if request.method == "POST":
        data = request.POST
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        user_email = data.get("user_email")
        user_phone = data.get("user_phone")
        gender = request.POST.get("gender")
        city = data.get("city")
        selected_country_name = data.get("selected_country_name")
        emailed_password = str(random.randint(100000, 999999))
        temp_password = make_password(emailed_password)
        user_photo = request.FILES.get("user_photo")
        print(user_photo)
        photo_path = ""
        is_active = 0
        if user_photo:
            extention = os.path.splitext(user_photo.name)[1].lower()
            fs = FileSystemStorage()
            file_path = os.path.join(
                fs.location, f"general_user_profile_photo/{user_email}{extention}"
            )
            if os.path.exists(file_path):
                os.remove(file_path)
            file_name = fs.save(
                f"general_user_profile_photo/{user_email}{extention}", user_photo
            )
            photo_path = fs.url(file_name)
            print(photo_path)

        errors = validate_user_input(
            first_name=first_name,
            last_name=last_name,
            user_email=user_email,
            user_phone=user_phone,
            city=city,
        )
        if errors:
            return JsonResponse({"success": False, "errors": errors})
        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO customer_user(first_name,last_name,email,phone,gender,city,country,password,is_active,date_of_creation,photo_customer_user) "
                        "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),%s)",
                        [
                            first_name,
                            last_name,
                            user_email,
                            user_phone,
                            gender,
                            city,
                            selected_country_name,
                            temp_password,
                            is_active,
                            photo_path,
                        ],
                    )
                    if user_email:
                        send_mail(
                            subject="Activate Your Account",
                            message=f"Dear {first_name}, \n\n Welcome to GreatKart! To get started, please activate your account using the code below as your temporary password:\n\n Temporary Password: {emailed_password} \n\n Simply log in with this Temporary Password as password to complete your account setup. For security, we recommend updating your password after logging in.\n\n If you have any questions or need assistance, feel free to contact our support team.\n\n Thank you for joining us! \n Best regards, \n GreatKart Team.",
                            from_email="greatkart@gmail.com",
                            recipient_list=[user_email],
                            fail_silently=False,
                        )
                        return JsonResponse(
                            {"success": True, "message": "User Registered Sucessfully"}
                        )
                # messages.success(request, "User Registered Sucessfully")
            except Exception as e:
                # messages.error(request, f"User registration unsuccessful. Error: {str(e)}")
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"User registration unsuccessful. Error: {str(e)}",
                    }
                )

    return render(
        request,
        "register.html",
        {"all_country_list": all_country_list, "country_name": country_name},
    )


def customer_login(request):
    if 'cust_user_inactive' in request.session:
        return redirect('cust_change_password_for_activation')
    if 'cust_first_name' in request.session:
        return redirect('home')
    if request.method == "POST":

        user_email = request.POST.get("user_email", "").strip()
        user_password = request.POST.get("user_password", "").strip()

        errors = []

        if not user_email:
            errors.append("Email is required.")

        if not user_password:
            errors.append("Password is required.")

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT first_name,password,is_active,photo_customer_user
                FROM customer_user
                WHERE email=%s
            """,
                [user_email],
            )

            customer_user = cursor.fetchone()

        if not customer_user:
            return JsonResponse({"success": False, "message": "User not found."})

        db_first_name, db_password, db_is_active, db_photo = customer_user
        
        if not check_password(user_password, db_password):
            return JsonResponse({"success": False, "message": "Incorrect password."})

        if db_is_active == 2:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Your account is disabled. Contact administrator.",
                }
            )

        request.session["cust_first_name"] = db_first_name
        request.session["photo_customer_user"] = db_photo
        request.session["user_email"] = user_email

        if db_is_active == 0:
            # print("hello")
            # request.session["cust_user_inactive"] = True

            request.session["cust_user_inactive"] = True

            return JsonResponse(
                {
                    "success": True,
                    "message": "Redirecting to activate your account...",
                    "redirect_url": reverse("cust_change_password_for_activation"),
                }
            )

        # request.session.set_expiry(600)

        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE customer_user SET last_login=NOW() WHERE email=%s",
                    [user_email],
                )
            return JsonResponse(
                {
                    "success": True,
                    "message": "Login successful.",
                    "redirect_url": reverse("home"),
                }
            )

    return render(request, "customer_login.html")


def cust_change_password_for_activation(request):
    if 'cust_user_inactive' not in request.session:
            return redirect('home')
    if request.method == "POST":
        data = request.POST
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*\W).{8,20}$"
        first_password = data.get("first_password")
        confirm_password = data.get("confirm_password")
        hashed_password = make_password(first_password)
        user_email = request.session.get("user_email")
        if not re.match(password_pattern, first_password):
            return JsonResponse(
                {
                    "success": False,
                    "message": "Password must be 8-20 characters long, with at least one uppercase letter, one lowercase letter, one number, and one special character.",
                }
            )
        elif first_password != confirm_password:
            return JsonResponse(
                {"success": False, "message": "Password and Confirm password Mismatch"}
            )
        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE customer_user SET password =%s, is_active=1, date_of_join=NOW() WHERE email=%s ",
                        [hashed_password, user_email],
                    )
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Password Change Sucessfully. Please Login.",
                            "redirect_url": reverse("cust_sign_out"),
                        }
                    )
            except Exception:
                return JsonResponse(
                    {"success": False, "message": "Server Problem.Password Not Change"}
                )

    return render(request, "change_password_for_user_activation.html")

def dashboard(request):
    if 'cust_user_inactive' in request.session:
            return redirect('cust_change_password_for_activation')
    if 'cust_first_name' not in request.session:
            return redirect('home')
    return render(request,'dashboard.html')

def forgot_password(request):
    if 'cust_user_inactive' in request.session:
            return redirect('cust_change_password_for_activation')
    if 'cust_first_name' in request.session:
            return redirect('home')

    if request.method == "POST":
         data = request.POST
         forget_pass_email = data.get("forget_pass_email")
         with connection.cursor() as cursor:
              cursor.execute("SELECT email,first_name FROM customer_user WHERE email=%s",[forget_pass_email])
              result = cursor.fetchone()
              

              if not result:
                    return JsonResponse({ "success": False, "message":"Email Not Found"})
              else:
                    try:
                        db_email,db_first_name = result
                        emailed_password = str(random.randint(100000, 999999))
                        temp_password = make_password(emailed_password)
                        send_mail(
                                subject="GreatKart Password Reset Request",
                                message=f"Dear {db_first_name}, \n\n We received a request to reset the password for your GreatKart account.\n\n Your temporary password is:\n\n Temporary Password: {emailed_password}\n Please use this temporary password to log in to your account. After logging in, you will be required to create a new password for security purposes.\n For your protection:\n - This temporary password should be used only once. \n - Do not share it with anyone.\n - Choose a strong password containing uppercase and lowercase letters, numbers, and special characters.\n If you did not request this password reset, please contact our support team immediately. \n Thank you for choosing GreatKart.\n\n Best regards,\n GreatKart Support Team",
                                from_email="greatkart@gmail.com",
                                recipient_list=[db_email],
                                fail_silently=False,
                            )

                        with connection.cursor() as cursor:
                            cursor.execute("UPDATE customer_user SET password =%s, is_active=0 WHERE email=%s",[temp_password,forget_pass_email])
                            return JsonResponse({ "success": True, "message":"Password Reset and Temporary Password Send to Your Email."})

                    except Exception as e:
                        # messages.error(request, f"User registration unsuccessful. Error: {str(e)}")
                        return JsonResponse(
                            {
                                "success": False,
                                "message": f"User registration unsuccessful. Error: {str(e)}",
                            }
                        )
         

    return render(request,'forgot_password.html')


def cust_sign_out(request):
    if 'cust_first_name' not in request.session:
        return redirect('home')
    request.session.flush()
    return redirect("customer_login")

