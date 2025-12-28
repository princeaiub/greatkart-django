$(document).ready(function() {
    $('#editUserForm').on('submit', function(e) {        
        e.preventDefault();
        var formData = new FormData(this);
        $('#loader').show();        
        
        $.ajax({
            url: editUserUrl,  // assuming you set data-url="{% url 'add_user' %}" in your form
            type: "POST",
            data: formData,
            processData: false,  // needed for file upload
            contentType: false,  // needed for file upload
            success: function(response) {
                $('#loader').hide();
                
                // Clear old messages
                $('#editformMessages').stop(true, true).hide().empty();

                let messageHtml = "";

                if (response.success) {
                    // ✅ success
                    
                    if(response.temporary_pass){
                        
                        messageHtml = `<div class="alert alert-success alert-dismissible fade show" role="alert">${response.message}
                        <br><strong>Temporary Password:</strong> ${response.temporary_pass}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>`;

                    }else{
                         messageHtml = `<div class="alert alert-success alert-dismissible fade show" role="alert">${response.message}
                         <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                         </div>`;
                    }
                    // location.reload();
                    // $('#editUserForm')[0].reset();
                    // $('#editformMessages').html(messageHtml).fadeIn(200);
                    // setTimeout(function(){
                    //     location.reload();

                    // },5000);
                    
                } else {
                    // ❌ validation errors
                    if (response.errors) {
                        messageHtml = "<div class='alert alert-danger alert-dismissible fade show' role='alert'><ul>";
                        response.errors.forEach(function(err) {
                            messageHtml += `<li>${err}</li>`;
                        });
                        messageHtml += "</ul> <button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button></div>";
                    } else if (response.message) {
                        // general error (like DB failure)
                        messageHtml = `<div class="alert alert-danger alert-dismissible fade show" role="alert">${response.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>`;
                    }
                }

                // Show the message with fade-in
                $('#editformMessages').html(messageHtml).fadeIn(200);
                $('html, body').animate({ scrollTop: 0 }, 'slow');
                 

                // Auto fade-out after 3 seconds
                // setTimeout(function() {
                //     $('#editformMessages').fadeOut("slow");
                // }, 3000);
            },
            error: function(xhr, status, error) {
                $('#loader').hide();
                $('#editformMessages').stop(true, true).hide().html(
                    `<div class="alert alert-danger" role="alert">Server error. Please try again.</div>`
                ).fadeIn(200);
                $('html, body').animate({ scrollTop: 0 }, 'slow');

                setTimeout(function() {
                    $('#editformMessages').fadeOut("slow");
                }, 10000);
            }
        });
    });
    // $('#activate_manually_checkbox').change(function(){
    //     if($(this).is(':checked'))
    //     {
    //         $('.hidden_field_temp_pass').show();
    //     }else
    //         {
    //             $('.hidden_field_temp_pass').hide();
    //         }

    // });
});
