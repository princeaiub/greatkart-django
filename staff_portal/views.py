from django.db import connection
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import random
import os, re
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.template.loader import render_to_string
import uuid
# Create your views here.
# all classes of staff portal


def check_user_session(request):
    # Not logged in → send to login
    if 'first_name' not in request.session:
        return redirect('login')

    # Logged in but inactive → send to change password
    if 'user_inactive' in request.session:
        return redirect('change_password_for_activation')

    # Logged in & active → allow page to continue
    return None # if upper 3 statement false then none, not necessary but clean

      



def validate_user_input(first_name=None, last_name=None, username=None, email=None, mobile_number=None, role=None,user_id=None):
    errors = []

    # First name
    if not first_name or len(first_name) < 2 or len(first_name) > 20:
        errors.append("Enter a valid first name")

    # Last name
    if not last_name or len(last_name) < 2 or len(last_name) > 20:
        errors.append("Enter a valid last name")

    # Username
    if not username or len(username) < 2 or len(username) > 20:
        errors.append("Enter a valid username")

    # Email
    if not email:
        errors.append("Enter email address")
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors.append("Enter a valid email address")

    # Mobile number
    if not mobile_number:
        errors.append("Enter mobile number")
    elif not re.fullmatch(r'\d{11}', mobile_number):
        errors.append("Mobile number must be exactly 11 digits.")

    # Role
    if role is None or role == "":
        errors.append("Please select user role")

    # Duplicate check
    if username or email or mobile_number:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_name, email, phone FROM accounts_superuser WHERE (user_name=%s OR email=%s OR phone=%s) AND id<>%s",
                [username, email, mobile_number,user_id]
            )
            all_user = cursor.fetchall()

        
        for db_users in all_user:
            if db_users[0] == username:
                    errors.append(f"Username {username} already exists.")
            if db_users[1] == email:
                    errors.append(f"Email {email} already exists.")
            if db_users[2] == mobile_number:
                    errors.append(f"Mobile number {mobile_number} already exists.")

    return errors

def validate_add_category(category_name=None,category_slug=None,category_description=None,cat_photo=None,cat_ext=None,file_size_kb=None,cat_exist=None):
    cat_errors =[]
    # Category name
    if not category_name or len(category_name) < 2 or len(category_name) > 30:
        cat_errors.append("Enter a valid Category name")
    # Category Slug
    if not category_slug or len(category_slug) < 2 or len(category_slug) > 30:
        cat_errors.append("Enter a valid Category Slug")
    # Category Description
    if not category_description or len(category_description) < 10 or len(category_description) > 1000:
        cat_errors.append("Description Must be 10 to 1000 Words")
    # If no photo upload
    if not cat_photo:
        cat_errors.append("You Must need to upload category Image")
    
    if cat_photo:
        if cat_ext not in [".jpg", ".jpeg", ".png"]:
            cat_errors.append("Image must be in JPG or JPEG or PNG format.")
        if file_size_kb>300:
            cat_errors.append("Image must be within 300KB")
    if cat_exist:
        cat_errors.append("Category with same name already exist")

    return cat_errors

def validate_add_product(product_name=None,product_slug=None,product_description=None,product_cost=None,product_price=None,product_stock=None,product_category=None,product_image=None,product_ext=None,product_file_size_kb=None):
        product_error=[]
        amount_regex = r"^(?!0+(?:\.0+)?$)\d+(\.\d{1,2})?$"
        # Product name
        if not product_name or len(product_name) < 2 or len(product_name) > 30:
            product_error.append("Enter a valid Category name") 
        # Product Slug
        if not product_slug or len(product_slug) < 2 or len(product_slug) > 30:
            product_error.append("Enter a valid Category Slug")

         # Product Description
        if not product_description or len(product_description) < 10 or len(product_description) > 1000:
            product_error.append("Description Must be 10 to 1000 Words")

        # Product Cost
        if not re.match(amount_regex,product_cost) or float(product_cost) <= 0:
            product_error.append("Enter a valid amount like 1.50")
         
         # Product Price
        if not re.match(amount_regex,product_price) or float(product_price) <= 0:
            product_error.append("Enter a valid amount like 1.50")
        
        # Product Stock
        if not re.match(amount_regex,product_stock):
            product_error.append("Enter a valid stock amount like 2 or 2.50")

        # Product category

        if product_category is None or product_category=="":
             product_error.append("Please select a product category")

        # If no photo upload
        if not product_image:
            product_error.append("You Must need to upload category Image")
    
        if product_image:
            if product_ext not in [".jpg", ".jpeg", ".png"]:
                product_error.append("Image must be in JPG or JPEG or PNG format.")
            if product_file_size_kb>300:
                product_error.append("Image must be within 300KB")
        

        return product_error





