/**
 * JobShield AI - Frontend Interactivity
 * Handles Drag & Drop, Sample Injection, Checklist State & Feedback
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Sample Selector
    const sampleBtns = document.querySelectorAll(".btn-load-sample");
    const jobTextArea = document.getElementById("job_text");
    const titleInput = document.getElementById("job_title_input");
    const textTabBtn = document.getElementById("tab-text-btn");

    sampleBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            const sampleKey = this.getAttribute("data-sample-key");
            if (!sampleKey) return;

            // Switch to text tab if needed
            if (textTabBtn) {
                const tab = new bootstrap.Tab(textTabBtn);
                tab.show();
            }

            fetch(`/api/sample/${sampleKey}`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        if (jobTextArea) jobTextArea.value = data.text;
                        if (titleInput) titleInput.value = data.title.replace(/^[🔴🟡🟢]\s*/, "");
                        
                        // Scroll smoothly to input
                        jobTextArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        jobTextArea.classList.add("border-primary");
                        setTimeout(() => jobTextArea.classList.remove("border-primary"), 1200);
                    }
                })
                .catch(err => console.error("Error loading sample:", err));
        });
    });

    // 2. Drag and Drop File Upload
    const dropzone = document.getElementById("file-dropzone");
    const fileInput = document.getElementById("document_file");
    const fileNameDisplay = document.getElementById("selected-filename");

    if (dropzone && fileInput) {
        dropzone.addEventListener("click", () => fileInput.click());

        fileInput.addEventListener("change", function () {
            if (this.files && this.files[0]) {
                displaySelectedFile(this.files[0]);
            }
        });

        ["dragenter", "dragover"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add("drag-over");
            }, false);
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove("drag-over");
            }, false);
        });

        dropzone.addEventListener("drop", (e) => {
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                fileInput.files = e.dataTransfer.files;
                displaySelectedFile(e.dataTransfer.files[0]);
            }
        });
    }

    function displaySelectedFile(file) {
        if (!fileNameDisplay) return;
        const sizeKb = (file.size / 1024).toFixed(1);
        fileNameDisplay.innerHTML = `
            <div class="alert alert-success d-flex align-items-center justify-content-between p-2 mt-3 mb-0">
                <div>
                    <i class="bi bi-file-earmark-check-fill me-2 fs-5 text-success"></i>
                    <strong>${file.name}</strong> <span class="text-muted">(${sizeKb} KB)</span>
                </div>
                <span class="badge bg-success">Ready to Analyze</span>
            </div>
        `;
    }

    // 3. Interactive Checklist Persistence
    const checkItems = document.querySelectorAll(".checklist-checkbox");
    if (checkItems.length > 0) {
        const scanId = document.body.getAttribute("data-scan-id") || "default";
        const storageKey = `jobshield_checklist_${scanId}`;
        const savedState = JSON.parse(localStorage.getItem(storageKey) || "{}");

        checkItems.forEach(chk => {
            const itemId = chk.getAttribute("id");
            if (savedState[itemId]) {
                chk.checked = true;
                chk.closest(".checklist-item").classList.add("completed");
            }

            chk.addEventListener("change", function () {
                const parent = this.closest(".checklist-item");
                if (this.checked) {
                    parent.classList.add("completed");
                    savedState[itemId] = true;
                } else {
                    parent.classList.remove("completed");
                    delete savedState[itemId];
                }
                localStorage.setItem(storageKey, JSON.stringify(savedState));
                updateChecklistCounter();
            });
        });

        updateChecklistCounter();
    }

    function updateChecklistCounter() {
        const total = document.querySelectorAll(".checklist-checkbox").length;
        const done = document.querySelectorAll(".checklist-checkbox:checked").length;
        const counterEl = document.getElementById("checklist-completed-count");
        if (counterEl) {
            counterEl.textContent = `${done} of ${total} verified`;
        }
    }

    // 4. Feedback Submission
    const feedbackForm = document.getElementById("feedback-form");
    if (feedbackForm) {
        feedbackForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const scanId = document.getElementById("feedback-scan-id").value;
            const rating = document.querySelector('input[name="rating"]:checked')?.value || 5;
            const comments = document.getElementById("feedback-comments").value;
            const btn = document.getElementById("feedback-submit-btn");

            btn.disabled = true;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Submitting...`;

            fetch("/api/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ scan_id: scanId, rating: parseInt(rating), comments: comments })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById("feedback-container").innerHTML = `
                    <div class="alert alert-success d-flex align-items-center mb-0">
                        <i class="bi bi-check-circle-fill fs-4 me-2"></i>
                        <div><strong>Thank you!</strong> Your feedback helps improve JobShield AI for all students.</div>
                    </div>
                `;
            })
            .catch(err => {
                btn.disabled = false;
                btn.textContent = "Submit Feedback";
                alert("Failed to save feedback. Please try again.");
            });
        });
    }
});
