$(document).ready(function(){

    $('#password_chg_from').on('submit', function(e){
        e.preventDefault();
        var formData = new FormData(this);
        $('#loader').show();
        $.ajax({
            url: $('#password_chg_from').data('chnpassUrl'),
            type: 'POST',
            data: formData,
            processData: false,  // needed for file upload
            contentType: false,  // needed for file upload
            success: function(response)
            {
                $('#loader').hide();
                $('#formMessages_pass_change').stop(true, true).hide().empty();
                let messageHTML = "";
                if(response.success){
                    messageHTML = `<div class="alert alert-success" role="alert">${response.message}</div>`;
                    // $('#password_chg_for_activation_from')[0].reset();
                    // ✅ Disable all inputs to prevent resubmission
                    // $('#password_chg_from:input').prop('disabled', true);
                    // setTimeout(function() {
                    //     if (response.redirect_url) {
                    //         window.location.href = response.redirect_url;
                    //     }
                    // }, 1000);
                    $('#password_chg_from')[0].reset();
                }else {
                    // ❌ validation errors
                    if (response.errors) {
                        messageHTML = "<div class='alert alert-danger' role='alert'><ul>";
                        response.errors.forEach(function(err) {
                            messageHTML += `<li>${err}</li>`;
                        });
                        messageHTML += "</ul></div>";
                    } else if (response.message) {
                        // general error (like DB failure)
                        messageHTML = `<div class="alert alert-danger" role="alert">${response.message}</div>`;
                    }
                }

                // Show the message with fade-in
                $('#formMessages_pass_change').html(messageHTML).fadeIn(200);

                // Auto fade-out after 3 seconds
                setTimeout(function() {
                    $('#formMessages_pass_change').fadeOut("slow");
                }, 3000);
            },
            error: function(xhr, status, error) {
                $('#loader').hide();
                $('#formMessages_pass_change').stop(true, true).hide().html(
                    `<div class="alert alert-danger" role="alert">Server error. Please try again.</div>`
                ).fadeIn(200);

                setTimeout(function() {
                    $('#formMessages_pass_change').fadeOut("slow");
                }, 10000);
            }


        });

    });
});