/**
 * DIP_SMC_PSO Control Room - Isometric Visualization
 * Interactive 3D system architecture with animated data flow
 */

// System components configuration
const COMPONENTS = {
    controllers: {
        id: 'controllers',
        label: 'Controllers',
        icon: '🎮',
        position: { x: 100, y: 100 },
        color: '#10b981',
        status: 'online',
        tooltip: 'Classical SMC, STA, Adaptive SMC, Hybrid Controllers',
        url: 'reference/controllers/index.html'
    },
    pso: {
        id: 'pso',
        label: 'PSO Engine',
        icon: '⚡',
        position: { x: 700, y: 100 },
        color: '#f59e0b',
        status: 'processing',
        tooltip: 'Particle Swarm Optimization & Parameter Tuning',
        url: 'reference/optimization/index.html'
    },
    simulation: {
        id: 'simulation',
        label: 'Simulation Core',
        icon: '🖥️',
        position: { x: 400, y: 250 },
        color: '#3b82f6',
        status: 'online',
        tooltip: 'Simulation Engine & Orchestration',
        url: 'reference/simulation/index.html'
    },
    plant: {
        id: 'plant',
        label: 'Plant Dynamics',
        icon: '📐',
        position: { x: 150, y: 400 },
        color: '#ec4899',
        status: 'online',
        tooltip: 'Double Inverted Pendulum Models',
        url: 'reference/plant/index.html'
    },
    monitoring: {
        id: 'monitoring',
        label: 'Monitoring',
        icon: '📊',
        position: { x: 650, y: 400 },
        color: '#14b8a6',
        status: 'online',
        tooltip: 'Real-time Metrics & Health Monitoring',
        url: 'reference/interfaces/monitoring___init__.html'
    },
    testing: {
        id: 'testing',
        label: 'Testing & QA',
        icon: '✅',
        position: { x: 400, y: 500 },
        color: '#8b5cf6',
        status: 'standby',
        tooltip: 'Test Suite & Validation Framework',
        url: 'TESTING.html'
    },
    storage: {
        id: 'storage',
        label: 'Data Storage',
        icon: '💾',
        position: { x: 250, y: 300 },
        color: '#6366f1',
        status: 'online',
        tooltip: 'Results & Configuration Storage',
        url: 'guides/index.html'
    },
    hil: {
        id: 'hil',
        label: 'HIL Interface',
        icon: '🔌',
        position: { x: 550, y: 300 },
        color: '#f97316',
        status: 'standby',
        tooltip: 'Hardware-in-the-Loop Integration',
        url: 'hil_quickstart.html'
    }
};

// Connection definitions (data flow)
const CONNECTIONS = [
    { from: 'controllers', to: 'simulation', bidirectional: true },
    { from: 'pso', to: 'controllers', bidirectional: false },
    { from: 'simulation', to: 'plant', bidirectional: true },
    { from: 'plant', to: 'storage', bidirectional: false },
    { from: 'simulation', to: 'monitoring', bidirectional: false },
    { from: 'monitoring', to: 'testing', bidirectional: false },
    { from: 'simulation', to: 'hil', bidirectional: true },
    { from: 'storage', to: 'testing', bidirectional: false }
];

// Isometric projection helper
function toIsometric(x, y) {
    const angle = Math.PI / 6; // 30 degrees
    return {
        x: (x - y) * Math.cos(angle),
        y: (x + y) * Math.sin(angle) * 0.5
    };
}

// Initialize control room
function initControlRoom() {
    const container = document.querySelector('.isometric-scene');
    if (!container) {
        console.warn('Control room container not found');
        return;
    }

    // Create components
    Object.values(COMPONENTS).forEach(component => {
        createComponent(container, component);
    });

    // Create connections
    CONNECTIONS.forEach(connection => {
        createConnection(container, connection);
    });

    // Start particle animations
    startParticleSystem(container);

    // Add keyboard navigation
    setupKeyboardNav();
}

