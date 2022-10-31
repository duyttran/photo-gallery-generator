/*
This js manages different supported gallery actions
 - click to get full size image in border dark box, and click to go back to gallery
 - left arrow to go to prev full size image
 - right arrow to go to next full size image

Some tips were taken from
https://timnwells.medium.com/enhancing-our-simple-responsive-image-gallery-746549cd2f11
*/
let darkBoxVisible = false;

window.addEventListener('load', (event) => {
    let images = document.querySelectorAll("img");
    if(images !== null && images !== undefined && images.length > 0) {
        images.forEach(function(img) {
            img.addEventListener('click', (evt) => {
                let raw_photo_url = img.src.replace('compressed_photos', 'raw_photos')
                showDarkbox(raw_photo_url);
            });
        });
    }
});

function zeroPadNum(num) {
    if (num < 10) {
        return '00' + num;
    } else if (num < 100) {
        return '0' + num;
    } else {
        return num;
    }
}

function prevImageSrc(src) {
    strNum = src.substring(src.length - 7, src.length - 4);
    prevNum = parseInt(strNum) - 1;
    if (prevNum <= 0) {
        prevNum = 1
    }
    return src.substring(0, src.length - 7) + zeroPadNum(prevNum) + src.substring(src.length - 4, src.length);
}

function nextImageSrc(src) {
    strNum = src.substring(src.length - 7, src.length - 4);
    nextNum = parseInt(strNum) + 1;
    return src.substring(0, src.length - 7) + zeroPadNum(nextNum) + src.substring(src.length - 4, src.length);
}

function showDarkbox(url) {
    console.log("darkbox url " + url);
    if(!darkBoxVisible) {
        let y = window.scrollY + 50;

        // Create the darkBox
        var div = document.createElement("div");
        div.id = "darkbox";
        div.innerHTML = '<img class="darkboximg" id="darkboximg" src="'+url+'" />';
        document.body.appendChild(div);
        let box = document.getElementById("darkbox");
        box.style.top = y.toString()+"px";
        box.addEventListener('click', (event) => {
            // Remove it
            let element = document.getElementById("darkbox");
            element.parentNode.removeChild(element);

            darkBoxVisible = false;
        });
        document.addEventListener('keydown', (event) => {
            let element = document.getElementById("darkboximg");
            if (event.key == "ArrowRight") {
                console.log("before arrow right " + element.src);
                element.src = nextImageSrc(element.src);
                console.log("after arrow right " + element.src);
            } else if (event.key =="ArrowLeft") {
                console.log("before arrow left " + element.src);
                element.src = prevImageSrc(element.src);
                console.log("after arrow left " + element.src);
            }
        });

        darkBoxVisible = true;

    } else {
        // Remove it
        let element = document.getElementById("darkbox");
        element.parentNode.removeChild(element);

        darkBoxVisible = false;
    }
}
