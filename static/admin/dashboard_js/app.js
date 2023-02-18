let admins = document.getElementById("admins")
let menthors = document.getElementById("menthors")
let students = document.getElementById("students")
let admins_container = document.getElementById("admins-container")
let menthors_container = document.getElementById("menthors-container")
let students_container = document.getElementById("students-container")
let person_count = 0
let main_arr = []
let x = admins_container
let nav = document.querySelector(".nav")
menthors.onclick = () => turn(menthors_container)
admins.onclick = () => turn(admins_container)
students.onclick = () => turn(students_container)
function turn(y) {

  if (x != y && !form.classList[1] && nav.style.opacity !== -5) {
    x.classList.add("none")
    y.classList.remove("none")
    x = y
  }

}



// ===================================================================================================
// verevum admin student menthor ejeri popoxutyunn a

let button_admins = document.querySelector(".for-admins")
let button_menthors = document.querySelector(".for-menthors")
let button_students = document.querySelector(".for-students")
let form = document.querySelector(".form")
let table = document.getElementById("table")
let main = document.querySelector(".main-container")

button_admins.onclick = () => formappear()
button_menthors.onclick = () => formappear()
button_students.onclick = () => formappear()
function formappear() {
  console.log(1);
  form.classList.add("appear")
  main.classList.add("blur")
}



// ===========================================================================================================
// add buttoni gorcery
arr_form = Array.from(form.children)
let bool = false
let form_btn = document.querySelector(".form-btn")
form_btn.onclick = person_adding

function person_adding() {
  let count = 0
  for (let i = 1; i < arr_form.length - 1; i++) {
    let value
    if (i == 5) {
      value = ""
      value = arr_form[i].children[1].children[1].value
    } else if (i > 5) {
      value = ""
      value = arr_form[i].children[1].children[0].value
    } else {
      value = ""
      value = arr_form[i].children[1].value
    }

    if (value) {
      count++
    }
  }
  let obj = {}
  obj.password = arr_form[6].children[1].children[0].value
  if (arr_form[6].children[1].children[0].value == arr_form[7].children[1].children[0].value && count == 7) {
    if (!bool) {
      let count2 = 3







      let tableA = document.getElementById("tableA")
      let tableM = document.getElementById("tableM")
      let tableS = document.getElementById("tableS")

      let div = document.createElement("div")
      div.classList.add("person")
      div.classList.add(`person${person_count}`)
      person_count++
      for (let i = 1; i < 5; i++) {
        let child = document.createElement("div")
        child.classList.add("item")
        child.classList.add(`item${i}`)

        if (i == 1) {
          let text_div = document.createElement("div")
          text_div.classList.add("item1-children")
          let p = document.createElement("p")
          obj.firstname = arr_form[1].children[1].value

          obj.lastname = arr_form[2].children[1].value

          p.innerHTML = `${arr_form[1].children[1].value} ${arr_form[2].children[1].value}`
          text_div.appendChild(p)
          let p2 = document.createElement("p")
          p2.classList.add("usName")
          obj.username = arr_form[4].children[1].value

          p2.innerHTML = arr_form[4].children[1].value
          text_div.appendChild(p2)
          child.appendChild(text_div)
        } else if (i > 1 && i < 4) {
          obj.email = arr_form[3].children[1].value

          obj.phone = arr_form[5].children[1].children[1].value
          let p = document.createElement("p")
          if (i == 2) {
            p.innerHTML = arr_form[count2].children[1].value
          } else {
            p.innerHTML = `+374 ${arr_form[count2].children[1].children[1].value}`
          }

          child.appendChild(p)
          count2 += 2
        } else {
          let icon1 = document.createElement("ion-icon")
          icon1.name = "trash-outline"
          icon1.classList.add("delete")
          icon1.classList.add("person-icon")
          child.appendChild(icon1)
          let icon2 = document.createElement("ion-icon")
          icon2.name = "create-outline"
          icon2.classList.add("edit")
          icon2.classList.add("person-icon")
          child.appendChild(icon2)
          icon1.onclick = function (e) {
            e.target.parentElement.parentElement.remove()
            let personn = e.target.parentElement.parentElement.classList[1]
          }
          icon2.onclick = function (e) {
            let index = e.target.parentElement.parentElement.classList[1].slice(6)
            form.classList.add("appear")
            main.classList.add("blur")
            let my_object = main_arr[index]

            arr_form[1].children[1].value = my_object.firstname
            arr_form[2].children[1].value = my_object.lastname
            arr_form[3].children[1].value = my_object.email
            arr_form[4].children[1].value = my_object.username
            arr_form[5].children[1].children[1].value = my_object.phone
            arr_form[6].children[1].children[0].value = my_object.password
            arr_form[7].children[1].children[0].value = my_object.password
            bool = true
            my_object.bool = true



          }
        }
        div.appendChild(child)

      }
      for (let i = 0; i < arr_form.length - 1; i++) {
        if (i == 5) {
          arr_form[i].children[1].children[1].value = ""
        } else if (i > 5) {
          arr_form[i].children[1].children[0].value = ""
        }
        else {
          arr_form[i].children[1].value = ""
        }

      }


      let y
      if (x == admins_container) {
        y = tableA
      } else if (x == menthors_container) {
        y = tableM
      } else if (x == students_container) {
        y = tableS
      }
      y.appendChild(div)
      form.classList.remove("appear")
      main.classList.remove("blur")



      //   if (bool) {
      //   console.log(fullname, email, phone, username);
      //   fullname = `${arr_form[1].children[1].value} ${arr_form[2].children[1].value}`
      //   email = arr_form[3].children[1].value
      //   phone = arr_form[5].children[1].value
      //   username = arr_form[4].children[1].value
      // }
      main_arr.push(obj)
    } else {
      form.classList.remove("appear")
      main.classList.remove("blur")
      let x
      for (let v = 0; v < main_arr.length; v++) {
        if (main_arr[v].bool == true) {
          x = v
          main_arr[v].bool = false
        }
      }
      main_arr[x].firstname = arr_form[1].children[1].value
      main_arr[x].lastname = arr_form[2].children[1].value
      main_arr[x].email = arr_form[3].children[1].value
      main_arr[x].username = arr_form[4].children[1].value
      main_arr[x].phone = arr_form[5].children[1].children[1].value
      main_arr[x].password = arr_form[6].children[1].children[0].value
      bool = false
      let myperson = document.querySelector(`.person${x}`)

      myperson.children[0].children[0].children[0].innerHTML = `${main_arr[x].firstname} ${main_arr[x].lastname}`
      myperson.children[0].children[0].children[1].innerHTML = main_arr[x].username
      myperson.children[1].children[0].innerHTML = main_arr[x].email
      myperson.children[2].children[0].innerHTML = `+374 ${main_arr[x].phone}`
      for (let i = 1; i < arr_form.length - 1; i++) {

        if (i === 5) {
          arr_form[5].children[1].children[1].value = ""
        } else if (i > 5) {
          arr_form[i].children[1].children[0].value = ""
        } else {
          arr_form[i].children[1].value = ""
        }
      }
    }
  }


}

