document.addEventListener('DOMContentLoaded', function() {
    // Input validation for DNA sequence
    const sequenceInput = document.getElementById('sequence');
    if (sequenceInput) {
        sequenceInput.addEventListener('input', function() {
            // Replace any characters that are not A, T, C, or G
            this.value = this.value.toUpperCase().replace(/[^ATCG]/g, '');
            
            // Update character counter
            const counter = this.parentNode.querySelector('.char-counter');
            if (counter) {
                counter.textContent = `${this.value.length} bases`;
            }
            
            // Update validation indicator
            const validationIndicator = document.querySelector('.validation-indicator');
            const indicatorDot = document.querySelector('.indicator-dot');
            const validationText = document.querySelector('.validation-text');
            
            if (validationIndicator && indicatorDot && validationText) {
                if (this.value.length > 0) {
                    indicatorDot.style.background = 'var(--success-color)';
                    validationText.textContent = 'Valid DNA sequence';
                } else {
                    indicatorDot.style.background = 'var(--warning-color)';
                    validationText.textContent = 'Enter a DNA sequence';
                }
            }
        });
    }

    // Update character counter for message input
    const messageInput = document.getElementById('message');
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            const counter = this.parentNode.querySelector('.char-counter');
            if (counter) {
                counter.textContent = `${this.value.length} characters`;
            }
        });
        
        // Initialize counter
        const counter = messageInput.parentNode.querySelector('.char-counter');
        if (counter) {
            counter.textContent = `${messageInput.value.length} characters`;
        }
    }

    // Initialize counter for sequence input if it has a value
    if (sequenceInput && sequenceInput.value) {
        const counter = sequenceInput.parentNode.querySelector('.char-counter');
        if (counter) {
            counter.textContent = `${sequenceInput.value.length} bases`;
        }
        
        // Update validation indicator
        const indicatorDot = document.querySelector('.indicator-dot');
        const validationText = document.querySelector('.validation-text');
        
        if (indicatorDot && validationText) {
            indicatorDot.style.background = 'var(--success-color)';
            validationText.textContent = 'Valid DNA sequence';
        }
    }

    // Copy button functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                // Create a temporary textarea element to copy the text
                const textarea = document.createElement('textarea');
                textarea.value = targetElement.textContent;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                
                // Change button text temporarily to indicate success
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                this.style.background = 'var(--success-color)';
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.background = '';
                }, 2000);
            }
        });
    });

    // Add futuristic typing effect to the header
    const headerText = document.querySelector('h1');
    if (headerText) {
        const text = headerText.innerHTML;
        headerText.innerHTML = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                headerText.innerHTML += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        // Uncomment to enable typing effect
        // typeWriter();
    }

    // Add visual feedback on form submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const button = this.querySelector('button[type="submit"]');
            if (button) {
                button.textContent = 'Processing...';
                button.disabled = true;
                
                // The form will be submitted and page will reload,
                // so no need to reset the button state
            }
        });
    });

    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(message => {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease';
                
                setTimeout(() => {
                    message.style.display = 'none';
                }, 500);
            });
        }, 5000);
    }

    // Add futuristic typing effect to the header on login page
    const loginHeader = document.querySelector('.login-header h1');
    if (loginHeader) {
        const text = loginHeader.innerHTML;
        loginHeader.innerHTML = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                loginHeader.innerHTML += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        // Enable typing effect for login page
        typeWriter();
    }

    // Form options functionality
    const includeSpacesCheckbox = document.querySelector('input[name="include_spaces"]');
    const uppercaseCheckbox = document.querySelector('input[name="uppercase"]');
    const messageTextarea = document.getElementById('message');
    
    if (includeSpacesCheckbox && messageTextarea) {
        includeSpacesCheckbox.addEventListener('change', function() {
            if (!this.checked && messageTextarea.value) {
                // Remove spaces from the message
                messageTextarea.value = messageTextarea.value.replace(/\s/g, '');
                
                // Update character counter
                const counter = messageTextarea.parentNode.querySelector('.char-counter');
                if (counter) {
                    counter.textContent = `${messageTextarea.value.length} characters`;
                }
            }
        });
    }
    
    if (uppercaseCheckbox && messageTextarea) {
        uppercaseCheckbox.addEventListener('change', function() {
            if (this.checked && messageTextarea.value) {
                // Convert message to uppercase
                messageTextarea.value = messageTextarea.value.toUpperCase();
            }
        });
    }

    // Mode toggle functionality for all modes
    window.toggleModeOptions = function() {
        const modeSelect = document.getElementById('mode');
        const nanoporeOptions = document.querySelector('.nanopore-options');
        const secureOptions = document.querySelector('.secure-options');
        const passwordInput = document.getElementById('password');
        
        if (modeSelect) {
            const selectedMode = modeSelect.value;
            
            // Hide all option groups first
            if (nanoporeOptions) nanoporeOptions.style.display = 'none';
            if (secureOptions) secureOptions.style.display = 'none';
            
            // Show appropriate option group
            if (selectedMode === 'nanopore' && nanoporeOptions) {
                nanoporeOptions.style.display = 'block';
            } else if (selectedMode === 'secure' && secureOptions) {
                secureOptions.style.display = 'block';
                // Set password as required for secure mode
                if (passwordInput) {
                    passwordInput.required = true;
                }
            } else if (passwordInput) {
                // Remove password requirement for non-secure modes
                passwordInput.required = false;
            }
        }
    };
    
    // Legacy function for backward compatibility
    window.toggleNanoporeOptions = window.toggleModeOptions;

    // Initialize mode options display on page load
    const modeSelect = document.getElementById('mode');
    if (modeSelect) {
        toggleModeOptions();
    }

    // Add particle effect to the background (optional - uncomment to enable)
    /*
    function createParticle() {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random position
        const x = Math.random() * window.innerWidth;
        const y = Math.random() * window.innerHeight;
        
        // Random size
        const size = Math.random() * 5 + 1;
        
        // Apply styles
        particle.style.left = `${x}px`;
        particle.style.top = `${y}px`;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        document.body.appendChild(particle);
        
        // Remove after animation
        setTimeout(() => {
            particle.remove();
        }, 5000);
    }
    
    // Create particles at intervals
    setInterval(createParticle, 200);
    */
}); 