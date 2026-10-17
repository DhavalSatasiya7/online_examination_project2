document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("theme-toggle");

    if (!btn) return;

    // Restore saved mode
    if(localStorage.getItem("theme") === "dark"){

        document.body.classList.add("dark-mode");

        btn.innerHTML = "☀️ Light Mode";

    }

    btn.onclick = function(){

        document.body.classList.toggle("dark-mode");

        if(document.body.classList.contains("dark-mode")){

            localStorage.setItem("theme","dark");

            btn.innerHTML="☀️ Light Mode";

        }
        else{

            localStorage.setItem("theme","light");

            btn.innerHTML="🌙 Dark Mode";

        }

    };

});