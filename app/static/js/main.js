console.log("ProofForge aktif");

function copyHash(button) {
    const text = button.getAttribute("data-copy");

    if (!text) {
        return;
    }

    navigator.clipboard.writeText(text).then(() => {
        const oldText = button.innerText;
        button.innerText = "Copied";

        setTimeout(() => {
            button.innerText = oldText;
        }, 1200);
    }).catch(() => {
        alert("Gagal menyalin teks.");
    });
}