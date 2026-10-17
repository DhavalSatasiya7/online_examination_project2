/* ==========================================================
   ONLINE EXAMINATION SYSTEM
   CLIENT-SIDE PROCTORING
   NO PROCTORING DATABASE TABLE
========================================================== */

(function () {

"use strict";


const config =
    window.EXAM_CONFIG || {};


const MAX_WARNINGS =
    config.maxWarnings || 3;


let stream = null;

let videoRecorder = null;

let audioRecorder = null;

let videoChunks = [];

let audioChunks = [];

let examSubmitted = false;

let warningCount = 0;

let faceModelReady = false;

let phoneModelReady = false;

let phoneModel = null;

let detectionRunning = false;

let lastFaceViolation = 0;

let lastPhoneViolation = 0;

let lastScreenshotTime = 0;

let faceRecognitionReady = false;


/* ==========================================================
   ELEMENTS
========================================================== */

const webcam =
    document.getElementById(
        "examWebcam"
    );

const webcamError =
    document.getElementById(
        "webcamError"
    );


/* ==========================================================
   START CAMERA + MICROPHONE
========================================================== */

async function startProctoring() {

    try {

        stream =
            await navigator.mediaDevices
                .getUserMedia({

                    video: {
                        width: {
                            ideal: 1280
                        },

                        height: {
                            ideal: 720
                        },

                        facingMode:
                            "user"
                    },

                    audio: true

                });


        webcam.srcObject =
            stream;


        webcamError.style.display =
            "none";


        updateStatus(
            "cameraStatus",
            "Camera: Active",
            true
        );


        startRecorders();


        monitorTracks();


        loadAIModels();


    }
    catch(error) {

        console.error(
            "Proctoring camera error:",
            error
        );


        webcamError.style.display =
            "flex";


        updateStatus(
            "cameraStatus",
            "Camera: Error",
            false
        );


        registerViolation(
            "CAMERA_DISCONNECTED",
            "Camera permission or camera access failed."
        );

    }

}


/* ==========================================================
   STATUS
========================================================== */

function updateStatus(
    id,
    text,
    good
) {

    const element =
        document.getElementById(id);


    if(!element) {

        return;

    }


    element.innerHTML =
        text;


    element.classList.toggle(
        "status-good",
        good
    );


    element.classList.toggle(
        "status-bad",
        !good
    );

}


/* ==========================================================
   RECORD VIDEO + AUDIO
========================================================== */

function startRecorders() {

    if(!stream) {

        return;

    }


    /* ---------------- VIDEO ---------------- */

    const videoTracks =
        stream.getVideoTracks();


    if(videoTracks.length) {

        const videoStream =
            new MediaStream(
                videoTracks
            );


        let options = {};


        if(
            MediaRecorder.isTypeSupported(
                "video/webm;codecs=vp9"
            )
        ) {

            options.mimeType =
                "video/webm;codecs=vp9";

        }
        else if(
            MediaRecorder.isTypeSupported(
                "video/webm"
            )
        ) {

            options.mimeType =
                "video/webm";

        }


        try {

            videoRecorder =
                new MediaRecorder(
                    videoStream,
                    options
                );


            videoRecorder.ondataavailable =
                function(event) {

                    if(
                        event.data &&
                        event.data.size > 0
                    ) {

                        videoChunks.push(
                            event.data
                        );

                    }

                };


            videoRecorder.onstop =
                function() {

                    uploadVideo();

                };


            videoRecorder.start(
                1000
            );

        }
        catch(error) {

            console.error(
                "Video recorder error:",
                error
            );

        }

    }


    /* ---------------- AUDIO ---------------- */

    const audioTracks =
        stream.getAudioTracks();


    if(audioTracks.length) {

        const audioStream =
            new MediaStream(
                audioTracks
            );


        let audioOptions = {};


        if(
            MediaRecorder.isTypeSupported(
                "audio/webm"
            )
        ) {

            audioOptions.mimeType =
                "audio/webm";

        }


        try {

            audioRecorder =
                new MediaRecorder(
                    audioStream,
                    audioOptions
                );


            audioRecorder.ondataavailable =
                function(event) {

                    if(
                        event.data &&
                        event.data.size > 0
                    ) {

                        audioChunks.push(
                            event.data
                        );

                    }

                };


            audioRecorder.onstop =
                function() {

                    uploadAudio();

                };


            audioRecorder.start(
                1000
            );

        }
        catch(error) {

            console.error(
                "Audio recorder error:",
                error
            );

        }

    }

}


/* ==========================================================
   UPLOAD VIDEO
========================================================== */

function uploadVideo() {

    if(!videoChunks.length) {

        return;

    }


    const blob =
        new Blob(
            videoChunks,
            {
                type:
                    "video/webm"
            }
        );


    const formData =
        new FormData();


    formData.append(
        "video",
        blob,
        "proctoring.webm"
    );


    fetch(
        config.videoUploadUrl,
        {

            method: "POST",

            body: formData

        }
    )
    .then(
        response =>
            response.json()
    )
    .then(
        data => {

            console.log(
                "Video uploaded:",
                data
            );

        }
    )
    .catch(
        error =>
            console.error(
                "Video upload error:",
                error
            )
    );

}


/* ==========================================================
   UPLOAD AUDIO
========================================================== */

function uploadAudio() {

    if(!audioChunks.length) {

        return;

    }


    const blob =
        new Blob(
            audioChunks,
            {
                type:
                    "audio/webm"
            }
        );


    const formData =
        new FormData();


    formData.append(
        "audio",
        blob,
        "proctoring.webm"
    );


    fetch(
        config.audioUploadUrl,
        {

            method: "POST",

            body: formData

        }
    )
    .then(
        response =>
            response.json()
    )
    .then(
        data => {

            console.log(
                "Audio uploaded:",
                data
            );

        }
    )
    .catch(
        error =>
            console.error(
                "Audio upload error:",
                error
            )
    );

}


/* ==========================================================
   CAMERA / MICROPHONE DISCONNECT
========================================================== */

function monitorTracks() {

    if(!stream) {

        return;

    }


    stream
        .getVideoTracks()
        .forEach(
            function(track) {

                track.addEventListener(
                    "ended",
                    function() {

                        updateStatus(
                            "cameraStatus",
                            "Camera: Disconnected",
                            false
                        );


                        registerViolation(
                            "CAMERA_DISCONNECTED",
                            "Your camera was disconnected."
                        );

                    }
                );

            }
        );


    stream
        .getAudioTracks()
        .forEach(
            function(track) {

                track.addEventListener(
                    "ended",
                    function() {

                        registerViolation(
                            "MICROPHONE_DISCONNECTED",
                            "Your microphone was disconnected."
                        );

                    }
                );

            }
        );

}


/* ==========================================================
   AI MODEL LOADING
========================================================== */

async function loadAIModels() {

    try {

        await faceapi.nets.tinyFaceDetector.loadFromUri(
            "https://justadudewhohacks.github.io/face-api.js/models"
        );


        await faceapi.nets.faceLandmark68Net.loadFromUri(
            "https://justadudewhohacks.github.io/face-api.js/models"
        );


        await faceapi.nets.faceRecognitionNet.loadFromUri(
            "https://justadudewhohacks.github.io/face-api.js/models"
        );


        faceModelReady = true;

        faceRecognitionReady = true;


        console.log(
            "Face AI models loaded."
        );

    }
    catch(error) {

        console.error(
            "Face model error:",
            error
        );

    }


    try {

        phoneModel =
            await cocoSsd.load();


        phoneModelReady = true;


        console.log(
            "Object detection model loaded."
        );

    }
    catch(error) {

        console.error(
            "Phone model error:",
            error
        );

    }


    startDetection();

}


/* ==========================================================
   START AI DETECTION
========================================================== */

function startDetection() {

    if(detectionRunning) {

        return;

    }


    detectionRunning = true;


    setInterval(
        detectFaces,
        2500
    );


    setInterval(
        detectObjects,
        4000
    );


    setInterval(
        captureScreenshot,
        30000
    );

}


/* ==========================================================
   FACE DETECTION
========================================================== */

async function detectFaces() {

    if(
        !faceModelReady ||
        !webcam ||
        webcam.readyState < 2 ||
        examSubmitted
    ) {

        return;

    }


    try {

        const detections =
            await faceapi
                .detectAllFaces(
                    webcam,
                    new faceapi.TinyFaceDetectorOptions({
                        inputSize: 320,
                        scoreThreshold: 0.5
                    })
                )
                .withFaceLandmarks();


        const count =
            detections.length;


        const faceCount =
            document.getElementById(
                "faceCount"
            );


        const personCount =
            document.getElementById(
                "personCount"
            );


        const faceStatus =
            document.getElementById(
                "faceStatus"
            );


        if(faceCount) {

            faceCount.innerText =
                count + " Face(s)";

        }


        if(personCount) {

            personCount.innerText =
                count;

        }


        /* ------------------------------------------
           NO FACE
        ------------------------------------------ */

        if(count === 0) {

            if(faceStatus) {

                faceStatus.innerHTML =
                    '<i class="fas fa-user-slash"></i> Face: Not Found';

            }


            registerFaceViolation(
                "NO_FACE",
                "No face was detected. Please keep your face visible."
            );

            return;

        }


        /* ------------------------------------------
           MULTIPLE FACES
        ------------------------------------------ */

        if(count > 1) {

            if(faceStatus) {

                faceStatus.innerHTML =
                    '<i class="fas fa-users"></i> Face: Multiple';

            }


            registerFaceViolation(
                "MULTIPLE_FACES",
                "Multiple faces were detected."
            );

            return;

        }


        /* ------------------------------------------
           ONE FACE
        ------------------------------------------ */

        if(faceStatus) {

            faceStatus.innerHTML =
                '<i class="fas fa-user-check"></i> Face: OK';

        }


        updateEyeStatus(
            detections[0]
        );

    }
    catch(error) {

        console.error(
            "Face detection error:",
            error
        );

    }

}


/* ==========================================================
   FACE VIOLATION COOLDOWN
========================================================== */

function registerFaceViolation(
    type,
    message
) {

    const now =
        Date.now();


    if(
        now - lastFaceViolation
        < 10000
    ) {

        return;

    }


    lastFaceViolation =
        now;


    registerViolation(
        type,
        message
    );

}


/* ==========================================================
   BASIC EYE / GAZE MONITORING
========================================================== */

function updateEyeStatus(
    detection
) {

    const eyeStatus =
        document.getElementById(
            "eyeStatus"
        );


    if(!eyeStatus) {

        return;

    }


    const landmarks =
        detection.landmarks;


    if(!landmarks) {

        eyeStatus.innerText =
            "Unavailable";

        return;

    }


    const leftEye =
        landmarks.getLeftEye();


    const rightEye =
        landmarks.getRightEye();


    const leftWidth =
        distance(
            leftEye[0],
            leftEye[3]
        );


    const rightWidth =
        distance(
            rightEye[0],
            rightEye[3]
        );


    if(
        leftWidth < 8 ||
        rightWidth < 8
    ) {

        eyeStatus.innerText =
            "Eyes Closed";

        eyeStatus.className =
            "status-warning";

    }
    else {

        eyeStatus.innerText =
            "Looking Forward";

        eyeStatus.className =
            "status-good";

    }

}


function distance(
    p1,
    p2
) {

    return Math.sqrt(
        Math.pow(
            p2.x - p1.x,
            2
        )
        +
        Math.pow(
            p2.y - p1.y,
            2
        )
    );

}


/* ==========================================================
   PHONE DETECTION
========================================================== */

async function detectObjects() {

    if(
        !phoneModelReady ||
        !phoneModel ||
        !webcam ||
        webcam.readyState < 2 ||
        examSubmitted
    ) {

        return;

    }


    try {

        const predictions =
            await phoneModel.detect(
                webcam
            );


        const phone =
            predictions.find(
                function(item) {

                    return (
                        item.class ===
                        "cell phone"
                        &&
                        item.score >=
                        0.45
                    );

                }
            );


        const phoneDetection =
            document.getElementById(
                "phoneDetection"
            );


        const phoneStatus =
            document.getElementById(
                "phoneStatus"
            );


        if(phone) {

            if(phoneDetection) {

                phoneDetection.innerText =
                    "Detected";

            }


            if(phoneStatus) {

                phoneStatus.innerHTML =
                    '<i class="fas fa-mobile-screen"></i> Phone: Detected';

            }


            const now =
                Date.now();


            if(
                now - lastPhoneViolation
                > 10000
            ) {

                lastPhoneViolation =
                    now;


                registerViolation(
                    "PHONE_DETECTED",
                    "A mobile phone was detected in the camera view."
                );

            }

        }
        else {

            if(phoneDetection) {

                phoneDetection.innerText =
                    "Clear";

            }


            if(phoneStatus) {

                phoneStatus.innerHTML =
                    '<i class="fas fa-mobile-screen"></i> Phone: Clear';

            }

        }

    }
    catch(error) {

        console.error(
            "Object detection error:",
            error
        );

    }

}


/* ==========================================================
   WARNING SYSTEM
========================================================== */

function registerViolation(
    type,
    message
) {

    if(examSubmitted) {

        return;

    }


    warningCount++;


    const warningElement =
        document.getElementById(
            "warningCount"
        );


    if(warningElement) {

        warningElement.innerText =
            warningCount;

    }


    sendProctoringEvent(
        type,
        message
    );


    showWarning(
        message
    );


    if(
        warningCount >=
        MAX_WARNINGS
    ) {

        setTimeout(
            function() {

                autoSubmit();

            },
            2000
        );

    }

}


/* ==========================================================
   SEND EVENT
========================================================== */

function sendProctoringEvent(
    type,
    message
) {

    fetch(
        config.eventUrl,
        {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/json"

            },

            body: JSON.stringify({

                event_type:
                    type,

                event_message:
                    message

            })

        }
    )
    .then(
        response =>
            response.json()
    )
    .then(
        data => {

            console.log(
                "Proctoring:",
                data
            );

        }
    )
    .catch(
        error => {

            console.error(
                "Proctoring event error:",
                error
            );

        }
    );

}


/* ==========================================================
   TAB SWITCH
========================================================== */

document.addEventListener(
    "visibilitychange",
    function() {

        if(
            document.hidden &&
            !examSubmitted
        ) {

            registerViolation(
                "TAB_SWITCH",
                "You switched away from the examination page."
            );

        }

    }
);


/* ==========================================================
   WINDOW BLUR
========================================================== */

window.addEventListener(
    "blur",
    function() {

        if(!examSubmitted) {

            registerViolation(
                "WINDOW_BLUR",
                "You moved away from the examination window."
            );

        }

    }
);


/* ==========================================================
   FULLSCREEN
========================================================== */

async function enterFullscreen() {

    try {

        if(
            !document.fullscreenElement
        ) {

            await document.documentElement
                .requestFullscreen();

        }

    }
    catch(error) {

        console.log(
            "Fullscreen request:",
            error
        );

    }

}


document.addEventListener(
    "fullscreenchange",
    function() {

        if(
            !document.fullscreenElement &&
            !examSubmitted
        ) {

            registerViolation(
                "FULLSCREEN_EXIT",
                "You exited fullscreen mode."
            );

        }

    }
);


/* ==========================================================
   WARNING MODAL
========================================================== */

function showWarning(
    message
) {

    const modal =
        document.getElementById(
            "warningModal"
        );


    const messageElement =
        document.getElementById(
            "warningMessage"
        );


    if(messageElement) {

        messageElement.innerText =
            message;

    }


    if(modal) {

        modal.style.display =
            "flex";

    }

}


window.closeWarning =
function() {

    const modal =
        document.getElementById(
            "warningModal"
        );


    if(modal) {

        modal.style.display =
            "none";

    }


    enterFullscreen();

};


/* ==========================================================
   SCREENSHOT
========================================================== */

async function captureScreenshot() {

    if(
        examSubmitted ||
        !webcam ||
        webcam.readyState < 2
    ) {

        return;

    }


    const now =
        Date.now();


    if(
        now - lastScreenshotTime
        < 20000
    ) {

        return;

    }


    lastScreenshotTime =
        now;


    try {

        const canvas =
            document.createElement(
                "canvas"
            );


        canvas.width =
            webcam.videoWidth;


        canvas.height =
            webcam.videoHeight;


        const context =
            canvas.getContext(
                "2d"
            );


        context.drawImage(
            webcam,
            0,
            0,
            canvas.width,
            canvas.height
        );


        canvas.toBlob(
            function(blob) {

                if(!blob) {

                    return;

                }


                const formData =
                    new FormData();


                formData.append(
                    "screenshot",
                    blob,
                    "screenshot.jpg"
                );


                fetch(
                    config.screenshotUploadUrl,
                    {

                        method: "POST",

                        body:
                            formData

                    }
                )
                .then(
                    response =>
                        response.json()
                )
                .then(
                    data =>
                        console.log(
                            "Screenshot:",
                            data
                        )
                )
                .catch(
                    error =>
                        console.error(
                            "Screenshot error:",
                            error
                        )
                );

            },
            "image/jpeg",
            0.75
        );

    }
    catch(error) {

        console.error(
            "Screenshot capture error:",
            error
        );

    }

}


/* ==========================================================
   STOP PROCTORING
========================================================== */

window.stopProctoring =
function() {

    examSubmitted =
        true;


    try {

        if(
            videoRecorder &&
            videoRecorder.state !==
            "inactive"
        ) {

            videoRecorder.stop();

        }

    }
    catch(error) {

        console.error(error);

    }


    try {

        if(
            audioRecorder &&
            audioRecorder.state !==
            "inactive"
        ) {

            audioRecorder.stop();

        }

    }
    catch(error) {

        console.error(error);

    }


    if(stream) {

        stream
            .getTracks()
            .forEach(
                function(track) {

                    track.stop();

                }
            );

    }

};


/* ==========================================================
   AUTO SUBMIT
========================================================== */

function autoSubmit() {

    if(examSubmitted) {

        return;

    }


    examSubmitted =
        true;


    sendProctoringEvent(
        "AUTO_SUBMITTED",
        "Exam automatically submitted because the maximum warning limit was reached."
    );


    if(
        videoRecorder &&
        videoRecorder.state !==
        "inactive"
    ) {

        videoRecorder.stop();

    }


    if(
        audioRecorder &&
        audioRecorder.state !==
        "inactive"
    ) {

        audioRecorder.stop();

    }


    setTimeout(
        function() {

            const form =
                document.getElementById(
                    "examForm"
                );


            if(form) {

                form.submit();

            }

        },
        500
    );

}


/* ==========================================================
   START
========================================================== */

window.addEventListener(
    "load",
    function() {
        startProctoring();

    }
);


})();