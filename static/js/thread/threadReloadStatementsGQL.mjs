import { makeStatementHTML } from './makeStatementHTML.mjs';




function reloadStatements(){

    $.ajax({
        type: 'POST',
        url: `/graphql/`,   // GraphQL endpoint
        contentType: "application/json",
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

        success: function(response) {
            makeStatementHTML(response);
        },

    });
}



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