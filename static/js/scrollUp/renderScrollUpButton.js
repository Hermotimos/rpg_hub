
// Render scrollUp button in the bottom right corner
function renderScrollUpButton() {

    var anchor = document.getElementById('scrollup');
    var url = anchor.getAttribute('value');

    anchor.style = `
        background: url(${url}) 0px 0px / cover transparent;
        width: 64px;
        height: 64px;
        right: 10px;
        bottom: 10px;
        position: fixed;
        display: none;
    `;
}

renderScrollUpButton();
