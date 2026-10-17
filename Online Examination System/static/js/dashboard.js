// ================= PIE CHART =================

new Chart(document.getElementById("pieChart"),{

type:"doughnut",

data:{

labels:["PASS","FAIL"],

datasets:[{

data:[{{ pass_percent }},{{ fail_percent }}],

backgroundColor:[

"#198754",

"#dc3545"

],

borderWidth:0

}]

},

options:{

responsive:true,

plugins:{

legend:{

position:"bottom"

}

},

cutout:"65%"

}

});




// ================= BAR CHART =================

new Chart(document.getElementById("barChart"),{

type:"bar",

data:{

labels:[

"Students",

"Subjects",

"Questions",

"Exams"

],

datasets:[{

label:"Total Count",

data:[

{{ total_students }},

{{ total_subjects }},

{{ total_questions }},

{{ total_exams_taken }}

],

backgroundColor:[

"#4e73df",

"#1cc88a",

"#f6c23e",

"#36b9cc"

],

borderRadius:12

}]

},

options:{

responsive:true,

plugins:{

legend:{

display:false

}

},

scales:{

y:{

beginAtZero:true

}

}

}

});




// ================= LINE CHART =================

new Chart(document.getElementById("lineChart"),{

type:"line",

data:{

labels:[

"Students",

"Subjects",

"Questions",

"Exams"

],

datasets:[{

label:"Statistics",

data:[

{{ total_students }},

{{ total_subjects }},

{{ total_questions }},

{{ total_exams_taken }}

],

fill:true,

backgroundColor:"rgba(78,115,223,0.15)",

borderColor:"#4e73df",

borderWidth:4,

tension:0.4,

pointRadius:6,

pointHoverRadius:8

}]

},

options:{

responsive:true,

plugins:{

legend:{

display:true

}

},

scales:{

y:{

beginAtZero:true

}

}

}

});