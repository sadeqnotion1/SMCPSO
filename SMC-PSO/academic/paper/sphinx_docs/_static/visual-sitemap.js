/**
 * Interactive Visual Sitemap using D3.js Force-Directed Graph
 * Modern, zoomable, draggable documentation navigation
 */

// Documentation structure data
const documentationData = {
    nodes: [
        // Root
        { id: "root", label: "DIP SMC PSO", group: 0, size: 50, url: "index.html" },

        // Main categories
        { id: "getting-started", label: "Getting Started", group: 1, size: 35, url: "guides/getting-started.html" },
        { id: "user-guides", label: "User Guides", group: 2, size: 35, url: "guides/index.html" },
        { id: "api", label: "API Reference", group: 3, size: 35, url: "api/index.html" },
        { id: "theory", label: "Theory & Math", group: 4, size: 35, url: "theory/index.html" },
        { id: "testing", label: "Testing", group: 5, size: 35, url: "testing/index.html" },
        { id: "deployment", label: "Deployment", group: 6, size: 35, url: "deployment/DEPLOYMENT_GUIDE.html" },
        { id: "project", label: "Project Docs", group: 7, size: 35, url: "CHANGELOG.html" },

        // Getting Started subcategories
        { id: "install", label: "Installation", group: 1, size: 20, url: "README.html" },
        { id: "quickstart", label: "Quick Start", group: 1, size: 20, url: "guides/getting-started.html" },
        { id: "dashboard", label: "Dashboard", group: 1, size: 20, url: "streamlit_dashboard_guide.html" },
        { id: "hil", label: "HIL Setup", group: 1, size: 20, url: "hil_quickstart.html" },

        // User Guides subcategories
        { id: "simulations", label: "Running Simulations", group: 2, size: 20, url: "guides/how-to/running-simulations.html" },
        { id: "pso-workflows", label: "PSO Optimization", group: 2, size: 20, url: "guides/how-to/optimization-workflows.html" },
        { id: "testing-guide", label: "Testing Workflows", group: 2, size: 20, url: "guides/how-to/testing-validation.html" },
        { id: "config", label: "Configuration", group: 2, size: 20, url: "guides/interactive_configuration_guide.html" },

        // API Reference subcategories
        { id: "controllers-api", label: "Controllers", group: 3, size: 25, url: "reference/controllers/index.html" },
        { id: "optimization-api", label: "Optimization", group: 3, size: 25, url: "reference/optimization/index.html" },
        { id: "simulation-api", label: "Simulation", group: 3, size: 25, url: "reference/simulation/index.html" },
        { id: "plant-api", label: "Plant Models", group: 3, size: 25, url: "reference/plant/index.html" },

        // Controllers
        { id: "classical-smc", label: "Classical SMC", group: 3, size: 15, url: "controllers/classical_smc_technical_guide.html" },
        { id: "sta-smc", label: "Super-Twisting", group: 3, size: 15, url: "controllers/sta_smc_technical_guide.html" },
        { id: "adaptive-smc", label: "Adaptive SMC", group: 3, size: 15, url: "controllers/adaptive_smc_technical_guide.html" },
        { id: "hybrid-smc", label: "Hybrid SMC", group: 3, size: 15, url: "controllers/hybrid_smc_technical_guide.html" },

        // Theory subcategories
        { id: "smc-theory", label: "SMC Theory", group: 4, size: 20, url: "theory/index.html" },
        { id: "pso-theory", label: "PSO Algorithm", group: 4, size: 20, url: "theory/pso_algorithm_foundations.html" },
        { id: "stability", label: "Stability Analysis", group: 4, size: 20, url: "mathematical_foundations/index.html" },
        { id: "dynamics", label: "Pendulum Dynamics", group: 4, size: 20, url: "plant_model.html" },

        // Testing subcategories
        { id: "test-standards", label: "Test Standards", group: 5, size: 20, url: "TESTING.html" },
        { id: "benchmarks", label: "Benchmarks", group: 5, size: 20, url: "benchmarks/index.html" },
        { id: "validation", label: "Validation", group: 5, size: 20, url: "validation/index.html" },

        // Deployment subcategories
        { id: "docker", label: "Docker", group: 6, size: 20, url: "deployment/docker.html" },
        { id: "streamlit-deploy", label: "Streamlit", group: 6, size: 20, url: "deployment/STREAMLIT_DEPLOYMENT.html" },
        { id: "production", label: "Production", group: 6, size: 20, url: "production/index.html" },

        // Project Docs subcategories
        { id: "changelog", label: "Changelog", group: 7, size: 20, url: "CHANGELOG.html" },
        { id: "contributing", label: "Contributing", group: 7, size: 20, url: "CONTRIBUTING.html" },
        { id: "citations", label: "Citations", group: 7, size: 20, url: "CITATIONS.html" }
    ],
    links: [
        // Root connections
        { source: "root", target: "getting-started", strength: 2 },
        { source: "root", target: "user-guides", strength: 2 },
        { source: "root", target: "api", strength: 2 },
        { source: "root", target: "theory", strength: 2 },
        { source: "root", target: "testing", strength: 2 },
        { source: "root", target: "deployment", strength: 2 },
        { source: "root", target: "project", strength: 2 },

        // Getting Started connections
        { source: "getting-started", target: "install", strength: 1.5 },
        { source: "getting-started", target: "quickstart", strength: 1.5 },
        { source: "getting-started", target: "dashboard", strength: 1.5 },
        { source: "getting-started", target: "hil", strength: 1.5 },

        // User Guides connections
        { source: "user-guides", target: "simulations", strength: 1.5 },
        { source: "user-guides", target: "pso-workflows", strength: 1.5 },
        { source: "user-guides", target: "testing-guide", strength: 1.5 },
        { source: "user-guides", target: "config", strength: 1.5 },

        // API connections
        { source: "api", target: "controllers-api", strength: 1.5 },
        { source: "api", target: "optimization-api", strength: 1.5 },
        { source: "api", target: "simulation-api", strength: 1.5 },
        { source: "api", target: "plant-api", strength: 1.5 },

        // Controllers connections
        { source: "controllers-api", target: "classical-smc", strength: 1 },
        { source: "controllers-api", target: "sta-smc", strength: 1 },
        { source: "controllers-api", target: "adaptive-smc", strength: 1 },
        { source: "controllers-api", target: "hybrid-smc", strength: 1 },

        // Theory connections
        { source: "theory", target: "smc-theory", strength: 1.5 },
        { source: "theory", target: "pso-theory", strength: 1.5 },
        { source: "theory", target: "stability", strength: 1.5 },
        { source: "theory", target: "dynamics", strength: 1.5 },

        // Testing connections
        { source: "testing", target: "test-standards", strength: 1.5 },
        { source: "testing", target: "benchmarks", strength: 1.5 },
        { source: "testing", target: "validation", strength: 1.5 },

        // Deployment connections
        { source: "deployment", target: "docker", strength: 1.5 },
        { source: "deployment", target: "streamlit-deploy", strength: 1.5 },
        { source: "deployment", target: "production", strength: 1.5 },

        // Project connections
        { source: "project", target: "changelog", strength: 1.5 },
        { source: "project", target: "contributing", strength: 1.5 },
        { source: "project", target: "citations", strength: 1.5 },

        // Cross-connections (workflow relationships)
        { source: "quickstart", target: "simulations", strength: 0.5 },
        { source: "simulations", target: "pso-workflows", strength: 0.5 },
        { source: "pso-workflows", target: "testing-guide", strength: 0.5 },
        { source: "controllers-api", target: "smc-theory", strength: 0.5 },
        { source: "optimization-api", target: "pso-theory", strength: 0.5 }
    ]
};

