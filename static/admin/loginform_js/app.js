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