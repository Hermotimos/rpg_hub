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
                            image {url}
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