// Create a component box
function createComponent(container, component) {
    const box = document.createElement('div');
    box.className = `iso-component component-${component.id}`;
    box.style.left = `${component.position.x}px`;
    box.style.top = `${component.position.y}px`;

    // Status indicator
    const status = document.createElement('div');
    status.className = `status-indicator status-${component.status}`;
    box.appendChild(status);

    // Icon and label
    const icon = document.createElement('div');
    icon.className = 'component-icon';
    icon.textContent = component.icon;
    icon.style.color = component.color;

    const label = document.createElement('div');
    label.className = 'component-label';
    label.textContent = component.label;

    // Tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'component-tooltip';
    tooltip.textContent = component.tooltip;

    box.appendChild(icon);
    box.appendChild(label);
    box.appendChild(tooltip);

    // Click handler
    box.addEventListener('click', () => {
        if (component.url) {
            window.location.href = component.url;
        }
    });

    // Hover effect - enhance glow
    box.addEventListener('mouseenter', () => {
        box.style.filter = `drop-shadow(0 20px 40px ${component.color})`;
    });

    box.addEventListener('mouseleave', () => {
        box.style.filter = 'drop-shadow(0 10px 20px rgba(0, 0, 0, 0.5))';
    });

    container.appendChild(box);
}

// Create connection line between components
function createConnection(container, connection) {
    const from = COMPONENTS[connection.from];
    const to = COMPONENTS[connection.to];

    if (!from || !to) return;

    const line = document.createElement('div');
    line.className = 'connection-line';

    // Calculate line position and rotation
    const dx = to.position.x - from.position.x;
    const dy = to.position.y - from.position.y;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * (180 / Math.PI);

    line.style.width = `${length}px`;
    line.style.left = `${from.position.x + 60}px`;
    line.style.top = `${from.position.y + 60}px`;
    line.style.transform = `rotate(${angle}deg)`;
    line.style.transformOrigin = 'left center';

    container.appendChild(line);

    // Add reverse line if bidirectional
    if (connection.bidirectional) {
        const reverseLine = line.cloneNode(true);
        reverseLine.style.animationDelay = '1s';
        reverseLine.style.opacity = '0.5';
        container.appendChild(reverseLine);
    }
}

// Particle system for data flow
function startParticleSystem(container) {
    setInterval(() => {
        CONNECTIONS.forEach((connection, index) => {
            setTimeout(() => {
                createParticle(container, connection);
            }, index * 300);
        });
    }, 3000);
}

// Create a single data particle
function createParticle(container, connection) {
    const from = COMPONENTS[connection.from];
    const to = COMPONENTS[connection.to];

    if (!from || !to) return;

    const particle = document.createElement('div');
    particle.className = 'data-particle';
    particle.style.left = `${from.position.x + 60}px`;
    particle.style.top = `${from.position.y + 60}px`;
    particle.style.background = from.color;
    particle.style.boxShadow = `0 0 10px ${from.color}`;

    container.appendChild(particle);

    // Animate particle to destination
    const dx = to.position.x - from.position.x;
    const dy = to.position.y - from.position.y;

    particle.style.setProperty('--dx', `${dx}px`);
    particle.style.setProperty('--dy', `${dy}px`);

    // Remove after animation
    setTimeout(() => {
        particle.remove();
    }, 2000);
}

// Keyboard navigation
function setupKeyboardNav() {
    const components = Object.keys(COMPONENTS);
    let currentIndex = 0;

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === 'Tab') {
            e.preventDefault();
            currentIndex = (currentIndex + 1) % components.length;
            highlightComponent(components[currentIndex]);
        } else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            currentIndex = (currentIndex - 1 + components.length) % components.length;
            highlightComponent(components[currentIndex]);
        } else if (e.key === 'Enter') {
            const component = COMPONENTS[components[currentIndex]];
            if (component.url) {
                window.location.href = component.url;
            }
        }
    });
}

// Highlight component for keyboard navigation
function highlightComponent(componentId) {
    // Remove previous highlights
    document.querySelectorAll('.iso-component').forEach(el => {
        el.style.outline = 'none';
    });

    // Highlight current
    const element = document.querySelector(`.component-${componentId}`);
    if (element) {
        element.style.outline = '3px solid #3b82f6';
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Update particle animation with custom properties
const style = document.createElement('style');
style.textContent = `
    .data-particle {
        --dx: 0px;
        --dy: 0px;
    }

    @keyframes particleFlow {
        0% {
            transform: translate(0, 0) scale(1);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
            transform: translate(var(--dx), var(--dy)) scale(0.5);
        }
        100% {
            transform: translate(var(--dx), var(--dy)) scale(0);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initControlRoom);
} else {
    initControlRoom();
}

// Export for external use
window.ControlRoom = {
    init: initControlRoom,
    components: COMPONENTS,
    connections: CONNECTIONS
};
