function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

document.querySelector("#set-color-btn").addEventListener("click", function () {
    let hexColor = document.querySelector("#neopixel-color").value;
    console.log('New color', hexColor);
    let colorVal = hexToRgb(hexColor);
    console.log(`/led_on/${colorVal.r}/${colorVal.g}/${colorVal.b}`);
    window.location = `/led_on/${colorVal.r}/${colorVal.g}/${colorVal.b}`;
});