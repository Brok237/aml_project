/**
 * ML PREDICTION DASHBOARD - JAVASCRIPT
 * Handles interactive features, charts, and user interactions
 */

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format a number as a percentage with specified decimal places
 * @param {number} value - The value to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted percentage string
 */
function formatPercentage(value, decimals = 2) {
    return (value * 100).toFixed(decimals) + '%';
}

/**
 * Format a number with thousand separators
 * @param {number} num - The number to format
 * @returns {string} Formatted number string
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - Type of toast: 'success', 'error', 'info' (default: 'info')
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="bi bi-${getToastIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after duration
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Get the appropriate icon for toast type
 * @param {string} type - Toast type
 * @returns {string} Icon name
 */
function getToastIcon(type) {
    const icons = {
        'success': 'check-circle-fill',
        'error': 'exclamation-triangle-fill',
        'info': 'info-circle-fill'
    };
    return icons[type] || icons['info'];
}

/**
 * Validate file size
 * @param {File} file - The file to validate
 * @param {number} maxSizeMB - Maximum file size in MB (default: 16)
 * @returns {boolean} True if file is valid
 */
function validateFileSize(file, maxSizeMB = 16) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
}

/**
 * Validate file type
 * @param {File} file - The file to validate
 * @returns {boolean} True if file type is allowed
 */
function validateFileType(file) {
    const allowedExtensions = ['xlsx', 'xls', 'csv'];
    const extension = file.name.split('.').pop().toLowerCase();
    return allowedExtensions.includes(extension);
}

// ============================================================================
// CHART UTILITIES
// ============================================================================

/**
 * Create a color palette for charts
 * @returns {object} Color palette
 */
function getChartColors() {
    return {
        primary: '#3b82f6',
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        info: '#0ea5e9',
        secondary: '#6b7280',
        light: '#f3f4f6'
    };
}

/**
 * Get chart default options
 * @returns {object} Default chart options
 */
function getChartDefaultOptions() {
    return {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 14,
                        weight: '500'
                    },
                    padding: 20,
                    usePointStyle: true
                }
            }
        }
    };
}

// ============================================================================
// DATA FORMATTING
// ============================================================================

/**
 * Format prediction data for display
 * @param {number} prediction - Prediction value (0 or 1)
 * @returns {object} Formatted prediction object
 */
function formatPrediction(prediction) {
    return {
        label: prediction === 1 ? 'Fraud' : 'Legitimate',
        class: prediction === 1 ? 'fraud' : 'legit',
        color: prediction === 1 ? '#ef4444' : '#10b981'
    };
}

/**
 * Format probability for display
 * @param {number} probability - Probability value (0-1)
 * @returns {string} Formatted probability string
 */
function formatProbability(probability) {
    return (probability * 100).toFixed(2) + '%';
}

/**
 * Calculate confidence level from probabilities
 * @param {array} probabilities - Array of probabilities [legit_prob, fraud_prob]
 * @returns {number} Confidence value (0-1)
 */
function calculateConfidence(probabilities) {
    return Math.max(...probabilities);
}

// ============================================================================
// TABLE UTILITIES
// ============================================================================

/**
 * Create a table row from prediction data
 * @param {number} rowIndex - Row index
 * @param {number} prediction - Prediction value
 * @param {array} probabilities - Probability values
 * @returns {HTMLTableRowElement} Table row element
 */
function createTableRow(rowIndex, prediction, probabilities) {
    const row = document.createElement('tr');
    
    const fraudProb = probabilities[1];
    const legitProb = probabilities[0];
    const confidence = calculateConfidence(probabilities);
    const predictionData = formatPrediction(prediction);
    
    row.innerHTML = `
        <td>${rowIndex}</td>
        <td><span class="badge badge-${predictionData.class}">${predictionData.label}</span></td>
        <td>${fraudProb.toFixed(4)}</td>
        <td>${legitProb.toFixed(4)}</td>
        <td>
            <span class="confidence-bar" style="width: ${confidence * 100}%"></span>
            ${(confidence * 100).toFixed(1)}%
        </td>
    `;
    
    return row;
}

// ============================================================================
// PAGINATION UTILITIES
// ============================================================================

/**
 * Calculate total pages
 * @param {number} totalItems - Total number of items
 * @param {number} itemsPerPage - Items per page
 * @returns {number} Total pages
 */
