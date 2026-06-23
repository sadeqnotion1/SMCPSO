/**
 * ============================================================================
 * Three.js Interactive Double-Inverted Pendulum Visualization
 * ============================================================================
 *
 * Real-time 3D physics simulation with user-controlled parameters.
 * Uses simplified dynamics for smooth browser performance.
 *
 * Features:
 * - WebGL rendering with Three.js
 * - Interactive parameter sliders (gains, masses, lengths)
 * - Orbit controls (zoom, pan, rotate)
 * - Material/lighting effects
 * - Real-time physics integration
 * ============================================================================
 */

class PendulumSimulator3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Simulation state
        this.state = {
            x: 0,      // Cart position
            theta1: 0.1, // First pendulum angle (rad)
            theta2: 0.1, // Second pendulum angle (rad)
            x_dot: 0,
            theta1_dot: 0,
            theta2_dot: 0
        };

        // Physical parameters (from config.yaml defaults)
        this.params = {
            m0: 1.0,   // Cart mass (kg)
            m1: 0.1,   // First pendulum mass (kg)
            m2: 0.1,   // Second pendulum mass (kg)
            l1: 0.5,   // First pendulum length (m)
            l2: 0.5,   // Second pendulum length (m)
            g: 9.81,   // Gravity (m/s^2)
            dt: 0.01   // Time step (s)
        };

        // Controller gains (Classical SMC defaults)
        this.gains = {
            k1: 10.0,
            k2: 5.0,
            k3: 8.0,
            k4: 3.0,
            k5: 15.0,
            k6: 2.0
        };

        // Simulation control
        this.running = false;
        this.time = 0;
        this.animationId = null;

        this.init();
    }

    init() {
        this.setupScene();
        this.setupLights();
        this.setupPendulum();
        this.setupControls();
        this.setupUI();
        this.animate();
    }

    setupScene() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            60,
            this.container.clientWidth / this.container.clientHeight,
            0.1,
            100
        );
        this.camera.position.set(3, 2, 3);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);

        // Grid helper
        const gridHelper = new THREE.GridHelper(10, 20, 0x888888, 0xcccccc);
        this.scene.add(gridHelper);

        // Axes helper
        const axesHelper = new THREE.AxesHelper(1);
        this.scene.add(axesHelper);

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize(), false);
    }

    setupLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        // Directional light (sun)
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 5);
        dirLight.castShadow = true;
        dirLight.shadow.camera.near = 0.1;
        dirLight.shadow.camera.far = 50;
        dirLight.shadow.camera.left = -5;
        dirLight.shadow.camera.right = 5;
        dirLight.shadow.camera.top = 5;
        dirLight.shadow.camera.bottom = -5;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        this.scene.add(dirLight);

        // Point light for highlights
        const pointLight = new THREE.PointLight(0xffffff, 0.4);
        pointLight.position.set(0, 3, 0);
        this.scene.add(pointLight);
    }

    setupPendulum() {
        // Rail (track for cart)
        const railGeometry = new THREE.CylinderGeometry(0.02, 0.02, 4, 16);
        const railMaterial = new THREE.MeshStandardMaterial({
            color: 0x666666,
            metalness: 0.8,
            roughness: 0.2
        });
        this.rail = new THREE.Mesh(railGeometry, railMaterial);
        this.rail.rotation.z = Math.PI / 2;
        this.rail.position.y = 0;
        this.rail.castShadow = true;
        this.scene.add(this.rail);

        // Cart
        const cartGeometry = new THREE.BoxGeometry(0.3, 0.15, 0.2);
        const cartMaterial = new THREE.MeshStandardMaterial({
            color: 0x2196F3,
            metalness: 0.5,
            roughness: 0.3
        });
        this.cart = new THREE.Mesh(cartGeometry, cartMaterial);
        this.cart.castShadow = true;
        this.cart.receiveShadow = true;
        this.scene.add(this.cart);

        // First pendulum rod
        const rod1Geometry = new THREE.CylinderGeometry(0.015, 0.015, this.params.l1, 16);
        const rod1Material = new THREE.MeshStandardMaterial({
            color: 0xFF5722,
            metalness: 0.7,
            roughness: 0.2
        });
        this.rod1 = new THREE.Mesh(rod1Geometry, rod1Material);
        this.rod1.castShadow = true;
        this.scene.add(this.rod1);

        // First pendulum bob
        const bob1Geometry = new THREE.SphereGeometry(0.05, 32, 32);
        const bob1Material = new THREE.MeshStandardMaterial({
            color: 0xFF5722,
            metalness: 0.8,
            roughness: 0.2
        });
        this.bob1 = new THREE.Mesh(bob1Geometry, bob1Material);
        this.bob1.castShadow = true;
        this.scene.add(this.bob1);

        // Second pendulum rod
        const rod2Geometry = new THREE.CylinderGeometry(0.015, 0.015, this.params.l2, 16);
        const rod2Material = new THREE.MeshStandardMaterial({
            color: 0x4CAF50,
            metalness: 0.7,
            roughness: 0.2
        });
        this.rod2 = new THREE.Mesh(rod2Geometry, rod2Material);
        this.rod2.castShadow = true;
        this.scene.add(this.rod2);

        // Second pendulum bob
        const bob2Geometry = new THREE.SphereGeometry(0.05, 32, 32);
        const bob2Material = new THREE.MeshStandardMaterial({
            color: 0x4CAF50,
            metalness: 0.8,
            roughness: 0.2
        });
        this.bob2 = new THREE.Mesh(bob2Geometry, bob2Material);
        this.bob2.castShadow = true;
        this.scene.add(this.bob2);

        // Trail visualization (optional - shows pendulum path)
        this.trailPoints = [];
        const trailGeometry = new THREE.BufferGeometry();
        const trailMaterial = new THREE.LineBasicMaterial({
            color: 0x4CAF50,
            opacity: 0.3,
            transparent: true
        });
        this.trail = new THREE.Line(trailGeometry, trailMaterial);
        this.scene.add(this.trail);

        this.updatePendulumGeometry();
    }

    setupControls() {
        // Orbit controls for camera
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.minDistance = 1;
        this.controls.maxDistance = 10;
        this.controls.maxPolarAngle = Math.PI / 2;
    }

    setupUI() {
        // Control panel already exists in HTML
        // Wire up event listeners

        // Simulation controls
        const startBtn = document.getElementById('start-sim');
        const stopBtn = document.getElementById('stop-sim');
        const resetBtn = document.getElementById('reset-sim');

        if (startBtn) startBtn.addEventListener('click', () => this.start());
        if (stopBtn) stopBtn.addEventListener('click', () => this.stop());
        if (resetBtn) resetBtn.addEventListener('click', () => this.reset());

        // Parameter sliders
        this.setupSlider('theta1-slider', 'theta1-value', -0.5, 0.5, 0.1, (val) => {
            this.state.theta1 = val;
            this.updatePendulumGeometry();
        });

        this.setupSlider('theta2-slider', 'theta2-value', -0.5, 0.5, 0.1, (val) => {
            this.state.theta2 = val;
            this.updatePendulumGeometry();
        });

        // Controller gain sliders
        ['k1', 'k2', 'k3', 'k4', 'k5', 'k6'].forEach(gain => {
            this.setupSlider(
                `${gain}-slider`,
                `${gain}-value`,
                0,
                30,
                this.gains[gain],
                (val) => { this.gains[gain] = val; }
            );
        });
    }

    setupSlider(sliderId, valueId, min, max, initial, callback) {
        const slider = document.getElementById(sliderId);
        const valueDisplay = document.getElementById(valueId);

        if (!slider || !valueDisplay) return;

        slider.min = min;
        slider.max = max;
        slider.step = (max - min) / 100;
        slider.value = initial;
        valueDisplay.textContent = initial.toFixed(2);

        slider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            valueDisplay.textContent = value.toFixed(2);
            callback(value);
        });
    }

    updatePendulumGeometry() {
        // Update cart position
        this.cart.position.set(this.state.x, 0.075, 0);

        // First pendulum joint position (top of cart)
        const joint1X = this.state.x;
        const joint1Y = 0.15;

        // First pendulum bob position
        const bob1X = joint1X + this.params.l1 * Math.sin(this.state.theta1);
        const bob1Y = joint1Y + this.params.l1 * Math.cos(this.state.theta1);

        // First rod position (center between joint and bob)
        this.rod1.position.set(
            (joint1X + bob1X) / 2,
            (joint1Y + bob1Y) / 2,
            0
        );
        this.rod1.rotation.z = -this.state.theta1;

        this.bob1.position.set(bob1X, bob1Y, 0);

        // Second pendulum bob position
        const bob2X = bob1X + this.params.l2 * Math.sin(this.state.theta2);
        const bob2Y = bob1Y + this.params.l2 * Math.cos(this.state.theta2);

        // Second rod position
        this.rod2.position.set(
            (bob1X + bob2X) / 2,
            (bob1Y + bob2Y) / 2,
            0
        );
        this.rod2.rotation.z = -this.state.theta2;

        this.bob2.position.set(bob2X, bob2Y, 0);

        // Update trail
        if (this.running && this.trailPoints.length < 500) {
            this.trailPoints.push(new THREE.Vector3(bob2X, bob2Y, 0));
            const positions = new Float32Array(this.trailPoints.length * 3);
            this.trailPoints.forEach((p, i) => {
                positions[i * 3] = p.x;
                positions[i * 3 + 1] = p.y;
                positions[i * 3 + 2] = p.z;
            });
            this.trail.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        }
    }

    computeControl() {
        // Simplified SMC control law: u = -K * [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]'
        const u = -(
            this.gains.k1 * this.state.x +
            this.gains.k2 * this.state.x_dot +
            this.gains.k3 * this.state.theta1 +
            this.gains.k4 * this.state.theta1_dot +
            this.gains.k5 * this.state.theta2 +
            this.gains.k6 * this.state.theta2_dot
        );

        // Saturation (limit control force)
        return Math.max(-50, Math.min(50, u));
    }

    updatePhysics() {
        // Simplified dynamics for browser performance
        // Full dynamics in Python code: src/core/dynamics.py

        const u = this.computeControl();
        const { m0, m1, m2, l1, l2, g } = this.params;
        const { x, theta1, theta2, x_dot, theta1_dot, theta2_dot } = this.state;

        // Simplified equations of motion (linearized around upright)
        // Real implementation uses full nonlinear dynamics

        const M = m0 + m1 + m2;

        // Accelerations (simplified)
        const x_ddot = (u - m1 * l1 * theta1_dot * theta1_dot * Math.sin(theta1)
                           - m2 * l2 * theta2_dot * theta2_dot * Math.sin(theta2)) / M;

        const theta1_ddot = (g * Math.sin(theta1) - x_ddot * Math.cos(theta1)) / l1;
        const theta2_ddot = (g * Math.sin(theta2) - x_ddot * Math.cos(theta2)) / l2;

        // Integrate (Euler method)
        this.state.x_dot += x_ddot * this.params.dt;
        this.state.theta1_dot += theta1_ddot * this.params.dt;
        this.state.theta2_dot += theta2_ddot * this.params.dt;

        this.state.x += this.state.x_dot * this.params.dt;
        this.state.theta1 += this.state.theta1_dot * this.params.dt;
        this.state.theta2 += this.state.theta2_dot * this.params.dt;

        // Boundary check (cart limits)
        if (Math.abs(this.state.x) > 2.0) {
            this.stop();
            console.log('Cart exceeded rail limits');
        }

        this.time += this.params.dt;
    }

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());

        if (this.running) {
            // Run multiple physics steps per frame for smoother simulation
            for (let i = 0; i < 2; i++) {
                this.updatePhysics();
            }
        }

        this.updatePendulumGeometry();
        this.controls.update();
        this.renderer.render(this.scene, this.camera);

        // Update stats display
        this.updateStats();
    }

    updateStats() {
        const timeDisplay = document.getElementById('sim-time');
        const theta1Display = document.getElementById('theta1-current');
        const theta2Display = document.getElementById('theta2-current');

        if (timeDisplay) timeDisplay.textContent = this.time.toFixed(2);
        if (theta1Display) theta1Display.textContent = (this.state.theta1 * 180 / Math.PI).toFixed(1);
        if (theta2Display) theta2Display.textContent = (this.state.theta2 * 180 / Math.PI).toFixed(1);
    }

    start() {
        this.running = true;
        console.log('Simulation started');
    }

    stop() {
        this.running = false;
        console.log('Simulation stopped');
    }

    reset() {
        this.stop();
        this.state = {
            x: 0,
            theta1: parseFloat(document.getElementById('theta1-slider')?.value || 0.1),
            theta2: parseFloat(document.getElementById('theta2-slider')?.value || 0.1),
            x_dot: 0,
            theta1_dot: 0,
            theta2_dot: 0
        };
        this.time = 0;
        this.trailPoints = [];
        this.trail.geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(0), 3));
        this.updatePendulumGeometry();
        console.log('Simulation reset');
    }

    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.renderer.dispose();
        this.container.removeChild(this.renderer.domElement);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('threejs-container')) {
        window.pendulumSim = new PendulumSimulator3D('threejs-container');
        console.log('3D Pendulum Simulator initialized');
    }
});
