$(document).ready(function() {
    $('#customer_login_form').on('submit', function(e) {        
        e.preventDefault();
        var formData = new FormData(this);
        $('#loader').show();       
        document.body.scrollTop = 0; // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera 
        
        $.ajax({
            url: customer_login,  // assuming you set data-url="{% url 'add_user' %}" in your form
            type: "POST",
            data: formData,
            processData: false,  // needed for file upload
            contentType: false,  // needed for file upload
            success: function(response) {
                $('#loader').hide();
                
                // Clear old messages
                $('#formMessages').stop(true, true).hide().empty();

                let messageHtml = "";

                if (response.success) {
                    // ✅ success
                    
                    messageHtml = `<div class="alert alert-success" role="alert">${response.message}</div>`;
                    // $('#editUserForm')[0].reset();
                    $('#formMessages').html(messageHtml).fadeIn(200);
                    setTimeout(function(){
                        location.reload();

                    },5000);
                    window.location.href = response.redirect_url;
                } else {
                    // ❌ validation errors
                    if (response.errors) {
                        messageHtml = "<div class='alert alert-danger' role='alert'><ul>";
                        response.errors.forEach(function(err) {
                            
                            
                            
                            messageHtml += `<li>${err}</li>`;
                            
                        });
                        messageHtml += "</ul></div>";
                    } else if (response.message) {
                        // general error (like DB failure)
                        messageHtml = `<div class="alert alert-danger" role="alert">${response.message}</div>`;
                    }
                }

                // Show the message with fade-in
                $('#formMessages').html(messageHtml).fadeIn(200);

                // Auto fade-out after 3 seconds
                setTimeout(function() {
                    $('#formMessages').fadeOut("slow");
                }, 3000);
            },
            error: function(xhr, status, error) {
                $('#loader').hide();
                $('#formMessages').stop(true, true).hide().html(
                    `<div class="alert alert-danger" role="alert">Server error. Please try again.</div>`
                ).fadeIn(200);

                setTimeout(function() {
                    $('#formMessages').fadeOut("slow");
                }, 10000);
            }
        });
    });

});