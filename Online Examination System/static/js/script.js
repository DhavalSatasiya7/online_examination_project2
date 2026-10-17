document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form");

    form.addEventListener("submit", function(e){

        let username =
        document.querySelector(
        "input[name='username']").value;

        let password =
        document.querySelector(
        "input[name='password']").value;

        if(username.trim()==="" ||
           password.trim()===""){

            alert(
            "Username and Password are required!");

            e.preventDefault();
        }
    });

});