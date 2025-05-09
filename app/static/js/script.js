document.addEventListener('DOMContentLoaded', () => {
    // Add any JavaScript functionality here
    console.log('Crypto Wallet application loaded');
    
    // Copy to clipboard functionality for addresses
    const copyButtons = document.querySelectorAll('.copy-address');
    if (copyButtons) {
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const addressElement = this.previousElementSibling;
                const textArea = document.createElement('textarea');
                textArea.value = addressElement.textContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                // Show feedback
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 2000);
            });
        });
    }

    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = 'Processing...';
            }
        });
    });

    // Add click event listeners for any interactive elements
    document.querySelectorAll('.interactive-element').forEach(element => {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            // Add your click handling logic here
        });
    });
});