def staff_login(request):
    if 'first_name' in request.session:
        # Already logged in → go home (or handle inactive separately)
        if 'user_inactive' in request.session:
            return redirect('change_password_for_activation')
        return redirect('staff_home')
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        
        #messages.error(request,password)
        with connection.cursor() as cursor:           
            
            cursor.execute("SELECT first_name,password, user_role, is_active,photo_superuser " \
            "from accounts_superuser where user_name=%s",[username])
            user = cursor.fetchone()
            
            if user:
                db_firstname, db_password, db_role,is_active,photo_superuser = user
                
                if check_password(password, db_password):                    
                    request.session['first_name']= db_firstname
                    request.session['user_photo']=photo_superuser
                    request.session['roles']=db_role                    
                    request.session['inputter_id']=username
                    if is_active==0:
                        request.session['user_inactive']=True                        
                        return redirect('change_password_for_activation')
                    # if is_admin == 1:
                    #     is_admin = 'Admin'
                    #     request.session['is_admin']  =is_admin
                    request.session.set_expiry(600)
                    if is_active == 2:
                        messages.error(request,"Your ID is disabled. Contact System Admin ")
                    else:
                        with connection.cursor() as cursor:
                            cursor.execute("UPDATE accounts_superuser SET last_login=NOW() WHERE user_name=%s",[username])
                        return redirect('staff_home')
                else:
                    messages.error(request,"wrong password")
            else:
                messages.error(request, "User Name Not Found")
        
    return render (request, 'login.html')


def staff_home(request):
    # Not logged in → send to login
    if 'first_name' not in request.session:
        return redirect('login')

    # Logged in but inactive → send to change password
    elif 'user_inactive' in request.session:
        return redirect('change_password_for_activation')
    return render(request, 'staff_home.html',{"first_name":request.session.get('first_name'),"user_photo":request.session.get('user_photo'), "roles": request.session.get('roles')})

def add_user(request):
    response = check_user_session(request)
    if response:
        return response 
    if request.method == "POST":
        data = request.POST
        first_name = data.get('first_name') 
        last_name  = data.get('last_name')
        username = data.get('username').lower() 
        emailed_password =  str(random.randint(100000, 999999))       
        temp_password = make_password(emailed_password)
        email      = data.get('email')
        mobile_number = data.get('mobile_number')
        role = data.get('role')  
        photo = request.FILES.get('staff_photo')        
        photo_path = ""
        inputter_id = request.session.get('inputter_id')
        if photo:
            ext = os.path.splitext(photo.name)[1].lower()          
            fs = FileSystemStorage()   
            file_path = os.path.join(fs.location, f"profile_photo/{username}{ext}")
            if os.path.exists(file_path):
                os.remove(file_path)
            filename = fs.save(f"profile_photo/{username}{ext}", photo)            
            photo_path = fs.url(filename)
        
        # Role flags
        is_active = 0
        if role == "admin":
            is_admin, is_staff, is_superuser = 1, 1, 1
        elif role == "superuser":
            is_admin, is_staff, is_superuser = 0, 1, 1
        elif role == "staff":
            is_admin, is_staff, is_superuser = 0, 1, 0
        else:
            is_admin, is_staff, is_superuser = 0, 0, 0
        
        # Validate input
        errors = validate_user_input(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            mobile_number=mobile_number,
            role=role
        )
        
        if errors:
            #for error in errors:
                #messages.error(request, error)
            return JsonResponse({"success":False,"errors":errors})
        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO accounts_superuser (first_name, last_name, user_name, password, email, phone, is_admin, is_staff, " \
                    "is_superuser,user_role,is_active,photo_superuser,creator_id,time_creation) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())",
                    [first_name,last_name,username,temp_password,email,mobile_number,is_admin,is_staff,is_superuser,role,is_active,photo_path,inputter_id])
                    if email:
                        send_mail(subject="Activate Your Account", message=f"Dear {first_name}, \n\n Welcome to GreatKart! To get started, please activate your account using the code below as your temporary password:\n\n Activation Code: {emailed_password} \n\n Simply log in with this code to complete your account setup. For security, we recommend updating your password after logging in.\n\n If you have any questions or need assistance, feel free to contact our support team.\n\n Thank you for joining us! \n Best regards, \n GreatKart Team.", from_email="greatkart@gmail.com",recipient_list=[email],fail_silently=False)
                #messages.success(request, "User Registered Sucessfully")
                    return JsonResponse({"success":True,"message":"User Registered Sucessfully"})
            except Exception as e:
                #messages.error(request, f"User registration unsuccessful. Error: {str(e)}")
                return JsonResponse({"success": False, "message": f"User registration unsuccessful. Error: {str(e)}"})
    return render(request, 'add_user.html', {"first_name":request.session.get('first_name'),"user_photo":request.session.get('user_photo'), "roles": request.session.get('roles')})

