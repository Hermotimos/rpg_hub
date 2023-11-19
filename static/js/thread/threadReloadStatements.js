
var uniqueStatementIds = [];
var currentProfileId = document.getElementById('display').getAttribute('current-profile-data');
var firstLoad = true;


function reloadStatements(){

    var formData = new FormData();
    // CSRF token required for POST requests
    formData.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
    formData.append('threadId', document.getElementById('thread_id').getAttribute('value'));
    formData.append('currentProfileId', currentProfileId);

    $.ajax({
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,

        // Django view endpoint
        // url: `/communications/statements/${document.getElementById('thread_id').getAttribute('value')}/`,

        // Django REST Framework view endpoint
        url: `/api/statements/thread/${document.getElementById('thread_id').getAttribute('value')}/`,

        success: function(response) {
            console.log(response);
            var statements = response.results;

            for (var num in statements)
            {
                // Skip iteration when Statement is already present
                var statement = statements[num];
                if (uniqueStatementIds.includes(statement.id)) {
                    continue;
                }


                if ( statements[num].image_obj.url !== '' ) {
                    var stmtImage = `<p><img class="img-fluid mx-auto d-block" src="${statements[num].image_obj.url}"></p>`
                } else {
                    var stmtImage = ``
                };


                var threadKind = statements[num].thread_obj.kind;
                var authorImg;
                if ( threadKind == 'Announcement' ) {

                    authorImg = `
                        <img class="img-fluid rounded" src="${statements[num].author_obj.user_image_obj.url}">
                        <figcaption class="font-12 font-italic text-center pt-1">
                            ${statements[num].author_obj.user_obj.username}
                        </figcaption>
                    `
                } else if ( threadKind == 'Debate' ) {

                    // TODO TEMP when Syngir, Murkon meet Dalamar, then remove the block with hardcoded id-s
                    if ( statements[num].author_obj.id == 18 && [82,93].includes(currentProfileId) ) {
                        authorImg = `
                             <img class="img-fluid rounded-circle" src="media/profile_pics/profile_Dalamar_Szarogwardzista_2.jpg">
                             <figcaption class="font-12 font-italic text-center pt-1">
                                Dalamar Szarogwardzista
                             </figcaption>
                        `
                    } else {
                        authorImg = `
                             <img class="img-fluid rounded-circle" src="${statements[num].author_obj.image_obj.url}">
                             <figcaption class="font-12 font-italic text-center pt-1">
                                ${statements[num].author_obj.character_obj.fullname}
                             </figcaption>
                        `
                    };
                    // TODO TEMP END
                };



                if ( !statements[num].thread_obj.is_ended ) {

                    var seenByImgs = ``;
                    var seenByProfiles = statements[num].seen_by_objs;
                    try {
                        var nextnum = parseInt(num) + 1;
                        var seenByProfilesNextStatementIds = [];
                        for ( var idx in statements[nextnum].seen_by_objs ) {
                            seenByProfilesNextStatementIds.push(statements[nextnum].seen_by_objs[idx].id);
                        };
                    }
                    catch(err) {
                        var seenByProfilesNextStatementIds = [];
                    }

                    for (var cnt in seenByProfiles) {
                        var imgSmall = ``;
                        if ( !seenByProfilesNextStatementIds.includes(seenByProfiles[cnt].id) && !(seenByProfiles[cnt].id == statements[num].author_obj.id)) {

                            if ( threadKind == 'Debate' ) {
                                imgSmall = `<img class="portait img-sm border border-dark rounded-circle mr-1" src="${seenByProfiles[cnt].image_obj.url}">`;
                            } else if ( threadKind == 'Announcement' ) {
                                imgSmall = `<img class="portait img-sm border border-dark rounded mr-1" src="${seenByProfiles[cnt].user_image_obj.url}">`;
                            };
                        };
                        seenByImgs += imgSmall;
                    };


                    var seenByRow = `
                        <div class="row mt-2 ml-1">
                            <div>
                                ${seenByImgs}
                            </div>
                        </div>
                    `
                } else {
                    var seenByRow = ``
                };


                var isGmAndDebate = ( statements[num].author_obj.status == 'gm' && threadKind == 'Debate' );
                var stmtText = `<div class="statement">${statements[num].text}</div>`;
                var createdAt = statements[num].created_datetime;

                if ( isGmAndDebate ) {

                    var stmtRow = `
                        <div class="col-12 font-18 font-italic text-justify">
                            ${stmtText}
                            ${stmtImage}
                            ${seenByRow}
                        </div>
                    `
                } else {

                    var stmtRow = `
                        <div class="col-2 pr-1 pr-sm-0">
                            <figure class="align-top mx-auto mb-0 px-lg-3 pt-1">
                                ${authorImg}
                            </figure>
                        </div>
                        <div class="col-10 font-18 font-italic text-justify mt-n1">
                            <small class="text-muted">
                                ${createdAt}
                            </small>
                            ${stmtText}
                            ${stmtImage}
                            ${seenByRow}
                        </div>
                    `
                };


                var stmt = `
                    <div class="container-fluid px-0 mt-4">
                        <div class="row">
                            ${stmtRow}
                        </div>
                    </div>

                    `

                $("#display").append(stmt);

                // After processing, add the statement's ID to the uniqueStatementIds array
                uniqueStatementIds.push(statement.id);

                setTimeout(() => {
                    scrollToCKEditor();
                }, 500);

            }
        }

    });
}


function scrollToCKEditor() {
    // If statements are loaded for the first time, scroll down to CKEditor
    // after 1 sec delay to allow for visual display of statements
    if (firstLoad && document.getElementById('display').hasChildNodes()) {
        document.getElementById('div_id_text').scrollIntoView({ behavior: 'smooth' });
        firstLoad = false;
    };
};


// first call before page is ready
reloadStatements();

// subsequently call with interval
$(document).ready(function(){
    setInterval(reloadStatements,3000);
})

