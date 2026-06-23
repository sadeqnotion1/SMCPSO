# Episode 01 - The System Model: What We Are Actually Controlling

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 8-10 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: This episode is the foundation. Every number mentioned here is the exact value from the advisor report. If your advisor asks "where did that come from?" - this episode is your answer.]**

## Opening: What Is a Double-Inverted Pendulum?

Let's start with the most basic question: what exactly are we controlling here?

Picture a shopping cart. Now bolt a broomstick to the top of it, standing straight up. That broomstick is hinged at the base - it can swing forward and backward. Now attach a second broomstick to the top of the first one, also hinged. You have a cart that can move left and right, a lower pendulum that can swing, and an upper pendulum that can swing independently.

Your job: keep both broomsticks pointing straight up while the cart can slide around. You have exactly one control input - a horizontal force on the cart, up to 150 Newtons in either direction.

That is the Double-Inverted Pendulum, or DIP. And it is genuinely hard to control. The system is underactuated - you have one force but three things to manage simultaneously. It is naturally unstable - leave it alone for a fraction of a second and everything falls over. And the physics coupling both pendulums together is nonlinear in ways that make the math messy.

## The State Vector: Six Numbers That Describe Everything

Before we can write a single equation, we need to define what "the state of the system" means.

At any given moment, the DIP's state is completely described by six numbers:

- The cart's horizontal position, x
- The angle of the first pendulum from vertical, theta-one
- The angle of the second pendulum from vertical, theta-two
- The cart's velocity, x-dot
- The angular velocity of the first pendulum, theta-one-dot
- The angular velocity of the second pendulum, theta-two-dot

That is your state vector - six numbers, packed into a column vector. When all six are zero, both pendulums are perfectly upright and the cart is stationary. That is the equilibrium we are trying to maintain.

Why does this matter? Because every controller we build takes these six numbers as input and outputs a single force. The entire complexity of SMC, PSO tuning, and stability analysis reduces to: "given these six numbers right now, what force do I apply to the cart?"

## The Equations of Motion: Lagrangian Mechanics

Now for the physics. The equations of motion come from Lagrangian mechanics - the same formalism used to describe everything from planetary orbits to robot arms. The result for our system is:

M-of-q times q-double-dot, plus C-of-q-and-q-dot times q-dot, plus G-of-q, plus friction equals B times u.

Let me unpack that term by term.

**M-of-q is the inertia matrix.** It is a 3x3 symmetric matrix, and here is the critical detail: it depends on the current configuration q. As the pendulums swing, the effective inertia of the system changes. The report states this variation is 40 to 60 percent across the operating workspace. This is not a small perturbation - the system's inertia nearly doubles between configurations. You cannot design a controller that ignores this.

The key coupling term in M is the expression 2 times m2 times l1 times lc2 times cosine of theta-one minus theta-two. When the two pendulums are at similar angles, this coupling is large. When they are at different angles, it changes sign. This is what makes the double pendulum fundamentally harder than a single pendulum - the two pendulums are constantly pushing and pulling on each other through this coupling.

**C-of-q-and-q-dot is the Coriolis and centrifugal matrix.** These are the forces that arise from rotating reference frames - the same force that makes water spiral down a drain. In the DIP, these terms are proportional to angular velocities squared and cross-products of velocities. They are zero when everything is stationary, and they grow as the pendulums start swinging. There is also a small gyroscopic coupling term - coefficient 0.01 - added to capture cross-coupling between the pendulum angular velocities.

**G-of-q is the gravity vector.** Notice that G1 equals zero. That is not an approximation - it is exact. Gravity acts vertically, and the cart moves horizontally, so gravity does no work on the cart. The gravity terms for the two pendulums are minus the respective masses times gravity times the center-of-mass distance times sine of the angle. These are the restoring forces that always want to pull the pendulums back down.

**The friction model** is viscous plus Coulomb. Viscous friction is proportional to velocity - like dragging through honey. Coulomb friction is constant direction opposition to motion - like static friction. There is a dead zone at velocities smaller than ten-to-the-minus-six meters per second to avoid a mathematical singularity when the velocity sign function switches around zero.

## The Physical Parameters: Memorize These Numbers

The report provides 14 physical parameters in SI units. These are the exact values used in every simulation.

Cart mass: 1.5 kilograms. Link 1 mass: 0.2 kilograms. Link 2 mass: 0.15 kilograms. Link 1 length: 0.4 meters. Link 2 length: 0.3 meters. The center-of-mass distances are half the link lengths: 0.2 and 0.15 meters respectively. Moments of inertia: 0.0081 and 0.0034 kilogram-meters-squared. Gravity: 9.81 meters per second squared. Maximum control force: 150 Newtons. Control period: 0.01 seconds, meaning the controller runs at 100 Hz.

**[AUDIO NOTE: These numbers come up in advisor questions. The most common: "Why is G1 zero?" Answer: horizontal cart, vertical gravity - they are perpendicular. "How did you get the inertia values?" Answer: standard thin-rod formula, I equals one-twelfth m l-squared.]**

## Three Models: Choosing the Right Tool

The report documents three distinct mathematical models, each used for a different purpose.

**The simplified model** linearizes the equations around the upright equilibrium. It approximates sine of theta as theta, cosine of theta as 1, and scales down the coupling terms to between 0.7 and 0.8 of their full values. It also omits the gyroscopic effects. The result is 10 to 50 times faster to simulate. We use this exclusively for PSO optimization, where 40 particles each run 200 iterations of 10-second simulations. On the full nonlinear model, that would take more than 8 hours per controller. On the simplified model, it completes in minutes.

**The full nonlinear model** is what you have been hearing described. Complete Lagrangian, every coupling term, Coriolis, centrifugal, gyroscopic, and full friction. This is the model that appears in every benchmark result, every published figure, and every number in the Monte Carlo tables. When the report says STA settles in 1.82 seconds, that is measured on the full nonlinear model.

**The low-rank model** uses singular value decomposition to create a reduced-order approximation. It preserves the dominant dynamics while running faster than the full model. This is used in hardware-in-the-loop mode where real-time compute budget is limited.

The linearization for the simplified model is computed numerically via finite differences with epsilon equal to 10 to the minus 8. An analytical closed-form Jacobian was not used - the symbolic derivative of the full inertia matrix with all its coupling terms is unwieldy enough that numerical differentiation is the pragmatic choice.

## Takeaway

The system model is not a detail to be brushed over. The configuration-dependent inertia, the Coriolis coupling between pendulums, and the friction nonlinearities are what make this problem interesting and what make naive linear controllers fail. Every controller in this project was designed knowing this model exactly.

In the next episode, we will take this model and ask: given these equations, how do you design a sliding surface that makes stability analysis tractable?

---

*Report references: Section 1.1 through 1.4, Equations eq:state, eq:eom, eq:Mfull, eq:Cfull, eq:Gvec, eq:friction.*
