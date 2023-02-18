let password = document.getElementById("password")
let eye = document.querySelector(".eye")
let close_eye = document.querySelector(".close-eye")
close_eye.onclick = () => eyes(close_eye, eye, password, "text")
eye.onclick = () => eyes(eye, close_eye, password, "password")
function eyes(x, y, z, o) {
    x.classList.add("none")
    y.classList.remove("none")
    z.type = o
}

let btnLogin = document.querySelector('.btn')
btnLogin.onclick = function () {
    form.classList.remove('opacity')
    section.classList.add('blur')
}

let section = document.querySelector('.container')
let form = document.querySelector('.form2')
let btn_cancel = document.querySelector('.btn-cancel')
let close = document.querySelector('.delete-icon')
function closing() {
    form.classList.add('opacity')
    section.classList.remove('blur')
}

btn_cancel.onclick = closing
close.onclick = closing