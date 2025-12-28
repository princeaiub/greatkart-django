$(document).ready(function() {
    $('#add_product_from').on('submit', function(e) {    
        
        e.preventDefault();
        var formData = new FormData(this);
        $('#loader').show();        
        
        $.ajax({
            url: add_product,  // assuming you set data-url="{% url 'add_user' %}" in your form
            type: "POST",
            data: formData,
            processData: false,  // needed for file upload
            contentType: false,  // needed for file upload
            success: function(response) {
                $('#loader').hide();
                
                // Clear old messages
                $('#formMessages_add_product').stop(true, true).hide().empty();

                let messageHtml = "";

                if (response.success) {
                    // ✅ success
                    
                    messageHtml = `<div class="alert alert-success" role="alert">${response.message}</div>`;
                    $('#add_product_from')[0].reset();
                    $('#formMessages_add_product').html(messageHtml).fadeIn(200);
                    // setTimeout(function(){
                    //     location.reload();

                    // },5000);
                    
                } else {
                    // ❌ validation errors
                    if (response.product_error) {
                        messageHtml = "<div class='alert alert-danger' role='alert'><ul>";
                        response.product_error.forEach(function(err) {
                            messageHtml += `<li>${err}</li>`;
                        });
                        messageHtml += "</ul></div>";
                    } else if (response.message) {
                        // general error (like DB failure)
                        messageHtml = `<div class="alert alert-danger" role="alert">${response.message}</div>`;
                    }
                }

                // Show the message with fade-in
                $('#formMessages_add_product').html(messageHtml).fadeIn(200);

                // Auto fade-out after 3 seconds
                setTimeout(function() {
                    $('#formMessages_add_product').fadeOut("slow");
                }, 3000);
            },
            error: function(xhr, status, error) {
                $('#loader').hide();
                $('#formMessages_add_product').stop(true, true).hide().html(
                    `<div class="alert alert-danger" role="alert">Server error. Please try again.</div>`
                ).fadeIn(200);

                setTimeout(function() {
                    $('#formMessages_add_product').fadeOut("slow");
                }, 10000);
            }
        });
    });

});