function calculateTotalPages(totalItems, itemsPerPage) {
    return Math.ceil(totalItems / itemsPerPage);
}

/**
 * Get paginated data
 * @param {array} data - Full data array
 * @param {number} page - Current page (1-indexed)
 * @param {number} itemsPerPage - Items per page
 * @returns {array} Paginated data
 */
function getPaginatedData(data, page, itemsPerPage) {
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return data.slice(startIndex, endIndex);
}

// ============================================================================
// EXPORT UTILITIES
// ============================================================================

/**
 * Export data to CSV format
 * @param {array} data - Array of objects to export
 * @param {string} filename - Output filename
 */
function exportToCSV(data, filename = 'export.csv') {
    if (!data || data.length === 0) {
        showToast('No data to export', 'error');
        return;
    }

    // Get headers from first object
    const headers = Object.keys(data[0]);
    
    // Create CSV content
    let csvContent = headers.join(',') + '\n';
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            // Escape quotes and wrap in quotes if contains comma
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        });
        csvContent += values.join(',') + '\n';
    });

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showToast('Data exported successfully', 'success');
}

// ============================================================================
// ANIMATION UTILITIES
// ============================================================================

/**
 * Animate a number from start to end value
 * @param {HTMLElement} element - Target element
 * @param {number} start - Start value
 * @param {number} end - End value
 * @param {number} duration - Animation duration in milliseconds
 */
function animateNumber(element, start, end, duration = 1000) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

// ============================================================================
// FORM UTILITIES
// ============================================================================

/**
 * Reset form and clear error messages
 * @param {HTMLFormElement} form - Form element to reset
 */
function resetForm(form) {
    form.reset();
    
    // Clear error messages
    const errorMessages = form.querySelectorAll('.alert-error');
    errorMessages.forEach(msg => msg.style.display = 'none');
    
    // Clear success messages
    const successMessages = form.querySelectorAll('.alert-success');
    successMessages.forEach(msg => msg.style.display = 'none');
}

/**
 * Disable form submission
 * @param {HTMLFormElement} form - Form element
 * @param {boolean} disabled - Disabled state
 */
function setFormDisabled(form, disabled) {
    const inputs = form.querySelectorAll('input, button, textarea, select');
    inputs.forEach(input => {
        input.disabled = disabled;
    });
}

// ============================================================================
// LOCAL STORAGE UTILITIES
// ============================================================================

/**
 * Save data to local storage
 * @param {string} key - Storage key
 * @param {any} data - Data to save
 */
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Error saving to local storage:', error);
    }
}

/**
 * Load data from local storage
 * @param {string} key - Storage key
 * @returns {any} Loaded data or null
 */
function loadFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('Error loading from local storage:', error);
        return null;
    }
}

/**
 * Remove data from local storage
 * @param {string} key - Storage key
 */
function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Error removing from local storage:', error);
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    // Add tooltip functionality if needed
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltips = document.querySelectorAll('.tooltip');
            tooltips.forEach(t => t.remove());
        });
    });
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + S to save/export
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            event.preventDefault();
            // Trigger export if available
            const exportBtn = document.querySelector('[data-action="export"]');
            if (exportBtn) {
                exportBtn.click();
            }
        }
        
        // Escape to close modals
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.active');
            modals.forEach(modal => modal.classList.remove('active'));
        }
    });
}

/**
 * Initialize all interactive features
 */
function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Log initialization
    console.log('ML Prediction Dashboard initialized');
}

// Run initialization when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);

// ============================================================================
// EXPORT FUNCTIONS FOR EXTERNAL USE
// ============================================================================

window.MLDashboard = {
    // Utility functions
    formatPercentage,
    formatNumber,
    showToast,
    validateFileSize,
    validateFileType,
    
    // Chart utilities
    getChartColors,
    getChartDefaultOptions,
    
    // Data formatting
    formatPrediction,
    formatProbability,
    calculateConfidence,
    
    // Table utilities
    createTableRow,
    
    // Pagination
    calculateTotalPages,
    getPaginatedData,
    
    // Export
    exportToCSV,
    
    // Animation
    animateNumber,
    
    // Form utilities
    resetForm,
    setFormDisabled,
    
    // Local storage
    saveToLocalStorage,
    loadFromLocalStorage,
    removeFromLocalStorage
};
