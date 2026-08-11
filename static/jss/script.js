// =========================================================
// MEDSTOCK JAVASCRIPT
// =========================================================


// =========================================================
// PAGE LOADED
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("MedStock loaded successfully.");

    hideFlashMessages();

    setMinimumExpiryDate();

});


// =========================================================
// TRANSFER CONFIRMATION
// =========================================================

function confirmTransfer(quantity, medicineName) {

    const message =
        "Are you sure you want to complete this transfer?\n\n" +
        "Medicine: " + medicineName + "\n" +
        "Quantity: " + quantity + " unit(s)\n\n" +
        "The inventory of both hospitals will be updated.";

    return window.confirm(message);
}


// =========================================================
// FLASH MESSAGE AUTO HIDE
// =========================================================

function hideFlashMessages() {

    const messages =
        document.querySelectorAll(".flash");

    messages.forEach(function (message) {

        setTimeout(function () {

            message.style.transition =
                "opacity 0.5s ease";

            message.style.opacity = "0";

            setTimeout(function () {

                message.remove();

            }, 500);

        }, 4000);

    });

}


// =========================================================
// EXPIRY DATE
// =========================================================

function setMinimumExpiryDate() {

    const expiryInputs =
        document.querySelectorAll(
            'input[name="expiry_date"]'
        );

    const today = new Date();

    const year =
        today.getFullYear();

    const month =
        String(today.getMonth() + 1)
        .padStart(2, "0");

    const day =
        String(today.getDate())
        .padStart(2, "0");

    const todayString =
        year + "-" + month + "-" + day;


    expiryInputs.forEach(function (input) {

        input.min = todayString;

    });

}