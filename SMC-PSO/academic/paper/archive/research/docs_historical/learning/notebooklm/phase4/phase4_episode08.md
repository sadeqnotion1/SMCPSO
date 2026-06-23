# Phase 4 NotebookLM Podcast: Episode 8 - Classical SMC - Control Law Implementation

**Duration**: 10-12 minutes | **Learning Time**: 2.5 hours | **Difficulty**: Intermediate-Advanced

---

## Opening Hook

You've seen how Classical S-M-C initializes: validating gains, unpacking them into meaningful names, and storing parameters. Now comes the main event: the compute underscore control method. This is where theory becomes code, where mathematical equations turn into numerical operations that run sixty times per second to keep pendulums balanced.

Think of this like watching a chef cook. You know the ingredients (gains, state), you know the recipe (control law), and now you'll see the actual technique: how to extract state variables, compute sliding surfaces, combine equivalent and switching control, and apply saturation.

By the end of this episode, you'll understand every line of the control law implementation.

## What You'll Discover

In this episode, you'll learn:
- How the compute underscore control method signature matches the interface
- State extraction: unpacking the 6-element state vector into named variables
- Sliding surface definition: s1 equals theta1 plus k1 times theta1 underscore dot
- Equivalent control: stabilizes cart position and velocity
- Switching control: drives sliding variables to zero using tanh
- Saturation: n-p dot clip enforces actuator limits
- History tracking: storing control outputs for analysis

## The Method Signature

Open source slash controllers slash classical underscore s-m-c dot p-y and find the compute underscore control method:

```
def compute underscore control open-paren self comma state colon n-p dot n-d-array comma d-t colon float close-paren arrow float colon
```

**Breaking down the signature:**

**def compute underscore control**: Defines the method.

**self**: The controller instance. Python passes this automatically when you call controller dot compute underscore control.

**state colon n-p dot n-d-array**: The system state as a NumPy array. Type hint indicates it's an n-d-array.

**d-t colon float**: The timestep in seconds. Classical S-M-C doesn't actually use this, but it's required by the interface for compatibility with time-dependent controllers.

**arrow float**: The method returns a single floating-point number: the control force F in Newtons.

**colon**: Marks the beginning of the method body.

**Why this signature?**

Because it matches ControllerInterface's abstract method. Every controller has the same signature, enabling polymorphism. The simulation runner can call compute underscore control on any controller without knowing its type.

## The Docstring

Inside the method, there's a docstring:

```
triple-quote
Compute control force using classical S-M-C law period

Args colon
    state colon open-bracket x comma x underscore dot comma theta1 comma theta1 underscore dot comma theta2 comma theta2 underscore dot close-bracket
    d-t colon Timestep in seconds open-paren not used in classical S-M-C comma but required by interface close-paren

Returns colon
    Control force F in Newtons open-paren saturated to limits close-paren
triple-quote
```

**What this tells us:**

**Purpose**: Compute the control force using Classical S-M-C.

**State breakdown**: The 6-element state vector contains:
1. x: cart position in meters
2. x underscore dot: cart velocity in meters per second
3. theta1: first pendulum angle in radians
4. theta1 underscore dot: first pendulum angular velocity in radians per second
5. theta2: second pendulum angle in radians
6. theta2 underscore dot: second pendulum angular velocity in radians per second

**d-t note**: Classical S-M-C doesn't use timestep, but the interface requires it.

**Return value**: Control force in Newtons, saturated to limits.

## Step 1: Extract State Variables

The first block of code extracts state variables:

```
# 1 period Extract state variables
x equals state open-bracket 0 close-bracket          # Cart position in meters
x underscore dot equals state open-bracket 1 close-bracket      # Cart velocity in meters per second
theta1 equals state open-bracket 2 close-bracket     # Pendulum 1 angle in radians
theta1 underscore dot equals state open-bracket 3 close-bracket # Pendulum 1 angular velocity in radians per second
theta2 equals state open-bracket 4 close-bracket     # Pendulum 2 angle in radians
theta2 underscore dot equals state open-bracket 5 close-bracket # Pendulum 2 angular velocity in radians per second
```

**What's happening?**

Each line assigns one element of the state array to a named variable. state open-bracket 0 close-bracket is the cart position, state open-bracket 1 close-bracket is the cart velocity, and so on.

**Why extract instead of using indices?**

Compare these two approaches:

**Approach 1: Using indices (confusing)**

```
s1 equals state open-bracket 2 close-bracket plus self dot k1 times state open-bracket 3 close-bracket
```

**Approach 2: Using named variables (clear)**

```
s1 equals theta1 plus self dot k1 times theta1 underscore dot
```

The second version is self-documenting. You immediately understand that s1 is a function of theta1 and theta1 underscore dot.

