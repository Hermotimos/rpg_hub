
// Pierwszy znaleziony paragraf dostaje wygrubienie
var paragraph = document.getElementsByClassName('font-18')[0]
paragraph.style.fontWeight = 'bold';




// AJAX może sięgać po pliki tylko na tym samym serwerze.
// Dlatego dalsze przykłady są na localhost, na porcie gdzie jest odpalone Django (http://127.0.0.1:8000)


// Wyprintuje 123 po wysłaniu żądania (onload = po send)
var xhttp = new XMLHttpRequest();
xhttp.onload = function() {
  console.log(123);
};
xhttp.open("GET", "http://127.0.0.1:8000/static/img/skadia.png");
xhttp.send();
console.log(xhttp.readyState);
// xhttp.readyState zawiera status XMLHttpRequest:
//      0: request not initialized
//      1: server connection established
//      2: request received
//      3: processing request
//      4: request finished and response is ready



// Zwróci błąd dla URL nieistniejącego na serwerze: GET http://127.0.0.1:8000/no-such-file 404 (Not Found)
var xhttp = new XMLHttpRequest();
xhttp.onload = function() {
  console.log(123);
};
xhttp.open("GET", "http://127.0.0.1:8000/no-such-file");
xhttp.send();
console.log(xhttp.readyState);








// AJAX. Jeśli mamy >1 zadanie dla AJAX na stronie, to tworzy się:
//      * 1 funkcję obsługującą obiekt XMLHttpRequest
//      * po 1 callback function na taska

function loadDoc(url, cFunction) {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = function() {cFunction(this);}
  xhttp.open("GET", url);
  xhttp.send();
}

function myFunction1(xhttp) {
  // action goes here
}

function myFunction2(xhttp) {
  // action goes here
}

loadDoc("url-1", myFunction1);
loadDoc("url-2", myFunction2);




// .readyState - property zawierające aktualny stan XMLHttpRequest
// (0: not initialized, 1: server connection established, 2: request received, 3: processing request, 4: request finished, response is ready)

// .onreadystatechange - property zawierające funkcję callback do wywołania za każdym razem, gdy zmienia się stan XMLHttpRequest

// Ta funkcja będzie printować do konsoli każdą zmianę stanu XMLHttpRequest

function loadDoc() {
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        console.log(this.readyState)
    };
    xhttp.open("GET", "http://127.0.0.1:8000/static/img/skadia.png");
    xhttp.send();
}

loadDoc()





// example call of Django view
// prints json console: {"first": 1, "second": "temp Syngir, Murkon", "third": [1, 2, 3, 4]}

/*
    # in technicalities app views.py
    def example_json_view(request):
        from django.http import JsonResponse
        return JsonResponse(
            {"first": 1, "second": "temp Syngir, Murkon", "third": [1, 2, 3, 4]}
        )

    # in urls.py
    path('example-json/', views.example_json_view, name='example-json'),

*/

function loadDoc() {
  const xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          console.log(this.responseText)
      }
  };
  xhttp.open("GET", "http://127.0.0.1:8000/technicalities/example-json/");
  xhttp.send();
}

loadDoc()

