function showTime() {
    var now = new Date();

    hour = now.getHours();
    minutes = now.getMinutes();
    seconds = now.getSeconds();

    if (hour < 10) hour = '0' + hour;
    if (minutes < 10) minutes = '0' + minutes;
    if (seconds < 10) seconds = '0' + seconds;

    document.getElementById('time').innerHTML = hour + ':' + minutes + ':' + seconds

    setTimeout('showTime()', 1000)
}
