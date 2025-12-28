$(document).ready(function() {
    function load_users(query = '', page = 1) {
        $.ajax({
            url: all_user_search,
            data: { q: query, page: page },
            dataType: "json",
            success: function(data) {
                $('#user_table_data').html(data.html);
                $('#user_table_pagination').html(data.pagination_html);
            }
        });
    }

    // Live search
    $('#all_user_search').on('keyup', function() {
        let query = $(this).val();
        load_users(query, 1);  // Always start from page 1 when searching
    });

    // Handle pagination click
    $(document).on('click', '.page-link', function(e) {
        e.preventDefault();
        let page = $(this).data('page');
        let query = $('#all_user_search').val();
        load_users(query, page);
    });
});
