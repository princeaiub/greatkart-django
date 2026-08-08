def cart_count_processor(request):
    cart = request.session.get('cart',{})
    cart_count = sum(cart.values())
    return {
        'cart_count':cart_count
    }

def login_processor(request):
    cust_user_name= request.session.get('cust_first_name')
    photo_customer_user = request.session.get('photo_customer_user')
    return{"cust_user_name":cust_user_name,'photo_customer_user':photo_customer_user}