// Color scheme matching your brand
const colorScheme = [
    "#0b2763", // Root - DIP Dark Blue
    "#10b981", // Getting Started - Green
    "#3b82f6", // User Guides - Blue
    "#8b5cf6", // API - Purple
    "#ec4899", // Theory - Pink
    "#14b8a6", // Testing - Teal
    "#f59e0b", // Deployment - Orange
    "#6b7280"  // Project - Gray
];

function initVisualSitemap(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth;
    const height = 800;

    // Create SVG
    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .style("border-radius", "12px")
        .style("background", "linear-gradient(135deg, #f9fafb 0%, #ffffff 100%)");

    // Add zoom behavior
    const g = svg.append("g");

    const zoom = d3.zoom()
        .scaleExtent([0.3, 3])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoom);

    // Create force simulation
    const simulation = d3.forceSimulation(documentationData.nodes)
        .force("link", d3.forceLink(documentationData.links)
            .id(d => d.id)
            .distance(d => 80 / d.strength)
        )
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(d => d.size + 10));

    // Create links
    const link = g.append("g")
        .selectAll("line")
        .data(documentationData.links)
        .join("line")
        .attr("stroke", "#cbd5e1")
        .attr("stroke-opacity", d => 0.3 + d.strength * 0.2)
        .attr("stroke-width", d => d.strength * 2);

    // Create nodes
    const node = g.append("g")
        .selectAll("g")
        .data(documentationData.nodes)
        .join("g")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended)
        );

    // Add circles
    node.append("circle")
        .attr("r", d => d.size)
        .attr("fill", d => colorScheme[d.group])
        .attr("stroke", "#fff")
        .attr("stroke-width", 3)
        .style("cursor", "pointer")
        .style("filter", "drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))")
        .on("mouseover", function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr("r", d.size * 1.2)
                .style("filter", "drop-shadow(0 8px 15px rgba(0, 0, 0, 0.2))");
        })
        .on("mouseout", function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr("r", d.size)
                .style("filter", "drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))");
        })
        .on("click", function(event, d) {
            if (d.url) {
                window.location.href = d.url;
            }
        });

    // Add labels
    node.append("text")
        .text(d => d.label)
        .attr("text-anchor", "middle")
        .attr("dy", d => d.size + 20)
        .attr("font-size", d => d.size > 30 ? "14px" : "11px")
        .attr("font-weight", d => d.size > 30 ? "700" : "600")
        .attr("fill", "#1f2937")
        .style("pointer-events", "none")
        .style("user-select", "none");

    // Add tooltip
    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "graph-tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "rgba(15, 23, 42, 0.95)")
        .style("color", "white")
        .style("padding", "12px 16px")
        .style("border-radius", "8px")
        .style("font-size", "14px")
        .style("font-weight", "600")
        .style("box-shadow", "0 10px 25px rgba(0, 0, 0, 0.3)")
        .style("pointer-events", "none")
        .style("z-index", "10000");

    node.on("mouseover", function(event, d) {
        tooltip
            .style("visibility", "visible")
            .html(`<strong>${d.label}</strong><br/><span style="font-size: 12px; opacity: 0.8;">Click to open</span>`);
    })
    .on("mousemove", function(event) {
        tooltip
            .style("top", (event.pageY - 50) + "px")
            .style("left", (event.pageX + 10) + "px");
    })
    .on("mouseout", function() {
        tooltip.style("visibility", "hidden");
    });

    // Update positions on simulation tick
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Add legend
    const legend = svg.append("g")
        .attr("transform", `translate(20, 20)`);

    const legendData = [
        { label: "Getting Started", color: colorScheme[1] },
        { label: "User Guides", color: colorScheme[2] },
        { label: "API Reference", color: colorScheme[3] },
        { label: "Theory & Math", color: colorScheme[4] },
        { label: "Testing", color: colorScheme[5] },
        { label: "Deployment", color: colorScheme[6] },
        { label: "Project Docs", color: colorScheme[7] }
    ];

    legendData.forEach((item, i) => {
        const legendRow = legend.append("g")
            .attr("transform", `translate(0, ${i * 25})`);

        legendRow.append("circle")
            .attr("r", 8)
            .attr("fill", item.color)
            .attr("stroke", "#fff")
            .attr("stroke-width", 2);

        legendRow.append("text")
            .attr("x", 20)
            .attr("y", 5)
            .text(item.label)
            .attr("font-size", "12px")
            .attr("font-weight", "600")
            .attr("fill", "#1f2937");
    });

    // Add instructions
    const instructions = svg.append("text")
        .attr("x", width - 20)
        .attr("y", height - 20)
        .attr("text-anchor", "end")
        .attr("font-size", "12px")
        .attr("fill", "#6b7280")
        .text("💡 Drag nodes • Scroll to zoom • Click to navigate");
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initVisualSitemap('visual-sitemap-container'));
} else {
    initVisualSitemap('visual-sitemap-container');
}
