from django.db import connection

def category_processor(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, category_name FROM category_catrgory ORDER BY category_name ASC"
        )
        show_all_category = cursor.fetchall()

    return {'show_all_category': show_all_category}