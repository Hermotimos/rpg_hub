
function getInformables() {
    var knowledgePacketId = this.getAttribute('id').split('_')[1]
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText)
        }
    };
    console.log(`http://127.0.0.1:8000/knowledge/almanac/informables/${knowledgePacketId}/`);
    xhttp.open("GET", `http://127.0.0.1:8000/knowledge/almanac/informables/${knowledgePacketId}/`);
    xhttp.send();
}

var informButtons = document.getElementsByClassName('icon-inform');
for (let item of informButtons) {
    item.addEventListener("click", getInformables);
}
