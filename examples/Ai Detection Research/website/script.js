// Track which charts have been initialized
let initializedCharts = new Set();

// Tab functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            // Initialize charts for this tab if not already done
            setTimeout(() => {
                initializeTabCharts(tabName);
            }, 100);
        });
    });

    // Load initial content
    loadResearchContent();
    
    // Initialize charts for the initially active tab
    setTimeout(() => {
        initializeTabCharts('claude');
    }, 500);
});

// Toggle full research view
function toggleFullResearch(tool) {
    const fullResearch = document.getElementById(`${tool}-full`);
    const button = event.target;
    
    if (fullResearch.classList.contains('hidden')) {
        fullResearch.classList.remove('hidden');
        button.textContent = 'Hide Full Research ▲';
    } else {
        fullResearch.classList.add('hidden');
        button.textContent = 'View Full Research ▼';
    }
}

// Load research content
function loadResearchContent() {
    // Check if data is available
    if (typeof window.researchData === 'undefined') {
        console.error('Research data not loaded');
        return;
    }
    
    // Load initial prompt
    document.getElementById('initial-prompt-content').innerHTML = marked.parse(window.researchData.initialPrompt);
    
    // Load Claude research
    document.getElementById('claude-summary').innerHTML = marked.parse(window.researchData.claude.summary);
    document.getElementById('claude-full').innerHTML = marked.parse(window.researchData.claude.fullResearch);
    
    // Load Gemini research
    document.getElementById('gemini-summary').innerHTML = marked.parse(window.researchData.gemini.summary);
    document.getElementById('gemini-full').innerHTML = marked.parse(window.researchData.gemini.fullResearch);
    
    // Load Manus research
    document.getElementById('manus-summary').innerHTML = marked.parse(window.researchData.manus.summary);
    document.getElementById('manus-full').innerHTML = marked.parse(window.researchData.manus.fullResearch);
    
    // Load OpenAI research
    document.getElementById('openai-summary').innerHTML = marked.parse(window.researchData.openai.summary);
    document.getElementById('openai-full').innerHTML = marked.parse(window.researchData.openai.fullResearch);
    
    // Load Perplexity research
    document.getElementById('perplexity-summary').innerHTML = marked.parse(window.researchData.perplexity.summary);
    document.getElementById('perplexity-full').innerHTML = marked.parse(window.researchData.perplexity.fullResearch);
}

// Add smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add loading states
function showLoading(elementId) {
    document.getElementById(elementId).innerHTML = '<div class="loading">Loading content</div>';
}

// Error handling
function showError(elementId, message) {
    document.getElementById(elementId).innerHTML = `<div class="error">${message}</div>`;
}// Enhanced script with visualizations

// Load research content
function loadResearchContent() {
    // Check if data is available
    if (typeof window.researchData === 'undefined') {
        console.error('Research data not loaded');
        return;
    }
    
    // Load initial prompt
    document.getElementById('initial-prompt-content').innerHTML = marked.parse(window.researchData.initialPrompt);
    
    // Load Claude research
    document.getElementById('claude-full').innerHTML = marked.parse(window.researchData.claude.fullResearch);
    
    // Load Gemini research
    document.getElementById('gemini-full').innerHTML = marked.parse(window.researchData.gemini.fullResearch);
    
    // Load Manus research
    document.getElementById('manus-full').innerHTML = marked.parse(window.researchData.manus.fullResearch);
    
    // Load OpenAI research
    document.getElementById('openai-full').innerHTML = marked.parse(window.researchData.openai.fullResearch);
    
    // Load Perplexity research
    document.getElementById('perplexity-full').innerHTML = marked.parse(window.researchData.perplexity.fullResearch);
}

// Store chart instances
let chartInstances = {};