def edit_staff_users(request, user_id):
    response = check_user_session(request)
    if response:
        return response 
    temporary_pass = None
    hashed_temp_pass = None  # default
    # temporary_pass = random.randint(100000,999999)
    # print(temporary_pass)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT first_name, last_name, user_name, email, phone, user_role, photo_superuser,is_active 
            FROM accounts_superuser WHERE id=%s
        """, [user_id])
        user_info = cursor.fetchone()
        username = user_info[2]

    if request.method == "POST":
        save_data = request.POST
        first_name_update = save_data.get('first_name')
        last_name_update = save_data.get('last_name')
        email_update = save_data.get('email')
        mobile_update = save_data.get('mobile_number')
        role_update = save_data.get('role')
        photo = request.FILES.get('staff_photo_update')        
        last_update_id = request.session.get('inputter_id') 
        chk_temp_pass = save_data.get('chk_temp_pass')=='on'
        enable_user_temp_pass = save_data.get('enable_user_checkbox')=='on'
        if enable_user_temp_pass:
            try:
                with connection.cursor() as cursor:                            
                    cursor.execute("UPDATE accounts_superuser SET is_active=1 WHERE id=%s ",[user_id])
                
                    return JsonResponse({"success":True,"message":"User Enable sucessfully Use previuos password"})                
                    
            except Exception as e:
                return JsonResponse({"success":False,"message":f"Re-active user not success{str(e)}"})

        errors = validate_user_input(
            first_name=first_name_update,
            last_name=last_name_update,
            email=email_update,
            mobile_number=mobile_update,
            role=role_update,
            user_id=user_id,
            username=username
        )

        # Determine role flags
        if role_update == "admin":
            is_admin, is_staff, is_superuser = 1, 1, 1
        elif role_update == "superuser":
            is_admin, is_staff, is_superuser = 0, 1, 1
        elif role_update == "staff":
            is_admin, is_staff, is_superuser = 0, 1, 0
        else:
            is_admin, is_staff, is_superuser = 0, 0, 0

        # 🔹 Return validation errors early
        if errors:
            return JsonResponse({"success": False, "errors": errors})

        try:
            with connection.cursor() as cursor:
        # ✅ Case 1 & 2 → Handle photo first (if uploaded)
                if photo:
                    fs = FileSystemStorage()
                    ext = os.path.splitext(photo.name)[1].lower()
                    file_path = os.path.join(fs.location, f"profile_photo/{username}{ext}")

                    if os.path.exists(file_path):
                        os.remove(file_path)

                    filename = fs.save(f"profile_photo/{username}{ext}", photo)
                    photo_path = fs.url(filename)

                    if chk_temp_pass:  # ✅ Case 1: Photo + Checkbox
                        temporary_pass = str(random.randint(100000,999999))
                        hashed_temp_pass = make_password(str(temporary_pass))
                        cursor.execute("""
                            UPDATE accounts_superuser 
                            SET first_name=%s, last_name=%s, email=%s, phone=%s,
                                is_admin=%s, is_staff=%s, is_superuser=%s,
                                user_role=%s, photo_superuser=%s, password=%s, creator_id=%s
                            WHERE id=%s
                        """, [first_name_update, last_name_update, email_update, mobile_update,
                            is_admin, is_staff, is_superuser, role_update,
                            photo_path, hashed_temp_pass, last_update_id, user_id])
                    else:  # ✅ Case 2: Photo only
                        cursor.execute("""
                            UPDATE accounts_superuser 
                            SET first_name=%s, last_name=%s, email=%s, phone=%s,
                                is_admin=%s, is_staff=%s, is_superuser=%s,
                                user_role=%s, photo_superuser=%s, creator_id=%s
                            WHERE id=%s
                        """, [first_name_update, last_name_update, email_update, mobile_update,
                            is_admin, is_staff, is_superuser, role_update,
                            photo_path, last_update_id, user_id])

                # ✅ Case 3 & 4 → No photo uploaded
                else:
                    if chk_temp_pass:  # ✅ Case 3: Password only
                        temporary_pass = str(random.randint(100000,999999))
                        hashed_temp_pass = make_password(str(temporary_pass))
                        cursor.execute("""
                            UPDATE accounts_superuser 
                            SET first_name=%s, last_name=%s, email=%s, phone=%s,
                                is_admin=%s, is_staff=%s, is_superuser=%s,
                                user_role=%s, password=%s, creator_id=%s
                            WHERE id=%s
                        """, [first_name_update, last_name_update, email_update, mobile_update,
                            is_admin, is_staff, is_superuser, role_update,
                            hashed_temp_pass, last_update_id, user_id])
                    else:  # ✅ Case 4: Normal update only
                        cursor.execute("""
                            UPDATE accounts_superuser 
                            SET first_name=%s, last_name=%s, email=%s, phone=%s,
                                is_admin=%s, is_staff=%s, is_superuser=%s,
                                user_role=%s, creator_id=%s
                            WHERE id=%s
                        """, [first_name_update, last_name_update, email_update, mobile_update,
                            is_admin, is_staff, is_superuser, role_update,
                            last_update_id, user_id])

            # 🔹 Send success response to AJAX
            return JsonResponse({"success": True, "message": "User information updated successfully!", "temporary_pass":temporary_pass})

        except Exception as e:
            # 🔹 Send database error to AJAX
            return JsonResponse({"success": False, "message": f"Error updating user: {str(e)}"})

    # 🔹 GET request → render page
    return render(request, 'edit_staff_users.html', {
        "first_name": request.session.get('first_name'),
        "user_photo": request.session.get('user_photo'),
        "roles": request.session.get('roles'),
        "user_info": user_info,
        # 'temporary_pass':temporary_pass,
        "user_id": user_id
    })
def all_users(request):
    response = check_user_session(request)
    if response:
        return response 
    all_users= []
    with connection.cursor() as cursor:
        cursor.execute("SELECT id,first_name,user_name,email,phone,user_role,photo_superuser,is_active FROM accounts_superuser ORDER BY time_creation DESC ")
        all_users = cursor.fetchall()

        # Set up pagination
    paginator = Paginator(all_users, 5)  # Show 5 feedback entries per page
    page = request.GET.get('page')  # Get the current page number from the URL (e.g., ?page=2)

    try:
        feedbacks_paginated = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        feedbacks_paginated = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver the last page
        feedbacks_paginated = paginator.page(paginator.num_pages)

        #print(all_users)
    return render(request,'all_users.html',{"first_name":request.session.get('first_name'),"user_photo":request.session.get('user_photo'), "roles": request.session.get('roles'),"all_users":feedbacks_paginated})

def all_user_search(request):
    response = check_user_session(request)
    if response:
        return response 
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)  # Current page number, default 1

    with connection.cursor() as cursor:
        if query:
            cursor.execute("""
                SELECT id,first_name,user_name,email,phone,user_role,photo_superuser,is_active
                FROM accounts_superuser
                WHERE first_name LIKE %s OR user_name LIKE %s OR phone LIKE %s
                ORDER BY time_creation DESC
            """, [f"%{query}%", f"%{query}%", f"%{query}%"])
        else:
            cursor.execute("""
                SELECT id,first_name,user_name,email,phone,user_role,photo_superuser,is_active
                FROM accounts_superuser
                ORDER BY time_creation DESC
            """)
        all_users = cursor.fetchall()

    # Pagination
    paginator = Paginator(all_users, 5)  # 5 users per page
    try:
        users_paginated = paginator.page(page)
    except PageNotAnInteger:
        users_paginated = paginator.page(1)
    except EmptyPage:
        users_paginated = paginator.page(paginator.num_pages)

    html = render_to_string('includes/user_table_body.html', {"all_users": users_paginated})
    
    # Optional: render pagination links
    pagination_html = render_to_string('includes/user_table_pagination.html', {"all_users": users_paginated, "query": query})
    
    return JsonResponse({'html': html, 'pagination_html': pagination_html})

    # return render(request,'all_users.html',{"first_name":request.session.get('first_name'),"user_photo":request.session.get('user_photo'), "roles": request.session.get('roles')})

def change_password_for_activation(request):
    # if 'first_name' not in request.session and 'user_inactive' not in request.session:
    #     return redirect('login')
    if 'first_name' not in request.session:
        return redirect('login')

    # If user is active, block this page → send them home
    if 'user_inactive' not in request.session:
        return redirect('staff_home')
    
    if request.method=="POST":
        data = request.POST
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*\W).{8,20}$"
        activation_password = data.get('activation_password')
        confirm_activation_password = data.get('confirm_activation_password')
        hashed_password = make_password(activation_password)
        username = request.session.get('inputter_id')
        if not re.match(password_pattern,activation_password):
            return JsonResponse({"success":False,"message":"Password must be 8-20 characters long, with at least one uppercase letter, one lowercase letter, one number, and one special character."})
        elif activation_password !=confirm_activation_password:
            return JsonResponse({"success":False, "message":"Password and Confirm password Mismatch"})
        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE accounts_superuser SET password=%s, is_active=1,date_of_join=NOW() WHERE user_name=%s",
    [hashed_password, username] )
                    return JsonResponse({"success":True, "message": "Password Change Sucessfully. Please Login.", "redirect_url": reverse('sign_out') })
                    # messages.success(request,"Password Change Sucessfully. Please Login.")
                    # return redirect('sign_out')
                    
            except Exception:
                    return JsonResponse({"success":False, "message": "Server Problem.Password Not Change" })
    

    return render(request, 'change_password_for_activation.html',{"first_name":request.session.get('first_name'),"user_photo":request.session.get('user_photo'), "roles": request.session.get('roles')})

def change_password(request):
    response = check_user_session(request)
    if response:
        return response 
    if request.method =="POST":
        data = request.POST
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*\W).{8,20}$"
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')
        hashed_password_change = make_password(new_password)
        username = request.session.get('inputter_id')
        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM accounts_superuser WHERE user_name=%s",[username])
            db_password=cursor.fetchone()[0]
            if not check_password(current_password,db_password):
                return JsonResponse({"success":False, "message":"Current Password is Wrong"})
            elif check_password(new_password,db_password):
                return JsonResponse({"success":False,"message":"Current Password And New Password Cant be same."})
            elif new_password !=confirm_new_password:
                return JsonResponse({"success": False, "message":"New Password and Confirm password missmatch"})
            elif not re.match(password_pattern,new_password):
                return JsonResponse({"success":False,"message":"Password must be 8-20 characters long, with at least one uppercase letter, one lowercase letter, one number, and one special character."})
            else:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE accounts_superuser SET password=%s WHERE user_name=%s",[hashed_password_change,username])
                        return JsonResponse({"success":True, "message":"Password change Successfully."})
                except Exception:
                    return JsonResponse({"success":False, "message": "Server Problem.Password Not Change" })

    return render(request, 'change_password.html',{'first_name':request.session.get('first_name'), 'user_photo':request.session.get('user_photo'), 'roles':request.session.get('roles')})

def add_category(request):
    response = check_user_session(request)
    if response:
        return response

    if request.method == "POST":
        cat_data = request.POST
        category_name = cat_data.get('category_name')
        category_slug = cat_data.get('category_slug')
        category_description = cat_data.get('category_description')
        cat_photo = request.FILES.get('cat_image')
        
        cat_ext = os.path.splitext(cat_photo.name)[1].lower() if cat_photo else None
        file_size_bytes = cat_photo.size if cat_photo else 0
        file_size_kb = round(file_size_bytes / 1024, 2)

        # Check existing category BEFORE validation
        with connection.cursor() as cursor:
            cursor.execute("SELECT category_name FROM category_catrgory WHERE category_name=%s", [category_name])
            result = cursor.fetchone()
            cat_exist = result[0] if result else None

        # 1️⃣ VALIDATION FIRST
        cat_errors = validate_add_category(
            category_name=category_name,
            category_slug=category_slug,
            category_description=category_description,
            cat_photo=cat_photo,
            cat_ext=cat_ext,
            file_size_kb=file_size_kb,
            cat_exist=cat_exist
        )

        if cat_errors:
            return JsonResponse({"success": False, "cat_errors": cat_errors})

        # 2️⃣ ONLY AFTER VALIDATION PASSES → SAVE FILE
        if cat_photo:
            fs = FileSystemStorage()
            file_path = f"category_photo/{category_name}{cat_ext}"

            # delete previous file if exists
            abs_path = os.path.join(fs.location, file_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)

            filename = fs.save(file_path, cat_photo)
            photo_path = fs.url(filename)
        else:
            photo_path = None

        # 3️⃣ Insert into database
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO category_catrgory 
                    (category_name, slug, description, cat_image, add_time)
                    VALUES (%s, %s, %s, %s, NOW())
                """, [category_name, category_slug, category_description, photo_path])

            return JsonResponse({"success": True, "message": "Category added successfully."})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Database error: {str(e)}"})

    return render(request, 'add_category.html', {
        "first_name": request.session.get('first_name'),
        "user_photo": request.session.get('user_photo'),
        "roles": request.session.get('roles')
    })


