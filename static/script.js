function formatPercentage(value, decimals = 2) {
    return (value * 100).toFixed(decimals) + '%';
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="bi bi-${getToastIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function getToastIcon(type) {
    const icons = {
        'success': 'check-circle-fill',
        'error': 'exclamation-triangle-fill',
        'info': 'info-circle-fill'
    };
    return icons[type] || icons['info'];
}

function validateFileSize(file, maxSizeMB = 16) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
}

function validateFileType(file) {
    const allowedExtensions = ['xlsx', 'xls', 'csv'];
    const extension = file.name.split('.').pop().toLowerCase();
    return allowedExtensions.includes(extension);
}

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

function formatPrediction(prediction) {
    return {
        label: prediction === 1 ? 'Fraud' : 'Legitimate',
        class: prediction === 1 ? 'fraud' : 'legit',
        color: prediction === 1 ? '#ef4444' : '#10b981'
    };
}

function formatProbability(probability) {
    return (probability * 100).toFixed(2) + '%';
}

function calculateConfidence(probabilities) {
    return Math.max(...probabilities);
}

function createTableRow(rowIndex, prediction, probabilities) {
    const row = document.createElement('tr');
    
    let fraudProb = probabilities.fraud ?? probabilities[1] ?? 0;
    let legitProb = probabilities.legit ?? probabilities[0] ?? 0;
  
    fraudProb = Math.min(Math.max(fraudProb, 0), 1);
    legitProb = Math.min(Math.max(legitProb, 0), 1);
    const confidence = Math.max(fraudProb, legitProb);
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

function calculateTotalPages(totalItems, itemsPerPage) {
    return Math.ceil(totalItems / itemsPerPage);
}

function getPaginatedData(data, page, itemsPerPage) {
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return data.slice(startIndex, endIndex);
}

function exportToCSV(data, filename = 'export.csv') {
    if (!data || data.length === 0) {
        showToast('No data to export', 'error');
        return;
    }

    const headers = Object.keys(data[0]);

    let csvContent = headers.join(',') + '\n';
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        });
        csvContent += values.join(',') + '\n';
    });

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

function resetForm(form) {
    form.reset();

    const errorMessages = form.querySelectorAll('.alert-error');
    errorMessages.forEach(msg => msg.style.display = 'none');

    const successMessages = form.querySelectorAll('.alert-success');
    successMessages.forEach(msg => msg.style.display = 'none');
}

function setFormDisabled(form, disabled) {
    const inputs = form.querySelectorAll('input, button, textarea, select');
    inputs.forEach(input => {
        input.disabled = disabled;
    });
}

function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Error saving to local storage:', error);
    }
}

function loadFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('Error loading from local storage:', error);
        return null;
    }
}

function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Error removing from local storage:', error);
    }
}

function initializeTooltips() {
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

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            event.preventDefault();
            const exportBtn = document.querySelector('[data-action="export"]');
            if (exportBtn) {
                exportBtn.click();
            }
        }

        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.active');
            modals.forEach(modal => modal.classList.remove('active'));
        }
    });
}

function initializeApp() {
    initializeTooltips();
    initializeKeyboardShortcuts();
    console.log('ML Prediction Dashboard initialized');
}

document.addEventListener('DOMContentLoaded', initializeApp);

window.MLDashboard = {
    formatPercentage,
    formatNumber,
    showToast,
    validateFileSize,
    validateFileType,
    getChartColors,
    getChartDefaultOptions,
    formatPrediction,
    formatProbability,
    calculateConfidence,
    createTableRow,
    calculateTotalPages,
    getPaginatedData,
    exportToCSV,
    animateNumber,
    resetForm,
    setFormDisabled,
    saveToLocalStorage,
    loadFromLocalStorage,
    removeFromLocalStorage
};
