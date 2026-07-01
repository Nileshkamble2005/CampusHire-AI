




function showStudent(){

    document.getElementById("studentFields").style.display="block";
    document.getElementById("recruiterFields").style.display="none";

    document.getElementsByName("college")[0].required=true;
    document.getElementsByName("branch")[0].required=true;
    document.getElementsByName("year")[0].required=true;

    document.getElementsByName("company")[0].required=false;
    document.getElementsByName("designation")[0].required=false;

}

function showRecruiter(){

    document.getElementById("studentFields").style.display="none";
    document.getElementById("recruiterFields").style.display="block";

    document.getElementsByName("college")[0].required=false;
    document.getElementsByName("branch")[0].required=false;
    document.getElementsByName("year")[0].required=false;

    document.getElementsByName("company")[0].required=true;
    document.getElementsByName("designation")[0].required=true;

}


// ==========================
// Show / Hide Password
// ==========================

function togglePassword(inputId, button){

    const input = document.getElementById(inputId);

    const icon = button.querySelector("i");

    if(input.type === "password"){

        input.type = "text";

        icon.classList.remove("bi-eye");

        icon.classList.add("bi-eye-slash");

    }

    else{

        input.type = "password";

        icon.classList.remove("bi-eye-slash");

        icon.classList.add("bi-eye");

    }

}

// ==========================
// Password Strength
// ==========================

function checkStrength(){

    let password = document.getElementById("password").value;

    let bar = document.getElementById("strengthBar");

    let text = document.getElementById("strengthText");

    if(password.length < 6){

        bar.style.width="30%";

        bar.className="progress-bar bg-danger";

        text.innerHTML="Weak Password";

    }

    else if(password.length < 10){

        bar.style.width="60%";

        bar.className="progress-bar bg-warning";

        text.innerHTML="Medium Password";

    }

    else{

        bar.style.width="100%";

        bar.className="progress-bar bg-success";

        text.innerHTML="Strong Password";

    }

}


// ==========================
// Password Match
// ==========================

function checkMatch(){

    let password = document.getElementById("password").value;

    let confirm = document.getElementById("confirmPassword").value;

    let message = document.getElementById("matchMessage");

    if(confirm.length===0){

        message.innerHTML="";

        return;

    }

    if(password===confirm){

        message.innerHTML="✅ Passwords Match";

        message.style.color="green";

    }

    else{

        message.innerHTML="❌ Passwords Do Not Match";

        message.style.color="red";

    }

}



// ==========================
// Email Validation
// ==========================

function validateEmail(){

    let email=document.getElementById("email").value;

    let message=document.getElementById("emailMessage");

    let pattern=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if(email===""){

        message.innerHTML="";
        return;

    }

    if(pattern.test(email)){

        message.innerHTML="✅ Valid Email";
        message.style.color="green";

    }

    else{

        message.innerHTML="❌ Invalid Email";
        message.style.color="red";

    }

}

function validatePhone(){

    let phone=document.getElementById("phone").value;

    let message=document.getElementById("phoneMessage");

    if(phone.length==0){

        message.innerHTML="";
        return;

    }

    if(phone.length==10){

        message.innerHTML="✅ Valid Number";
        message.style.color="green";

    }

    else{

        message.innerHTML="❌ Enter 10 Digits";
        message.style.color="red";

    }

}


document.querySelector("form").addEventListener("submit",function(){

    let btn=document.getElementById("registerBtn");

    btn.innerHTML="Registering...";

    btn.disabled=true;

});