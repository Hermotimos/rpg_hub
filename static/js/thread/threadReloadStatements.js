
var firstLoad = true;

function reloadStatements(){
    $.ajax({
        type: 'GET',
        url: `/communications/statements/${document.getElementById('thread_id').getAttribute('value')}/`,
        success: function(response){
            console.log(response);
            $("#display").empty();

            for (var num in response.statements)
            {

                var threadKind = response.statements[num].thread_obj.kind;
                var isGmAndDebate = ( response.statements[num].author_obj.status == 'gm' && threadKind == 'Debate' );
                var isLastStatement = ( num == response.statements.length - 1 );

                var anchor = ``;
                if (isLastStatement) {
                    anchor = `<a class="anchor anchor3" id="page-bottom"></a>`
                };

                if ( response.statements[num].image_obj.url !== '' ) {
                    var stmtImage = `<p><img class="img-fluid mx-auto d-block" src="${response.statements[num].image_obj.url}"></p>`
                } else {
                    var stmtImage = ``
                };


                // TODO TEMP replace this with the code at the bottom of the file when Syngir, Murkon meet Dalamar
                var authorImg;
                if ( threadKind == 'Announcement' ) {

                    authorImg = `
                        <img class="img-fluid rounded" src="${response.statements[num].author_obj.user.image.url}">
                        <figcaption class="font-12 font-italic text-center pt-1">
                            ${response.statements[num].author_obj.user.username}
                        </figcaption>
                    `
                } else if ( threadKind == 'Debate' ) {

                    if ( response.statements[num].author_obj.id == 18 && [82,93].includes(response.currentProfileId) ) {
                        authorImg = `
                             <img class="img-fluid rounded-circle" src="media/profile_pics/profile_Dalamar_Szarogwardzista_2.jpg">
                             <figcaption class="font-12 font-italic text-center pt-1">
                                Dalamar Szarogwardzista
                             </figcaption>
                        `
                    } else {
                        authorImg = `
                             <img class="img-fluid rounded-circle" src="${response.statements[num].author_obj.image.url}">
                             <figcaption class="font-12 font-italic text-center pt-1">
                                ${response.statements[num].author_obj.character.fullname}
                             </figcaption>
                        `
                    };
                };
                // TODO TEMP END replace


                if ( !response.statements[num].thread_obj.is_ended ) {

                    var seenByImgs = ``;
                    var seenByProfiles = response.statements[num].seen_by_objs;
                    try {
                        var nextnum = parseInt(num) + 1;
                        var seenByProfilesNextStatementIds = [];
                        for ( var idx in response.statements[nextnum].seen_by_objs ) {
                            seenByProfilesNextStatementIds.push(response.statements[nextnum].seen_by_objs[idx].id);
                        };
                    }
                    catch(err) {
                        var seenByProfilesNextStatementIds = [];
                    }

                    for (var cnt in seenByProfiles) {
                        var imgSmall = ``;
                        if ( !seenByProfilesNextStatementIds.includes(seenByProfiles[cnt].id) && !(seenByProfiles[cnt].id == response.statements[num].author_id)) {

                            if ( threadKind == 'Debate' ) {
                                imgSmall = `<img class="portait img-sm border border-dark rounded-circle mr-1" src="${seenByProfiles[cnt].image.url}">`;
                            } else if ( threadKind == 'Announcement' ) {
                                imgSmall = `<img class="portait img-sm border border-dark rounded mr-1" src="${seenByProfiles[cnt].user.image.url}">`;
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


                var stmtText = `<div class="statement">${response.statements[num].text}</div>`
                var createdAt = response.statements[num].created_datetime;

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
                    ${anchor}
                    <div class="container-fluid px-0 mt-4">
                        <div class="row">
                            ${stmtRow}
                        </div>
                    </div>

                    `

                $("#display").append(stmt);

                setTimeout(function() {
                    scrollToCKEditor();
                }, 1000);

            }
        }
        /*
        ,
        error: function(response){
            alert('An error occured');
            // console.log('ggggggg', response);
        }
        */

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

// subsequent calls with interval
$(document).ready(function(){
    setInterval(reloadStatements,3000);
})



// TODO TEMP replace above Syngir, Murkon with this when they meet Dalamar
// var authorImg;
// if ( threadKind == 'Announcement' ) {

//    authorImg = `
//        <img class="img-fluid rounded" src="${response.statements[num].author_obj.user.image.url}">
//        <figcaption class="font-12 font-italic text-center pt-1">
//            ${response.statements[num].author_obj.user.username}
//        </figcaption>
//    `
// } else if ( threadKind == 'Debate' ) {

//    authorImg = `
//         <img class="img-fluid rounded-circle" src="${response.statements[num].author_obj.image.url}">
//         <figcaption class="font-12 font-italic text-center pt-1">
//            ${response.statements[num].author_obj.character.fullname}
//         </figcaption>
//    `
// };