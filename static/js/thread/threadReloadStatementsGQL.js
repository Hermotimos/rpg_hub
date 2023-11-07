
var uniqueStatementIds = [];
var currentProfileId = document.getElementById('display').getAttribute('current-profile-data');
var firstLoad = true;


function reloadStatements(){

    $.ajax({
        type: 'POST',
        data: JSON.stringify({
            query: `
                query MyQuery {
                    statementsByThreadId(threadId: ${document.getElementById('thread_id').getAttribute('value')}) {
                        id
                        text
                        author {
                            id
                            status
                            userImage {url}
                            character {fullname}
                            user {username}
                        }
                        thread {
                            kind
                            isEnded
                        }
                        image {url}
                        createdDatetime
                        seenBy {
                            id
                            character {fullname}
                            image {url}
                            userImage {url}
                            user {username}
                        }
                    }
                }
            `
        }),
        variables: {
            "threadId": $(document.getElementById('thread_id').getAttribute('value'))
        },
        // processData: false,
        // contentType: false,

        // GraphQL endpoint
        url: `/graphql/`,
        contentType: "application/json",
        // headers: {
        //   Authorization: "bearer ***********"
        // },

        success: function(response){
            console.log(response);
            var statements = response.data.statementsByThreadId;

            for (var num in statements)
            {
                var statement = statements[num];

                // Skip iteration when Statement is already present
                if (uniqueStatementIds.includes(statement.id)) {
                    continue;
                }

                var threadKind = statements[num].thread.kind;
                var isGmAndDebate = ( statements[num].author.status == 'gm' && threadKind == 'Debate' );
                var isLastStatement = ( num == statements.length - 1 );

                var anchor = ``;
                if (isLastStatement) {
                    anchor = `<a class="anchor anchor3" id="page-bottom"></a>`
                };

                if ( statements[num].image.url !== '' ) {
                    var stmtImage = `<p><img class="img-fluid mx-auto d-block" src="${statements[num].image.url}"></p>`
                } else {
                    var stmtImage = ``
                };


                // TODO TEMP replace this with the code at the bottom of the file when Syngir, Murkon meet Dalamar
                var authorImg;
                if ( threadKind == 'Announcement' ) {

                    authorImg = `
                        <img class="img-fluid rounded" src="${statements[num].author.userImage.url}">
                        <figcaption class="font-12 font-italic text-center pt-1">
                            ${statements[num].author.user.username}
                        </figcaption>
                    `
                } else if ( threadKind == 'Debate' ) {

                    if ( statements[num].author.id == 18 && [82,93].includes(currentProfileId) ) {
                        authorImg = `
                             <img class="img-fluid rounded-circle" src="media/profile_pics/profile_Dalamar_Szarogwardzista_2.jpg">
                             <figcaption class="font-12 font-italic text-center pt-1">
                                Dalamar Szarogwardzista
                             </figcaption>
                        `
                    } else {
                        authorImg = `
                             <img class="img-fluid rounded-circle" src="${statements[num].author.image.url}">
                             <figcaption class="font-12 font-italic text-center pt-1">
                                ${statements[num].author.character.fullname}
                             </figcaption>
                        `
                    };
                };
                // TODO TEMP END replace


                if ( !statements[num].thread.isEnded ) {

                    var seenByImgs = ``;
                    var seenByProfiles = statements[num].seenBy;
                    try {
                        var nextnum = parseInt(num) + 1;
                        var seenByProfilesNextStatementIds = [];
                        for ( var idx in statements[nextnum].seenBy ) {
                            seenByProfilesNextStatementIds.push(statements[nextnum].seenBy[idx].id);
                        };
                    }
                    catch(err) {
                        var seenByProfilesNextStatementIds = [];
                    }

                    for (var cnt in seenByProfiles) {
                        var imgSmall = ``;
                        if ( !seenByProfilesNextStatementIds.includes(seenByProfiles[cnt].id) && !(seenByProfiles[cnt].id == statements[num].author.id)) {

                            if ( threadKind == 'Debate' ) {
                                imgSmall = `<img class="portait img-sm border border-dark rounded-circle mr-1" src="${seenByProfiles[cnt].image.url}">`;
                            } else if ( threadKind == 'Announcement' ) {
                                imgSmall = `<img class="portait img-sm border border-dark rounded mr-1" src="${seenByProfiles[cnt].userImage.url}">`;
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


                var stmtText = `<div class="statement">${statements[num].text}</div>`;
                var createdAt = statements[num].createdDatetime;

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

                // After processing, add the statement's ID to the uniqueStatementIds array
                uniqueStatementIds.push(statement.id);

                setTimeout(function() {
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


// call before page is ready
reloadStatements();

// subsequently call with interval
$(document).ready(function(){
    setInterval(reloadStatements,3000);
})



// TODO TEMP replace above Syngir, Murkon with this when they meet Dalamar
// var authorImg;
// if ( threadKind == 'Announcement' ) {

//    authorImg = `
//        <img class="img-fluid rounded" src="${statements[num].author.userImage.url}">
//        <figcaption class="font-12 font-italic text-center pt-1">
//            ${statements[num].author.user.username}
//        </figcaption>
//    `
// } else if ( threadKind == 'Debate' ) {

//    authorImg = `
//         <img class="img-fluid rounded-circle" src="${statements[num].author.image.url}">
//         <figcaption class="font-12 font-italic text-center pt-1">
//            ${statements[num].author.character.fullname}
//         </figcaption>
//    `
// };