/* =========================================================
   SEASONAL CROP ADVISOR
   FINAL MERGED JAVASCRIPT
   Flask + ML Backend
   ========================================================= */

const API_URL = "/predict";

/* =========================================================
   DOM
   ========================================================= */

const $ = (id) => document.getElementById(id);

const form = $("predictForm");
const predictBtn = $("predictBtn");
const resultsSec = $("results");

const seasonInput = $("season");
const soilInput = $("soilType");


/* =========================================================
   SPLASH SCREEN
   Preserved from original inline JavaScript
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {

    const splashScreen = $("splashScreen");

    if (!splashScreen) {
        return;
    }

    /*
       Check whether user came back from
       Admin Login page.
    */

    const urlParams =
        new URLSearchParams(window.location.search);

    const skipSplash =
        urlParams.get("skip_splash") === "1";


    /* =========================================
       DIRECTLY OPEN CROP RECOMMENDATION
       ========================================= */

    if (skipSplash) {

        /*
           Hide splash immediately
        */

        splashScreen.classList.add("hide");

        document.body.classList.remove(
            "splash-active"
        );


        /*
           Remove splash from DOM
        */

        setTimeout(() => {

            if (splashScreen) {
                splashScreen.remove();
            }

        }, 100);


        /*
           Go directly to Crop Prediction
        */

        setTimeout(() => {

            const predictionSection =
                $("prediction");

            if (predictionSection) {

                predictionSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }

        }, 150);


        return;
    }


    /* =========================================
       NORMAL WEBSITE OPENING
       ========================================= */

    document.body.classList.add(
        "splash-active"
    );


    window.setTimeout(() => {

        splashScreen.classList.add("hide");

        document.body.classList.remove(
            "splash-active"
        );


        window.setTimeout(() => {

            if (splashScreen) {
                splashScreen.remove();
            }

        }, 750);

    }, 3600);

});



/* =========================================================
   FOOTER / CURRENT YEAR
   ========================================================= */

if ($("year")) {
    $("year").textContent = new Date().getFullYear();
}


/* =========================================================
   NAVIGATION DRAWER
   ========================================================= */

const hamburger = $("hamburger");
const drawer = $("navDrawer");

function toggleDrawer(force) {

    if (!drawer || !hamburger) return;

    const open =
        force !== undefined
            ? force
            : !drawer.classList.contains("open");

    drawer.classList.toggle("open", open);

    hamburger.setAttribute(
        "aria-expanded",
        String(open)
    );

    hamburger.setAttribute(
        "aria-label",
        open ? "Close menu" : "Open menu"
    );
}


if (hamburger && drawer) {

    hamburger.addEventListener(
        "click",
        () => toggleDrawer()
    );

    /*
       Close drawer when any navigation link
       is clicked.
    */

    drawer.querySelectorAll("a").forEach((link) => {

        link.addEventListener(
            "click",
            () => toggleDrawer(false)
        );

    });

    /*
       ESC key closes drawer
    */

    document.addEventListener(
        "keydown",
        (event) => {

            if (event.key === "Escape") {
                toggleDrawer(false);
            }

        }
    );
}


/* =========================================================
   CUSTOM DROPDOWN
   ========================================================= */

