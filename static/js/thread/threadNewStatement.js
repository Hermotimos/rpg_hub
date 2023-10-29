
function newStatement(e){

    // Event.preventDefault() prevents default handling of click action (stops page from reloading)
    e.preventDefault();

    // Get text from editor
    frames = document.getElementsByClassName('cke_wysiwyg_frame');
    ckeditortext = frames[0].contentDocument.activeElement.innerHTML;

    // Construct FormData object and feed it with form data
    var formData = new FormData();
    formData.append('thread_id', $('#thread_id').val());
    formData.append('author_id', $('#id_author').val());
    formData.append('ckeditortext', ckeditortext);
    formData.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
    formData.append('file', document.getElementById('id_image').files[0]);

    // Send async request with form data
    // processData and contentType required to use FormData
    $.ajax({
        type:'POST',
        url:'/communications/statement-create',
        processData: false,
        contentType: false,
        data: formData,
    });

    // Clear text from editor
    document.getElementsByClassName('cke_wysiwyg_frame')[0].contentDocument.activeElement.innerText = null;
    // Clear file upload
    document.getElementById('id_image').value = null;
}
// Attach an event handler to the form element with the id of 'post-form' when a submit event occurs.
// The handler specifies that the newStatement function should be executed when the form is submitted.
$(document).on('submit', '#post-form', newStatement);