**This is the principle of readable code**: future developers, including future you, should understand what's happening without decoding indices.

## Step 2: Define Sliding Surfaces

Next, the sliding surfaces are computed:

```
# 2 period Define sliding surfaces
# Sliding surface forces theta plus k times theta underscore dot arrow 0
s1 equals theta1 plus self dot k1 times theta1 underscore dot  # Pendulum 1 sliding variable
s2 equals theta2 plus self dot k2 times theta2 underscore dot  # Pendulum 2 sliding variable
```

**What's happening?**

**s1 equals theta1 plus self dot k1 times theta1 underscore dot**: Computes the first sliding surface variable.

**s2 equals theta2 plus self dot k2 times theta2 underscore dot**: Computes the second sliding surface variable.

**What does this mean mathematically?**

The sliding surface is defined as:

s equals theta plus k times theta underscore dot equals 0

This is a line in the phase space (theta, theta underscore dot plane). When s equals 0, the system is on the sliding surface.

**Why this particular form?**

Because on the sliding surface, s equals 0, so:

theta equals negative k times theta underscore dot

This is a first-order stable system. If theta is positive, theta underscore dot is negative, driving theta back toward zero. The gain k controls the convergence rate.

**Larger k**: Faster convergence, but more aggressive control.
**Smaller k**: Slower convergence, but smoother control.

## Recap: Core Concepts So Far

Let's recap what we've covered.

**Method Signature**: Matches ControllerInterface's abstract method. Takes state and d-t, returns float.

**State Extraction**: Unpacks the 6-element state array into named variables for readability.

**Sliding Surfaces**: s1 and s2 are combinations of angle and angular velocity. When s equals 0, the system converges exponentially.

## Step 3: Equivalent Control

Next comes the equivalent control term:

```
# 3 period Equivalent control open-paren stabilizes cart position close-paren
u underscore eq equals negative open-paren self dot k3 times x plus self dot k4 times x underscore dot close-paren
```

**What's happening?**

**u underscore eq**: The equivalent control term.

**negative open-paren self dot k3 times x plus self dot k4 times x underscore dot close-paren**: Computes a linear combination of cart position and velocity, then negates it.

**What does equivalent control do?**

It stabilizes the cart's position. Think of it as proportional-derivative or P-D control for the cart:
- If x is positive (cart too far right), k3 times x is positive, so negative k3 times x pushes the cart left.
- If x underscore dot is positive (cart moving right), k4 times x underscore dot is positive, so negative k4 times x underscore dot slows it down.

**Why is it called "equivalent" control?**

In sliding mode control theory, equivalent control is the continuous control that would keep the system on the sliding surface if there were no disturbances. It's the "ideal" control assuming perfect model knowledge.

In practice, disturbances and model errors exist, so we add switching control to drive the system back to the sliding surface.

## Step 4: Switching Control

Now comes the switching control term:

```
# 4 period Switching control open-paren drives sliding variables to zero close-paren
# Uses tanh open-paren smooth approximation close-paren instead of sign open-paren discontinuous close-paren
combined underscore s equals s1 plus self dot k5 times s2  # Combine sliding surfaces
u underscore sw equals negative self dot eta times n-p dot tanh open-paren combined underscore s slash self dot boundary underscore layer close-paren
```

**What's happening?**

**combined underscore s equals s1 plus self dot k5 times s2**: Combines the two sliding surfaces with coupling gain k5.

**u underscore sw equals negative self dot eta times n-p dot tanh open-paren combined underscore s slash self dot boundary underscore layer close-paren**: Computes switching control using the hyperbolic tangent function.

**Breaking down the switching control:**

**combined underscore s slash self dot boundary underscore layer**: Scales the combined sliding variable by the boundary layer width.

**n-p dot tanh open-paren ... close-paren**: Applies the hyperbolic tangent function. tanh is a smooth approximation of the sign function:
- tanh of large positive values approaches 1
- tanh of large negative values approaches negative 1
- tanh of zero equals zero

**negative self dot eta times ...**: Multiplies by the switching gain eta and negates.

**Why tanh instead of sign?**

The classic S-M-C control law uses the sign function:

u underscore sw equals negative eta times sign open-paren combined underscore s close-paren

But sign is discontinuous. It jumps from negative 1 to positive 1 instantly as combined underscore s crosses zero. This causes chattering: rapid oscillations in the control output.

tanh is smooth. It transitions gradually from negative 1 to positive 1, reducing chattering while maintaining robustness.

**What does the boundary layer do?**

The boundary layer width controls how "sharp" the tanh transition is:
- Small boundary layer: tanh approximates sign closely. Faster convergence, more chattering.
- Large boundary layer: tanh is smoother. Less chattering, slower convergence.

