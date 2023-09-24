
function newStatement(e){
    // Event.preventDefault() prevents default handling of click action (stops page from reloading)
    e.preventDefault();

    frames = document.getElementsByClassName('cke_wysiwyg_frame');
    ckeditortext = frames[0].contentDocument.activeElement.innerHTML;

    var formData = new FormData();
    formData.append('thread_id', $('#thread_id').val());
    formData.append('author_id', $('#id_author').val());
    formData.append('ckeditortext', ckeditortext);
    formData.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
    formData.append('file', document.getElementById('id_image').files[0]);

    $.ajax({
        type:'POST',
        url:'/communications/statement-create',

        // processData and contentType required to use FormData
        processData: false,
        contentType: false,
        data: formData,

        success: function(data){
         //alert(data)
        }
    });

    document.getElementsByClassName('cke_wysiwyg_frame ')[0].contentDocument.activeElement.innerText = null;
    document.getElementById('id_image').value = null;
}

$(document).on('submit','#post-form',newStatement);