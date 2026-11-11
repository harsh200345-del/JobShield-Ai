/**
 * JobShield AI - Chart.js Visualization Engine
 * Renders interactive Category Radar and Gauge Breakdown
 */

function initRiskCharts(categoryScores, totalScore, riskLevel) {
    // 1. Radar Chart: 5 Safety Categories
    const radarCtx = document.getElementById("riskRadarChart");
    if (radarCtx) {
        const labels = [
            "Financial Demands",
            "Communication Channels",
            "Promise Realism",
            "Role Clarity",
            "Pressure & Urgency"
        ];
        
        const dataValues = [
            categoryScores.financial || 0,
            categoryScores.communication || 0,
            categoryScores.realism || 0,
            categoryScores.role_clarity || 0,
            categoryScores.pressure || 0
        ];

        let accentColor = "#10b981"; // green
        let accentBg = "rgba(16, 185, 129, 0.2)";
        if (riskLevel === "HIGH") {
            accentColor = "#ef4444";
            accentBg = "rgba(239, 68, 68, 0.25)";
        } else if (riskLevel === "MEDIUM") {
            accentColor = "#f59e0b";
            accentBg = "rgba(245, 158, 11, 0.25)";
        }

        new Chart(radarCtx, {
            type: "radar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Detected Risk Severity (0-100)",
                    data: dataValues,
                    backgroundColor: accentBg,
                    borderColor: accentColor,
                    borderWidth: 2,
                    pointBackgroundColor: accentColor,
                    pointBorderColor: "#fff",
                    pointHoverBackgroundColor: "#fff",
                    pointHoverBorderColor: accentColor
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: "#e2e8f0" },
                        grid: { color: "#e2e8f0" },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: {
                            stepSize: 20,
                            font: { size: 10 }
                        },
                        pointLabels: {
                            font: { size: 11, weight: "bold" },
                            color: "#334155"
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return ` Risk Factor: ${context.raw} / 100`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 2. Doughnut Gauge: Total Score
    const gaugeCtx = document.getElementById("riskGaugeChart");
    if (gaugeCtx) {
        let gaugeColor = "#10b981";
        if (riskLevel === "HIGH") gaugeColor = "#ef4444";
        else if (riskLevel === "MEDIUM") gaugeColor = "#f59e0b";

        new Chart(gaugeCtx, {
            type: "doughnut",
            data: {
                datasets: [{
                    data: [totalScore, Math.max(0, 100 - totalScore)],
                    backgroundColor: [gaugeColor, "#e2e8f0"],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "75%",
                plugins: {
                    tooltip: { enabled: false },
                    legend: { display: false }
                }
            }
        });
    }
}
