//
// Screen Test Javascript (white, black, red, green, blue)
//

var current = 1;

function testChange()
{
    if (current === 0)
        document.body.style.background = "#ffffff";
    else if (current == 1)
        document.body.style.background = "#000000";
    else if (current == 2)
        document.body.style.background = "#ff0000";
    else if (current == 3)
        document.body.style.background = "#00ff00";
    else if (current == 4)
        document.body.style.background = "#0000ff";

    current = ++current % 5;
}
