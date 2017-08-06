var myList = ['First Option','Second Option','Third Option'];

function makeOL(array) {
    var list = document.createElement('ol');

    for(var i = 0; i < array.length; i++) {
        var item = document.createElement('li');
        item.appendChild(document.createTextNode(array[i]));
        list.appendChild(item);
    }

    return list;
}

document.getElementById('partner-list-preview').appendChild(makeOL(myList));