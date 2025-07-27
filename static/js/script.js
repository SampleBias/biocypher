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

    // Safety Screening functionality
    const safetyScreenBtn = document.getElementById('safety-screen-btn');
    if (safetyScreenBtn) {
        safetyScreenBtn.addEventListener('click', function() {
            const sequence = this.getAttribute('data-sequence');
            if (sequence) {
                performSafetyScreening(sequence);
            }
        });
    }

    // CSRF token for safety screening API calls
    function getCSRFToken() {
        const csrfInput = document.querySelector('input[name="csrf_token"]');
        return csrfInput ? csrfInput.value : '';
    }

    // Perform safety screening
    function performSafetyScreening(sequence) {
        const button = document.getElementById('safety-screen-btn');
        const resultsContainer = document.getElementById('safety-results');
        const statusContainer = document.getElementById('safety-status');
        const detailsContainer = document.getElementById('safety-details');

        // Show loading state
        button.classList.add('loading');
        button.disabled = true;
        button.textContent = 'Analyzing...';

        // Make API call
        fetch('/api/safety_screen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                sequence: sequence
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading state
            button.classList.remove('loading');
            button.disabled = false;
            button.textContent = '🛡️ Safety Screen';

            if (data.success) {
                // Display results
                displaySafetyResults(data.report, statusContainer, detailsContainer);
                resultsContainer.style.display = 'block';
                
                // Smooth scroll to results
                resultsContainer.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'nearest' 
                });
            } else {
                // Show error
                showSafetyError(data.error || 'Safety screening failed', statusContainer);
                resultsContainer.style.display = 'block';
            }
        })
        .catch(error => {
            // Remove loading state
            button.classList.remove('loading');
            button.disabled = false;
            button.textContent = '🛡️ Safety Screen';

            // Show error
            showSafetyError('Network error occurred during safety screening', statusContainer);
            resultsContainer.style.display = 'block';
            console.error('Safety screening error:', error);
        });
    }

    // Display safety screening results
    function displaySafetyResults(report, statusContainer, detailsContainer) {
        // Set status
        statusContainer.innerHTML = `
            <div class="safety-status ${report.safety_color}">
                ${report.safety_icon} ${report.safety_status}
            </div>
        `;
        statusContainer.className = `safety-status ${report.safety_color}`;

        // Build detailed results
        let detailsHTML = '';

        // Sequence characteristics
        detailsHTML += `
            <div class="safety-section">
                <h5>📊 Sequence Analysis</h5>
                <div class="safety-grid">
                    <div class="safety-item">
                        <span class="label">Length:</span>
                        <span class="value">${report.sequence_length} bases</span>
                    </div>
                    <div class="safety-item">
                        <span class="label">GC Content:</span>
                        <span class="value">${report.sequence_characteristics.gc_content}%</span>
                    </div>
                    <div class="safety-item">
                        <span class="label">ORFs Found:</span>
                        <span class="value">${report.sequence_characteristics.orfs.length}</span>
                    </div>
                    <div class="safety-item">
                        <span class="label">Homopolymer Runs:</span>
                        <span class="value">${report.sequence_characteristics.homopolymer_runs.length}</span>
                    </div>
                </div>
            </div>
        `;

        // Pathogen analysis
        detailsHTML += `
            <div class="safety-section">
                <h5>🦠 Pathogen Risk Analysis</h5>
                <div class="safety-item">
                    <span class="label">Risk Level:</span>
                    <span class="value risk-${report.pathogen_analysis.risk_level}">${report.pathogen_analysis.risk_level.toUpperCase()}</span>
                </div>
                ${report.pathogen_analysis.matches.length > 0 ? `
                    <div class="match-list">
                        <strong>⚠️ Pathogen Signatures Detected:</strong>
                        ${report.pathogen_analysis.matches.map(match => 
                            `<div class="match-item">
                                <strong>${match.category}:</strong> ${match.signature} (pos: ${match.position})
                            </div>`
                        ).join('')}
                    </div>
                ` : '<p style="color: var(--success-color);">✅ No pathogen signatures detected</p>'}
            </div>
        `;

        // Natural occurrence
        detailsHTML += `
            <div class="safety-section">
                <h5>🧬 Natural Occurrence Check</h5>
                ${report.natural_occurrence.natural_occurrence ? `
                    <div class="safety-item">
                        <span class="label">Found in:</span>
                        <span class="value">${report.natural_occurrence.organisms.join(', ')}</span>
                    </div>
                    <div class="match-list">
                        <strong>🧬 Natural Sequence Matches:</strong>
                        ${report.natural_occurrence.matches.map(match => 
                            `<div class="match-item">
                                <strong>${match.type}:</strong> ${match.organism || match.gene} - ${match.signature} (pos: ${match.position})
                            </div>`
                        ).join('')}
                    </div>
                ` : '<p style="color: var(--success-color);">✅ No natural sequence matches found</p>'}
            </div>
        `;

        // Warnings
        if (report.sequence_characteristics.warnings.length > 0) {
            detailsHTML += `
                <div class="safety-section">
                    <h5>⚠️ Warnings</h5>
                    <ul>
                        ${report.sequence_characteristics.warnings.map(warning => 
                            `<li style="color: var(--warning-color);">${warning}</li>`
                        ).join('')}
                    </ul>
                </div>
            `;
        }

        // Recommendations
        detailsHTML += `
            <div class="recommendations">
                <h5>💡 Recommendations</h5>
                <ul>
                    ${report.recommendations.map(rec => 
                        `<li>${rec}</li>`
                    ).join('')}
                </ul>
                <p style="margin-top: 1rem; font-size: 0.9rem; color: var(--light-color); opacity: 0.8;">
                    <em>Screening completed: ${report.timestamp}</em>
                </p>
            </div>
        `;

        detailsContainer.innerHTML = detailsHTML;
    }

    // Show safety screening error
    function showSafetyError(errorMessage, statusContainer) {
        statusContainer.innerHTML = `
            <div class="safety-status unsafe">
                ❌ ERROR: ${errorMessage}
            </div>
        `;
        statusContainer.className = 'safety-status unsafe';
        
        const detailsContainer = document.getElementById('safety-details');
        detailsContainer.innerHTML = `
            <div class="safety-section">
                <h5>⚠️ Error Details</h5>
                <p style="color: var(--error-color);">${errorMessage}</p>
                <p style="margin-top: 1rem;">Please try again or contact support if the problem persists.</p>
            </div>
        `;
    }
}); 