$(document).ready(function () {

  // SEARCH
  $('#search-form').on('keyup submit', function (e) {
    e.preventDefault();

    let query = $('#search-input').val().trim();

    $.ajax({
      url: PRODUCT_SEARCH_URL,
      data: {
        q: query,
        page: 1
      },
      success: function (response) {
        $('#product-container').html(response.html);
      }
    });
  });

  // PAGINATION (AJAX)
  $(document).on('click', '.js-page', function (e) {
    e.preventDefault();

    let page = $(this).data('page');
    let query = $('#search-input').val().trim();

    $.ajax({
      url: PRODUCT_SEARCH_URL,
      data: {
        q: query,
        page: page
      },
      success: function (response) {
        $('#product-container').html(response.html);
      }
    });
  });

});