function setupDropdown(
    dropdownId,
    toggleId,
    valueId,
    listId,
    hiddenInput,
    errorId,
    attribute
) {

    const dropdown = $(dropdownId);
    const toggle = $(toggleId);
    const valueEl = $(valueId);
    const list = $(listId);
    const hidden = $(hiddenInput);

    if (
        !dropdown ||
        !toggle ||
        !valueEl ||
        !list ||
        !hidden
    ) {
        return;
    }


    /* -----------------------------------------
       CLOSE DROPDOWN
       ----------------------------------------- */

    function close() {

        dropdown.classList.remove("open");

        toggle.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    /* -----------------------------------------
       OPEN / CLOSE DROPDOWN
       ----------------------------------------- */

    toggle.addEventListener(
        "click",
        (event) => {

            event.stopPropagation();

            const currentlyOpen =
                dropdown.classList.contains("open");


            /*
               Close all other dropdowns
            */

            document
                .querySelectorAll(".dropdown.open")
                .forEach((item) => {

                    item.classList.remove("open");

                });


            /*
               Open selected dropdown
            */

            if (!currentlyOpen) {

                dropdown.classList.add("open");

                toggle.setAttribute(
                    "aria-expanded",
                    "true"
                );


                if (
                    errorId &&
                    $(errorId)
                ) {

                    $(errorId).classList.remove(
                        "show"
                    );
                }
            }

        }
    );


    /* -----------------------------------------
       SELECT DROPDOWN ITEM
       ----------------------------------------- */

    list
        .querySelectorAll("li")
        .forEach((li) => {

            li.addEventListener(
                "click",
                () => {

                    /*
                       Remove previous selection
                    */

                    list
                        .querySelectorAll("li")
                        .forEach((item) => {

                            item.classList.remove(
                                "selected"
                            );

                        });


                    /*
                       Select current item
                    */

                    li.classList.add("selected");


                    /*
                       Display selected text
                    */

                    valueEl.textContent =
                        li.textContent.trim();


                    /*
                       Store actual value
                    */

                    hidden.value =
                        li.dataset[attribute];


                    /*
                       Mark dropdown as having value
                    */

                    dropdown.classList.add(
                        "has-value"
                    );


                    /*
                       Close dropdown
                    */

                    close();

                }
            );

        });


    /* -----------------------------------------
       CLOSE WHEN CLICKING OUTSIDE
       ----------------------------------------- */

    document.addEventListener(
        "click",
        (event) => {

            if (
                !event.target.closest(
                    "#" + dropdownId
                )
            ) {

                close();

            }

        }
    );


    return {
        close
    };
}


/* =========================================================
   SOIL DROPDOWN
   ========================================================= */

setupDropdown(
    "soilDropdown",
    "soilToggle",
    "soilValue",
    "soilList",
    "soilType",
    "soilError",
    "soil"
);


/* =========================================================
   SEASON DROPDOWN
   ========================================================= */

setupDropdown(
    "seasonDropdown",
    "seasonToggle",
    "seasonValue",
    "seasonList",
    "season",
    "seasonError",
    "season"
);


/* =========================================================
   pH SLIDER
   ========================================================= */

const phInput = $("soil_ph");
const phRange = $("phRange");
const phGroup = $("phGroup");


if (
    phInput &&
    phRange &&
    phGroup
) {

    /* -----------------------------------------
       pH INPUT FOCUS
       ----------------------------------------- */

    phInput.addEventListener(
        "focus",
        () => {

            phGroup.classList.add(
                "slider-open"
            );

        }
    );


    /* -----------------------------------------
       MANUAL pH INPUT
       ----------------------------------------- */

    phInput.addEventListener(
        "input",
        () => {

            const value =
                parseFloat(
                    phInput.value
                );


            if (
                !isNaN(value) &&
                value >= 0 &&
                value <= 14
            ) {

                phRange.value = value;

            }


            if ($("phError")) {

                $("phError").classList.remove(
                    "show"
                );

            }

        }
    );


    /* -----------------------------------------
       pH RANGE SLIDER
       ----------------------------------------- */

    phRange.addEventListener(
        "input",
        () => {

            phInput.value =
                phRange.value;


            if ($("phError")) {

                $("phError").classList.remove(
                    "show"
                );

            }

        }
    );

}


/* =========================================================
   VALIDATION
   ========================================================= */

function setError(
    groupId,
    errorId,
    show
) {

    if (
        groupId &&
        $(groupId)
    ) {

        $(groupId).classList.toggle(
            "invalid",
            show
        );

    }


    if (
        errorId &&
        $(errorId)
    ) {

        $(errorId).classList.toggle(
            "show",
            show
        );

    }

    return !show;
}


/* =========================================================
   FORM VALIDATION
   ========================================================= */

function validateForm(data) {

    let valid = true;


    /* Soil */

    valid =
        setError(
            null,
            "soilError",
            data.soil_type === ""
        ) && valid;


    /* pH */

    valid =
        setError(
            null,
            "phError",
            isNaN(data.soil_ph) ||
            data.soil_ph < 0 ||
            data.soil_ph > 14
        ) && valid;


    /* NPK */

    valid =
        setError(
            null,
            "npkError",
            isNaN(data.N) ||
            isNaN(data.P) ||
            isNaN(data.K) ||
            data.N < 0 ||
            data.P < 0 ||
            data.K < 0
        ) && valid;


    /* Season */

    valid =
        setError(
            null,
            "seasonError",
            data.season === ""
        ) && valid;


    return valid;
}


/* =========================================================
   COLLECT FORM DATA
   ========================================================= */

function collectFormData() {

    return {

        N: parseFloat(
            $("nitrogen").value
        ),

        P: parseFloat(
            $("phosphorus").value
        ),

        K: parseFloat(
            $("potassium").value
        ),

        soil_ph: parseFloat(
            $("soil_ph").value
        ),

        season:
            seasonInput
                ? seasonInput.value
                : "",

        soil_type:
            soilInput
                ? soilInput.value
                : ""

    };
}


/* =========================================================
   RESPONSE PARSER
   ========================================================= */

function parseRecommendations(data) {

    if (data.success === false) {

        throw new Error(
            data.error ||
            "Prediction failed"
        );

    }


    /*
       Backend returns recommendations array
    */

    if (
        Array.isArray(
            data.recommendations
        )
    ) {

        return data.recommendations;

    }


    /*
       Backend returns single crop
    */

    if (data.crop) {

        return [

            {

                crop: data.crop,

                percentage:
                    Number(
                        data.confidence ??
                        data.suitability ??
                        100
                    )

            }

        ];

    }


    throw new Error(
        "No crop recommendation received from backend."
    );
}


/* =========================================================
   DISPLAY RESULTS
   ========================================================= */

function displayResults(
    recommendations
) {

    if (
        !recommendations ||
        recommendations.length === 0
    ) {

        throw new Error(
            "No crop recommendations available."
        );

    }


    /* -----------------------------------------
       TOP CROP
       ----------------------------------------- */

    const first =
        recommendations[0];

    const topCrop =
        $("topCrop");

    const topPct =
        $("topPct");

    const topBar =
        $("topBar");


    if (topCrop) {

        topCrop.textContent =
            first.crop ||
            "Unknown";

    }


    const pctVal =
        Number(
            first.percentage ??
            first.suitability ??
            0
        );


    if (topPct) {

        topPct.textContent =
            pctVal + "%";

    }


    /* -----------------------------------------
       SECOND CROP
       ----------------------------------------- */

    const second =
        recommendations[1];


    if ($("crop2")) {

        $("crop2").textContent =
            second
                ? second.crop
                : "N/A";

    }


    if ($("pct2")) {

        $("pct2").textContent =
            second
                ? (
                    Number(
                        second.percentage ??
                        second.suitability ??
                        0
                    )
                    + "%"
                )
                : "0%";

    }


    /* -----------------------------------------
       THIRD CROP
       ----------------------------------------- */

    const third =
        recommendations[2];


    if ($("crop3")) {

        $("crop3").textContent =
            third
                ? third.crop
                : "N/A";

    }


    if ($("pct3")) {

        $("pct3").textContent =
            third
                ? (
                    Number(
                        third.percentage ??
                        third.suitability ??
                        0
                    )
                    + "%"
                )
                : "0%";

    }


    /* -----------------------------------------
       SHOW RESULTS
       ----------------------------------------- */

    if (resultsSec) {

        resultsSec.classList.add(
            "show"
        );

        resultsSec.scrollIntoView({
            behavior: "smooth"
        });

    }


    /* -----------------------------------------
       TOP PROGRESS BAR
       ----------------------------------------- */

    setTimeout(
        () => {

            if (topBar) {

                topBar.style.width =
                    Math.max(
                        0,
                        Math.min(
                            100,
                            pctVal
                        )
                    ) + "%";

            }

        },
        100
    );
}


/* =========================================================
   PREDICTION SUBMISSION
   ========================================================= */

if (form) {

    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            /* -------------------------------------
               COLLECT DATA
               ------------------------------------- */

            const data =
                collectFormData();


            /* -------------------------------------
               VALIDATE
               ------------------------------------- */

            if (
                !validateForm(data)
            ) {

                return;

            }


            /* -------------------------------------
               BUTTON LOADING
               ------------------------------------- */

            if (predictBtn) {

                predictBtn.classList.add(
                    "loading"
                );

                predictBtn.textContent =
                    "Predicting...";

            }


            try {

                /* ---------------------------------
                   SEND DATA TO FLASK
                   --------------------------------- */

                const response =
                    await fetch(
                        API_URL,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    data
                                )
                        }
                    );


                /* ---------------------------------
                   READ RESPONSE
                   --------------------------------- */

                const resData =
                    await response.json();


                /* ---------------------------------
                   SERVER ERROR
                   --------------------------------- */

                if (
                    !response.ok ||
                    resData.success === false
                ) {

                    throw new Error(
                        resData.error ||
                        `Server responded with status ${response.status}`
                    );

                }


                /* ---------------------------------
                   PARSE RECOMMENDATIONS
                   --------------------------------- */

                const recommendations =
                    parseRecommendations(
                        resData
                    );


                /* ---------------------------------
                   DISPLAY
                   --------------------------------- */

                displayResults(
                    recommendations
                );

            }


            catch (error) {

                console.error(
                    "Prediction failed:",
                    error
                );

                alert(
                    "Prediction Error: " +
                    error.message
                );

            }


            finally {

                if (predictBtn) {

                    predictBtn.classList.remove(
                        "loading"
                    );

                    predictBtn.textContent =
                        "Predict Crop";

                }

            }

        }
    );

}


/* =========================================================
   PREDICT AGAIN
   Preserved from original inline JavaScript
   ========================================================= */

const predictAgain =
    $("predictAgain");

if (predictAgain) {

    predictAgain.addEventListener(
        "click",
        () => {

            if (resultsSec) {

                resultsSec.classList.remove(
                    "show"
                );

            }


            const predictionSection =
                $("prediction");

            if (predictionSection) {

                predictionSection.scrollIntoView({
                    behavior: "smooth"
                });

            }

        }
    );

}


/* =========================================================
   FINAL YEAR UPDATE
   ========================================================= */

if ($("year")) {

    $("year").textContent =
        new Date().getFullYear();

}


/* =========================================================
   END OF FINAL MERGED SCRIPT
   ========================================================= */