// Initialize charts for specific tab
function initializeTabCharts(tabName) {
    // Only initialize if not already done for this tab
    if (initializedCharts.has(tabName)) {
        return;
    }
    
    switch(tabName) {
        case 'claude':
            if (!chartInstances['claudeAccuracy']) {
                createClaudeAccuracyChart();
            }
            if (!chartInstances['claudeMarket']) {
                createClaudeMarketChart();
            }
            break;
        case 'gemini':
            if (!chartInstances['geminiEffectiveness']) {
                createGeminiEffectivenessChart();
            }
            break;
        case 'overview':
            if (!chartInstances['comparisonRadar']) {
                createComparisonRadarChart();
            }
            break;
    }
    
    initializedCharts.add(tabName);
}

// Claude Accuracy Chart
function createClaudeAccuracyChart() {
    const ctx = document.getElementById('claude-accuracy-chart');
    if (!ctx) return;
    
    chartInstances['claudeAccuracy'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Text', 'Image', 'Video', 'Voice'],
            datasets: [{
                label: 'Claimed Accuracy',
                data: [99, 98, 96, 99],
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2
            }, {
                label: 'Real-World Accuracy',
                data: [69, 77, 75, 86],
                backgroundColor: 'rgba(239, 68, 68, 0.5)',
                borderColor: 'rgba(239, 68, 68, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'AI Detection Accuracy: Claims vs Reality'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + '%';
                        }
                    }
                }
            }
        }
    });
}

// Claude Market Growth Chart
function createClaudeMarketChart() {
    const ctx = document.getElementById('claude-market-chart');
    if (!ctx) return;
    
    chartInstances['claudeMarket'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032'],
            datasets: [{
                label: 'Market Size ($B)',
                data: [1.3, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 3.9, 4.1],
                borderColor: 'rgba(16, 185, 129, 1)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value + 'B';
                        }
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Deepfake Detection Market Growth'
                },
                annotation: {
                    annotations: {
                        criticalWindow: {
                            type: 'box',
                            xMin: 0,
                            xMax: 1.5,
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            borderColor: 'rgba(239, 68, 68, 0.5)',
                            borderWidth: 2
                        }
                    }
                }
            }
        }
    });
}

// Gemini Effectiveness Chart
function createGeminiEffectivenessChart() {
    const ctx = document.getElementById('gemini-effectiveness-chart');
    if (!ctx) return;
    
    chartInstances['geminiEffectiveness'] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Pure AI Detection', 'Mixed Content', 'Evaded Content', 'False Positives'],
            datasets: [{
                data: [95, 89, 26, 5],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Detection Effectiveness by Content Type'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

// Comparison Radar Chart
function createComparisonRadarChart() {
    const ctx = document.getElementById('comparison-radar-chart');
    if (!ctx) return;
    
    chartInstances['comparisonRadar'] = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Comprehensiveness',
                'Technical Detail',
                'Practical Actions',
                'Developer Focus',
                'User Accessibility',
                'Future Vision'
            ],
            datasets: [{
                label: 'Claude',
                data: [100, 90, 95, 85, 80, 90],
                borderColor: 'rgba(59, 130, 246, 1)',
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderWidth: 2
            }, {
                label: 'Gemini',
                data: [85, 95, 70, 60, 75, 85],
                borderColor: 'rgba(236, 72, 153, 1)',
                backgroundColor: 'rgba(236, 72, 153, 0.2)',
                borderWidth: 2
            }, {
                label: 'Manus',
                data: [70, 60, 85, 75, 95, 60],
                borderColor: 'rgba(16, 185, 129, 1)',
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                borderWidth: 2
            }, {
                label: 'OpenAI',
                data: [80, 85, 75, 95, 70, 90],
                borderColor: 'rgba(139, 92, 246, 1)',
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                borderWidth: 2
            }, {
                label: 'Perplexity',
                data: [75, 70, 80, 70, 85, 75],
                borderColor: 'rgba(249, 115, 22, 1)',
                backgroundColor: 'rgba(249, 115, 22, 0.2)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'AI Research Approach Comparison',
                    padding: {
                        top: 10,
                        bottom: 30
                    }
                }
            }
        }
    });
}

