document.addEventListener("DOMContentLoaded", () => {
    console.log("Library Chatbot system loaded successfully!");

    // Auto-scroll chat history to the bottom
    const chatHistory = document.querySelector(".chat-history");
    if (chatHistory) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Add confirmation before clearing chat
    const clearForm = document.querySelector('form[action="/clear"]');
    if (clearForm) {
        clearForm.addEventListener("submit", (event) => {
            const confirmClear = confirm("Are you sure you want to clear the chat history?");
            if (!confirmClear) {
                event.preventDefault();
            }
        });
    }

    // Highlight role cards on click
    const roleCards = document.querySelectorAll(".role-card");
    roleCards.forEach(card => {
        card.addEventListener("click", () => {
            card.style.boxShadow = "0 0 15px #27ae60";
            setTimeout(() => {
                card.style.boxShadow = "";
            }, 800);
        });
    });

    // Simple form validation (extra safety)
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", () => {
            const inputs = form.querySelectorAll("input[required], select[required]");
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    alert("Please fill out all required fields.");
                }
            });
        });
    });
});