def all_category(request):
    response = check_user_session(request)
    if response:
        return response
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT id,category_name,cat_image FROM category_catrgory")
        show_category = cursor.fetchall()

    


    return render(request, 'all_category.html', {
        "first_name": request.session.get('first_name'),
        "user_photo": request.session.get('user_photo'),
        "roles": request.session.get('roles'),
        "show_category":show_category
    })


def add_product(request):
    response = check_user_session(request)
    if response:
        return response
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT id,category_name FROM category_catrgory")
        result_category = cursor.fetchall()

    if request.method =="POST":
        product_data = request.POST
        product_name = product_data.get('product_name')
        product_slug = product_data.get('product_slug')
        product_description = product_data.get('product_description')
        product_cost = product_data.get('product_cost')
        product_price = product_data.get('product_price')
        product_stock = product_data.get('product_stock')
        product_availbity=1 if product_data.get('product_availbity')=='on' else 0
        product_category = product_data.get('product_category')
        product_image = request.FILES.get('product_image')        
        product_ext = os.path.splitext(product_image.name)[1].lower() if product_image else None 
        product_file_size = product_image.size if product_image else 0
        product_file_size_kb = round(product_file_size/1024,2)

        # 1️⃣ VALIDATION FIRST
        product_error = validate_add_product(
            product_name=product_name,
            product_slug =product_slug,
            product_description=product_description,
            product_cost=product_cost,
            product_price=product_price,
            product_stock=product_stock,
            product_category=product_category,
            product_image=product_image,
            product_ext=product_ext,
            product_file_size_kb=product_file_size_kb  

        )

        if product_error:
            return JsonResponse({"success":False, "product_error":product_error})
        
        # 2️⃣ ONLY AFTER VALIDATION PASSES → SAVE FILE
        if product_image:
            unique_id = uuid.uuid4().hex[:8]
            fs = FileSystemStorage()
            file_path = f"product_photo/{product_name}_{unique_id}{product_ext}"

            # delete previous file if exists
            # abs_path = os.path.join(fs.location, file_path)
            # if os.path.exists(abs_path):
            #     os.remove(abs_path)

            filename = fs.save(file_path, product_image)
            photo_path = fs.url(filename)
        else:
            photo_path = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO product (product_name,product_slug,product_description,pruchase_cost,product_price,product_stock,product_available,product_category,product_create_date,product_image) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW(),%s)",
                            [product_name,product_slug,product_description,product_cost,product_price,product_stock,product_availbity,product_category,photo_path])
                
                return JsonResponse({"success":True,"message":"Product Added Successfully"})
        except Exception as e:
            return JsonResponse({"success":False, "message":f"Database error: {str(e)}"})
        

    return render(request,'add_product.html', {
        "result_category":result_category,
        "first_name": request.session.get('first_name'),
        "user_photo": request.session.get('user_photo'),
        "roles": request.session.get('roles')
    })

def all_product_under_cat(request,cat_id):
    response = check_user_session(request)
    if response:
        return response
   
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT product_id,product_name,product_slug,product_description,product_price,product_image FROM product WHERE product_category=%s ORDER BY product_id DESC",[cat_id])
            result_under_product_cat = cursor.fetchall()
    except Exception as e:
        return JsonResponse({"success":False, "message":f"Problem occourd {str(e)}"})
    return render(request,'all_product_under_cat.html',{'result_under_product_cat':result_under_product_cat})
    



def sign_out(request):    
    request.session.flush()
    return redirect('login') 



