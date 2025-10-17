// Honeywell Aerospace Competitive Analysis - Modern JavaScript

class CompetitiveAnalysisApp {
    constructor() {
        this.isAnalyzing = false;
        this.currentAnalysis = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadReports();
        this.checkStatus();
    }

    bindEvents() {
        // Analysis form submission
        const analysisForm = document.getElementById('analysisForm');
        if (analysisForm) {
            analysisForm.addEventListener('submit', (e) => this.handleAnalysisSubmit(e));
        }

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Auto-refresh reports every 30 seconds
        setInterval(() => {
            if (!this.isAnalyzing) {
                this.loadReports();
            }
        }, 30000);
    }

    async handleAnalysisSubmit(e) {
        e.preventDefault();
        
        if (this.isAnalyzing) {
            return;
        }

        const honeywellProduct = document.getElementById('honeywellProduct').value.trim();
        const competitorQuery = document.getElementById('competitorQuery').value.trim();

        if (!honeywellProduct || !competitorQuery) {
            this.showAlert('Please fill in both fields', 'warning');
            return;
        }

        this.startAnalysis(honeywellProduct, competitorQuery);
    }

    async startAnalysis(honeywellProduct, competitorQuery) {
        this.isAnalyzing = true;
        this.updateAnalyzeButton(true);

        try {
            this.showAlert('Starting competitive analysis...', 'info');
            
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    honeywell_product: honeywellProduct,
                    competitor_query: competitorQuery
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.currentAnalysis = data.result;
                // Use analysis_results if available, otherwise fall back to result
                const analysisData = data.result.analysis_results || data.result;
                this.displayResults(analysisData);
                this.showAlert('Analysis completed successfully!', 'success');
                this.loadReports(); // Refresh reports list
                
                // Trigger plane celebration animation
                this.triggerPlaneCelebration();
            } else {
                throw new Error(data.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Analysis error:', error);
            this.showAlert(`Analysis failed: ${error.message}`, 'danger');
        } finally {
            this.isAnalyzing = false;
            this.updateAnalyzeButton(false);
        }
    }

    updateAnalyzeButton(isAnalyzing) {
        const button = document.getElementById('analyzeBtn');
        const spinner = button.querySelector('.spinner-border');
        const text = button.querySelector('.btn-text');

        if (isAnalyzing) {
            button.disabled = true;
            spinner.classList.remove('d-none');
            text.textContent = 'Analyzing...';
            button.classList.add('pulse');
        } else {
            button.disabled = false;
            spinner.classList.add('d-none');
            text.textContent = 'Run Analysis';
            button.classList.remove('pulse');
        }
    }

    displayResults(result) {
        const resultsSection = document.getElementById('results');
        const resultsContent = document.getElementById('resultsContent');

        if (!result) {
            resultsSection.classList.add('d-none');
            return;
        }

        // Build results HTML
        let html = `
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="result-item aerospace-theme">
                        <h5><i class="fas fa-chart-line me-2"></i>Analysis Summary</h5>
                        <p class="mb-2"><strong>Product:</strong> ${result.honeywell_product || 'N/A'}</p>
                        <p class="mb-2"><strong>Comparison:</strong> ${result.competitor_query || 'N/A'}</p>
                        <p class="mb-0"><strong>Confidence:</strong> 
                            <span class="confidence-badge ${this.getConfidenceClass(result.confidence_score)}">
                                ${(result.confidence_score * 100).toFixed(1)}%
                            </span>
                        </p>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="result-item aerospace-theme">
                        <h5><i class="fas fa-database me-2"></i>Data Sources</h5>
                        <p class="mb-2"><strong>Sources Used:</strong> ${result.data_sources_used?.length || 0}</p>
                        <p class="mb-0"><strong>Analysis Time:</strong> ${result.analysis_timestamp ? new Date(result.analysis_timestamp).toLocaleString() : 'N/A'}</p>
                    </div>
                </div>
            </div>
        `;

        // Competitive Gaps
        if (result.competitive_gaps && result.competitive_gaps.length > 0) {
            html += `
                <div class="row">
                    <div class="col-12 mb-4">
                        <h5><i class="fas fa-exclamation-triangle me-2"></i>Competitive Gaps (${result.competitive_gaps.length})</h5>
                        <div class="row">
            `;
            
            result.competitive_gaps.forEach(gap => {
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="result-item aerospace-theme">
                            <h6 class="text-${this.getImpactColor(gap.impact)}">${gap.category}</h6>
                            <p class="mb-2"><strong>Gap:</strong> ${gap.gap}</p>
                            <p class="mb-2"><strong>Impact:</strong> <span class="badge bg-${this.getImpactColor(gap.impact)}">${gap.impact}</span></p>
                            <p class="mb-0"><strong>Opportunity:</strong> ${gap.opportunity}</p>
                        </div>
                    </div>
                `;
            });
            
            html += `
                        </div>
                    </div>
                </div>
            `;
        }

        // Key Insights
        if (result.insights && result.insights.length > 0) {
            html += `
                <div class="row">
                    <div class="col-12 mb-4">
                        <h5><i class="fas fa-lightbulb me-2"></i>Key Insights (${result.insights.length})</h5>
                        <div class="result-item aerospace-theme">
                            <ul class="list-unstyled mb-0">
            `;
            
            result.insights.slice(0, 10).forEach(insight => {
                html += `<li class="mb-2"><i class="fas fa-arrow-right me-2 text-primary"></i>${insight}</li>`;
            });
            
            html += `
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }

        // Strategic Recommendations
        if (result.recommendations && result.recommendations.length > 0) {
            html += `
                <div class="row">
                    <div class="col-12 mb-4">
                        <h5><i class="fas fa-target me-2"></i>Strategic Recommendations</h5>
                        <div class="result-item aerospace-theme">
                            <ol class="mb-0">
            `;
            
            result.recommendations.forEach(rec => {
                html += `<li class="mb-2">${rec}</li>`;
            });
            
            html += `
                            </ol>
                        </div>
                    </div>
                </div>
            `;
        }

        resultsContent.innerHTML = html;
        resultsSection.classList.remove('d-none');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    async loadReports() {
        try {
            const response = await fetch('/reports');
            const data = await response.json();

            if (response.ok) {
                this.displayReports(data.reports);
            } else {
                throw new Error(data.error || 'Failed to load reports');
            }
        } catch (error) {
            console.error('Error loading reports:', error);
            this.displayReportsError(error.message);
        }
    }

    displayReports(reports) {
        const reportsList = document.getElementById('reportsList');

        if (!reports || reports.length === 0) {
            reportsList.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-file-pdf fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No reports available yet. Run an analysis to generate your first report!</p>
                </div>
            `;
            return;
        }

        let html = '';
        reports.forEach(report => {
            const sizeKB = (report.size / 1024).toFixed(1);
            const createdDate = new Date(report.created).toLocaleDateString();
            const createdTime = new Date(report.created).toLocaleTimeString();
            
            html += `
                <div class="report-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-2">
                                <i class="fas fa-file-pdf me-2 text-danger"></i>
                                ${report.filename}
                            </h6>
                            <div class="report-meta">
                                <span class="me-3"><i class="fas fa-calendar me-1"></i>${createdDate}</span>
                                <span class="me-3"><i class="fas fa-clock me-1"></i>${createdTime}</span>
                                <span><i class="fas fa-weight me-1"></i>${sizeKB} KB</span>
                            </div>
                        </div>
                        <div class="ms-3">
                            <button class="btn btn-outline-primary btn-sm" onclick="app.downloadReport('${report.filename}')">
                                <i class="fas fa-download me-1"></i>Download
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        reportsList.innerHTML = html;
    }

    displayReportsError(message) {
        const reportsList = document.getElementById('reportsList');
        reportsList.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Failed to load reports: ${message}
            </div>
        `;
    }

    async downloadReport(filename) {
        try {
            const response = await fetch(`/download/${filename}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showAlert(`Downloaded ${filename}`, 'success');
            } else {
                throw new Error('Download failed');
            }
        } catch (error) {
            console.error('Download error:', error);
            this.showAlert(`Download failed: ${error.message}`, 'danger');
        }
    }

    async checkStatus() {
        try {
            const response = await fetch('/status');
            const data = await response.json();
            
            if (response.ok) {
                console.log('API Status:', data.status);
            }
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }

    showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of the analysis section
        const analysisSection = document.getElementById('analysis');
        analysisSection.insertBefore(alertDiv, analysisSection.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    getConfidenceClass(score) {
        if (score >= 0.8) return 'confidence-high';
        if (score >= 0.6) return 'confidence-medium';
        return 'confidence-low';
    }

    getImpactColor(impact) {
        switch (impact.toLowerCase()) {
            case 'high': return 'danger';
            case 'medium': return 'warning';
            case 'low': return 'success';
            default: return 'secondary';
        }
    }

    triggerPlaneCelebration() {
        // Create success overlay
        const overlay = document.createElement('div');
        overlay.className = 'success-overlay';
        document.body.appendChild(overlay);
        
        // Create flying plane
        const plane = document.createElement('div');
        plane.className = 'plane-celebration';
        plane.innerHTML = '✈️';
        document.body.appendChild(plane);
        
        // Remove elements after animation completes
        setTimeout(() => {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            if (plane.parentNode) plane.parentNode.removeChild(plane);
        }, 3000);
    }
}

// Utility functions
function scrollToAnalysis() {
    document.getElementById('analysis').scrollIntoView({ behavior: 'smooth' });
}

function scrollToReports() {
    document.getElementById('reports').scrollIntoView({ behavior: 'smooth' });
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CompetitiveAnalysisApp();
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.app) {
        window.app.loadReports();
    }
});
