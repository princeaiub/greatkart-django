from django.db import connection

def cart_count_processor(request):
    
    customer_id = request.session.get("customer_id")
    cart_count=0
    if customer_id:
        with connection.cursor() as cursor:
                cursor.execute("SELECT COALESCE(SUM(quantity),0) FROM cart WHERE customer_id=%s",[customer_id])
                cart_count= cursor.fetchone()[0]

                return {
                            'cart_count':cart_count
                        }

    else:   
        cart = request.session.get('cart',{})
        cart_count = sum(cart.values())
        return {
            'cart_count':cart_count
        }

def login_processor(request):
    cust_user_name= request.session.get('cust_first_name')
    photo_customer_user = request.session.get('photo_customer_user')
    return{"cust_user_name":cust_user_name,'photo_customer_user':photo_customer_user}