// ===============================================================
// adding users to the table



let form_close = document.querySelector(".form-close")
form_close.onclick = close
let form_cancel = document.querySelector(".form-cancel")
form_cancel.onclick = close
function close() {
  form.classList.remove("appear")
  main.classList.remove("blur")
  bool = false

  for (let i = 1; i < arr_form.length - 4; i++) {


    arr_form[i].children[1].value = ""
  }
  arr_form[5].children[1].children[1].value = ""
  arr_form[6].children[1].children[0].value = ""
  arr_form[7].children[1].children[0].value = ""
}


// ================================================
// CANCEL EV CLOSE  buttonnery ashxatanqy


let eye = document.querySelector(".eye")
let close_eye = document.querySelector(".close-eye")
let password = document.getElementById("password")

let eye2 = document.querySelector(".eye2")
let close_eye2 = document.querySelector(".close-eye2")
let confirm_password = document.getElementById("confirm-password")
close_eye.onclick = () => eyes(close_eye, eye, password, "text")
eye.onclick = () => eyes(eye, close_eye, password, "password")
eye2.onclick = () => eyes(eye2, close_eye2, confirm_password, "password")
close_eye2.onclick = () => eyes(close_eye2, eye2, confirm_password, "text")


function eyes(x, y, z, o) {
  x.classList.add("none")
  y.classList.remove("none")
  z.type = o
}

// ============================================================
// let right=document.querySelector(".right")

// right.


let menu = document.querySelector(".menu")
let nonmenu = document.querySelector(".nonmenu")

menu.onclick = () => {
  nav.style.opacity = 1
  nonmenu.style.display = "block"
  menu.style.display = "none"
  nav.style.zIndex = 10

}


nonmenu.onclick = () => {
  nav.style.opacity = 0
  nonmenu.style.display = "none"
  menu.style.display = "block"
  nav.style.zIndex = -100
}