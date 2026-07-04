/* ==========================================================
   app.js
   Small front-end helper scripts (no framework, plain JS).
   ========================================================== */

document.addEventListener("DOMContentLoaded", function () {

    // --------------------------------------------------------
    // Auto-hide flash messages after 4 seconds
    // --------------------------------------------------------
    const alerts = document.querySelectorAll(".alert-auto-dismiss");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.classList.remove("show");
            alert.classList.add("fade");
            setTimeout(() => alert.remove(), 400);
        }, 4000);
    });

    // --------------------------------------------------------
    // Show selected PDF file name on the upload page
    // --------------------------------------------------------
    const fileInput = document.getElementById("resume_file");
    const fileNameLabel = document.getElementById("fileNameLabel");
    if (fileInput && fileNameLabel) {
        fileInput.addEventListener("change", function () {
            if (fileInput.files.length > 0) {
                fileNameLabel.textContent = fileInput.files[0].name;
            } else {
                fileNameLabel.textContent = "No file chosen";
            }
        });
    }

    // --------------------------------------------------------
    // Password confirmation live check (register / reset password)
    // --------------------------------------------------------
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirm_password");
    const matchWarning = document.getElementById("passwordMatchWarning");

    function checkPasswordsMatch() {
        if (!password || !confirmPassword || !matchWarning) return;
        if (confirmPassword.value.length === 0) {
            matchWarning.classList.add("d-none");
            return;
        }
        if (password.value !== confirmPassword.value) {
            matchWarning.classList.remove("d-none");
        } else {
            matchWarning.classList.add("d-none");
        }
    }

    if (password && confirmPassword) {
        password.addEventListener("input", checkPasswordsMatch);
        confirmPassword.addEventListener("input", checkPasswordsMatch);
    }

    // --------------------------------------------------------
    // OTP input: allow only digits, auto-focus friendly
    // --------------------------------------------------------
    const otpInput = document.getElementById("otp");
    if (otpInput) {
        otpInput.addEventListener("input", function () {
            otpInput.value = otpInput.value.replace(/[^0-9]/g, "").slice(0, 6);
        });
    }

    // --------------------------------------------------------
    // Animate circular ATS score ring (if present on page)
    // --------------------------------------------------------
    const ring = document.querySelector(".progress-ring");
    if (ring) {
        const score = parseInt(ring.getAttribute("data-score"), 10) || 0;
        const radius = ring.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;

        ring.style.strokeDasharray = `${circumference} ${circumference}`;
        ring.style.strokeDashoffset = circumference;

        setTimeout(function () {
            const offset = circumference - (score / 100) * circumference;
            ring.style.strokeDashoffset = offset;
        }, 200);
    }

    // --------------------------------------------------------
    // Edit Portfolio: dynamically add / remove project rows
    // --------------------------------------------------------
    const addProjectBtn = document.getElementById("addProjectBtn");
    const projectsContainer = document.getElementById("projectsContainer");

    if (addProjectBtn && projectsContainer) {
        addProjectBtn.addEventListener("click", function () {
            const row = document.createElement("div");
            row.classList.add("row", "g-2", "mb-2", "project-row");
            row.innerHTML = `
                <div class="col-md-4">
                    <input type="text" name="project_title" class="form-control" placeholder="Project title">
                </div>
                <div class="col-md-7">
                    <input type="text" name="project_description" class="form-control" placeholder="Short description">
                </div>
                <div class="col-md-1">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-project-btn">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            `;
            projectsContainer.appendChild(row);
        });

        projectsContainer.addEventListener("click", function (event) {
            if (event.target.closest(".remove-project-btn")) {
                event.target.closest(".project-row").remove();
            }
        });
    }
});