It's a trade-off parameter you tune based on your priorities.

## Step 5: Total Control

The total control is the sum of equivalent and switching control:

```
# 5 period Total control equals equivalent plus switching
F equals u underscore eq plus u underscore sw
```

**Why add them?**

**Equivalent control** stabilizes the cart's position and velocity.

**Switching control** drives the pendulums toward the sliding surface, which in turn drives the angles toward zero.

Together, they stabilize the entire system: cart position, pendulum 1 angle, and pendulum 2 angle.

## Step 6: Apply Saturation

Real actuators have limits. You can't apply infinite force. The next step enforces saturation:

```
# 6 period Apply saturation open-paren physical actuator limits close-paren
F equals n-p dot clip open-paren F comma self dot sat underscore min comma self dot sat underscore max close-paren
```

**What's happening?**

**n-p dot clip open-paren F comma self dot sat underscore min comma self dot sat underscore max close-paren**: Clamps F to the range open-bracket sat underscore min comma sat underscore max close-bracket.

If F is less than sat underscore min (default negative 20 dot 0), it's set to sat underscore min.
If F is greater than sat underscore max (default positive 20 dot 0), it's set to sat underscore max.
Otherwise, F remains unchanged.

**Why is saturation necessary?**

Because physical actuators have force limits. A motor can't produce infinite torque. Without saturation, the control law might command 1000 Newtons, but the actuator can only provide 20 Newtons. Saturation makes the control law realistic.

**Does saturation affect stability?**

In theory, yes. Saturation can degrade performance or even cause instability if the gains are poorly tuned. But for well-tuned gains, saturation rarely activates except during large disturbances, so stability is maintained.

## Step 7: Store for History and Debugging

Finally, the control output is stored:

```
# 7 period Store for history slash debugging
self dot last underscore control equals F
self dot history dot append open-paren F close-paren

return F
```

**What's happening?**

**self dot last underscore control equals F**: Stores the current control output. Some controllers use this for derivative or filtering calculations.

**self dot history dot append open-paren F close-paren**: Adds F to the history list. After simulation, you can plot self dot history to visualize control effort over time.

**return F**: Returns the control force to the simulation runner.

**Why store history?**

For analysis and plotting. You can compare different controllers by plotting their control histories and seeing which ones are smoother or more aggressive.

## Recap: Complete Control Law

Let's recap the entire compute underscore control method.

**Step 1: Extract state variables** into named variables for readability.

**Step 2: Define sliding surfaces** s1 and s2 as combinations of angle and angular velocity.

**Step 3: Compute equivalent control** to stabilize cart position and velocity.

**Step 4: Compute switching control** using tanh to drive sliding variables to zero while reducing chattering.

**Step 5: Sum equivalent and switching control** to get total control F.

**Step 6: Apply saturation** to enforce physical actuator limits.

**Step 7: Store control output** in last underscore control and history, then return F.

**This is Classical S-M-C in action**: a robust, nonlinear control law that balances pendulums despite disturbances and model uncertainties.

## Pronunciation Guide

Here are the technical terms from this episode with phonetic pronunciations:

- u underscore eq: "u-equivalent" or "u-e-q"
- u underscore sw: "u-switching" or "u-s-w"
- tanh: "tanch" or "hyperbolic tangent" (rhymes with "branch")
- n-p dot clip: "NumPy dot clip"
- sign: "sign" (signum function)
- P-D: "P-D" (proportional-derivative control)
- chattering: "chattering" (rapid oscillations)
- saturation: "saturation" (clamping to limits)

## What's Next

In Episode 9, we'll dive deeper into the mathematics behind the control law. You'll understand why the sliding surface is defined as s equals theta plus k times theta underscore dot, what equivalent control means theoretically, how the boundary layer trades off chattering versus convergence, and why helper methods like reset and get underscore gains exist.

Here's a preview question: What happens on the sliding surface? How does the system behave when s equals 0? We'll answer this with phase space analysis next episode.

## Pause and Reflect

Before moving to Episode 9, ask yourself these questions:

1. What are the six state variables, and what do they represent?
2. How are sliding surfaces s1 and s2 defined?
3. What does equivalent control stabilize?
4. Why use tanh instead of the sign function?
5. What does n-p dot clip do, and why is saturation necessary?

If you can answer these confidently, you're ready to proceed. If anything is unclear, open classical underscore s-m-c dot p-y and trace through the compute underscore control method line by line, annotating what each operation does.

**Excellent progress! You've decoded the control law. Let's continue!**

---

**Episode 8 of 13** | Phase 4: Advancing Skills

**Previous**: [Episode 7 - Classical SMC - Imports and Initialization](phase4_episode07.md) | **Next**: [Episode 9 - Classical SMC - Math Breakdown](phase4_episode09.md)
