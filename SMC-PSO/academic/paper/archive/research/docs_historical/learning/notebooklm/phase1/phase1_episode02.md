# Phase 1 NotebookLM Podcast: Episode 2 - Your First Python Program

**Duration**: 22-24 minutes | **Learning Time**: 3 hours | **Difficulty**: Beginner

---

## Opening Hook

Imagine you're learning a new language - say, Spanish. You could spend months studying grammar rules and vocabulary lists before ever speaking a word. Or you could jump in, make mistakes, and start communicating right away. Which approach would help you learn faster?

Programming is the same. Today, we're not going to study Python theory. We're going to write actual code, see it run, and learn by doing. By the end of this episode, you'll have Python installed, you'll have written your first program, and you'll understand how to store and manipulate information using variables.

The magic moment when you type a command and the computer does exactly what you told it to? That's coming in the next twenty minutes.

---

## What You'll Discover

By listening to this episode, you'll learn:

- How to install Python 3.11 or higher on Windows, Mac, or Linux
- How to verify Python is working correctly
- What variables are and why they're fundamental to programming
- How Python handles different types of data (numbers, text, true/false)
- How to perform calculations and see results
- Your first Python program that actually does something useful

---

## Installing Python: Your Programming Foundation

Python is a programming language - a way to give instructions to computers using English-like commands instead of clicking buttons. It's particularly popular for scientific computing, data science, and control systems because it's powerful but relatively easy to learn.

Let's get it installed on your computer.

**Windows Installation**

First, go to python dot org forward slash downloads. That's the official Python website. You'll see a big yellow button that says "Download Python 3 dot 11 dot something" - whatever the latest version is. As long as it's 3.11 or higher, you're good. Click that button.

The installer downloads. When it finishes, run it. Here's the critical step that many beginners miss:

**Check the box that says "Add Python to PATH"**

This is at the bottom of the first installer screen. It's easy to overlook, but it's essential. PATH tells Windows where to find Python when you type "python" in the command line. Without this checkbox, Windows won't know what "python" means.

After checking that box, click "Install Now". The installer does its thing for a few minutes. When it finishes, you'll see "Setup was successful". Click Close.

Now let's verify it worked. Open Command Prompt:
- Press Windows key
- Type c-m-d
- Press Enter

In the command prompt, type:
python space dash dash version

Press Enter.

You should see something like:
Python 3 dot 11 dot 5

If you see that, congratulations! Python is installed and working. If you see an error like "python is not recognized", you probably missed the "Add to PATH" checkbox. You'll need to uninstall and reinstall, making sure to check that box.

**Mac Installation**

Mac comes with Python, but it's usually an old version - Python 2 dot 7, which is obsolete. We need Python 3 dot 11 or higher.

Go to python dot org forward slash downloads. Click the download button for Mac. You'll get a .pkg file - that's Mac's installer format.

Double-click the installer and follow the prompts. Mac will ask for your password since you're installing system-wide software. Enter it and continue.

When installation finishes, open Terminal:
- Press Command-Space
- Type "terminal"
- Press Enter

In Terminal, type:
python3 space dash dash version

Note that it's "python3" not just "python" on Mac. This is because Mac keeps the old Python 2 around for legacy software.

You should see:
Python 3 dot 11 dot something

If you do, you're ready to code!

**Linux Installation**

Most Linux distributions come with Python 3 pre-installed. Let's check what version you have.

Open Terminal (usually Ctrl-Alt-T) and type:
python3 space dash dash version

If you see 3 dot 11 or higher, you're all set. If you see 3 dot 9 or 3 dot 10, that might work for this project, but it's better to upgrade.

To install or upgrade on Ubuntu or Debian:

sudo space apt space update
sudo space apt space install space python3 space python3 dash pip

The "sudo" command means "super-user do" - run this command with administrator privileges. Linux will ask for your password.

After installation, verify again:
python3 space dash dash version

You should see a recent Python version.

---

## Your First Interaction with Python: The REPL

REPL stands for "Read, Eval, Print, Loop". It's an interactive environment where you type Python code, and Python immediately runs it and shows you the result.

Think of it like a conversation with the computer. You say something, it responds. You say something else, it responds again.

Let's start the REPL. Open your command line (Command Prompt on Windows, Terminal on Mac/Linux) and type:

Windows: python
Mac/Linux: python3

Press Enter.

Your prompt changes to three greater-than symbols:
greater-than greater-than greater-than

This is Python's prompt. It's waiting for you to type Python code.

**The Obligatory Hello World**

Every programming tutorial starts with "Hello, World!" - a program that displays that message. Let's do it.

Type:
print open-parenthesis double-quote Hello comma World! double-quote close-parenthesis

Press Enter.

You should see:
Hello, World!

Congratulations! You just wrote and ran your first Python program.

Let's break down what happened:
- **print** is a function that displays text
- **open-parenthesis** starts the list of things to give the function
- **double-quote** marks the beginning of text (a "string" in programming)
- **Hello, World!** is the actual text
- **double-quote** marks the end of the text
- **close-parenthesis** ends the list of things

So in full: print takes the text "Hello, World!" and displays it.

**Python as a Calculator**

Let's try some math. Type:
2 space plus space 3

Press Enter.

You see:
5

Python evaluated the expression and showed you the result. Try:
10 space asterisk space 5

The asterisk means "multiply". You see:
50

Try:
100 space forward-slash space 4

Forward-slash means "divide". You see:
25 dot 0

Notice it says "25.0" not "25". That's because division always returns a decimal number (a "float" in programming) even if the result is a whole number.

Try:
2 space asterisk asterisk space 8

Double-asterisk means "to the power of". Two to the power of eight equals:
256

Python is a calculator, but it's also so much more. Let's see how to remember values.

---

## Variables: Your Computer's Memory

Imagine you're doing a complex physics calculation. You compute the mass of the cart: 1.5 kilograms. Then you compute the length of the first pendulum: 0.8 meters. Then you use both values in a formula.

If you had to re-type "1.5" and "0.8" every time you needed them, you'd make typos and waste time. Variables solve this problem: they're named containers that store values.

In Python, creating a variable is simple. Still in the REPL, type:

mass space equals space 1 point 5

Press Enter.

Nothing prints, but something important happened. Python created a variable named "mass" and stored the value 1.5 in it.

To see what's in a variable, just type its name:

mass

Press Enter.

You see:
1 dot 5

Now create another variable:

length space equals space 0 point 8

Press Enter.

And use both variables in a calculation. Let's compute a simple energy value - don't worry about the physics, focus on the code:

energy space equals space mass space asterisk space 10 space asterisk space length

Press Enter.

Now check the result:

energy

Press Enter.

You see:
12 dot 0

Python took the value from "mass" (1.5), multiplied by 10, then multiplied by the value from "length" (0.8), and stored the result in "energy".

**Why Variables Matter**

Three reasons:

First, **clarity**. Reading "mass asterisk length" is much clearer than reading "1.5 asterisk 0.8". The code documents what it's doing.

Second, **reuse**. You can use the same variable many times without retyping the value.

Third, **flexibility**. If you want to try a different mass, you change one line - "mass equals 2.0" - and all calculations using that variable automatically update.

Variables are fundamental to every program you'll ever write.

---

## Data Types: Different Kinds of Information

Python handles different kinds of data differently. Let's explore the main types.

**Integers: Whole Numbers**

Type:
age space equals space 25

Press Enter.

Check its type:
type open-parenthesis age close-parenthesis

Press Enter.

You see:
less-than class quote int quote greater-than

"int" is short for "integer" - a whole number with no decimal point. Examples: 1, 100, negative 42, 0.

**Floats: Decimal Numbers**

Type:
height space equals space 1 point 75

Press Enter.

Check its type:
type open-parenthesis height close-parenthesis

Press Enter.

You see:
less-than class quote float quote greater-than

"float" is short for "floating-point number" - a number with a decimal point. Examples: 1.5, 3.14159, 0.001, negative 2.7.

**Strings: Text**

Type:
name space equals space double-quote Alice double-quote

Press Enter.

Check its type:
type open-parenthesis name close-parenthesis

Press Enter.

You see:
less-than class quote str quote greater-than

"str" is short for "string" - text data. Anything inside double-quotes (or single-quotes - Python accepts both) is a string. Examples: "Hello", "Python 3.11", "42" (notice this is text, not the number 42).

**Booleans: True or False**

Type:
is underscore student space equals space True

Press Enter.

Important: "True" has a capital T. Python is case-sensitive. "true" is not the same as "True".

Check its type:
type open-parenthesis is underscore student close-parenthesis

Press Enter.

You see:
less-than class quote bool quote greater-than

"bool" is short for "boolean" - a value that's either True or False. These are crucial for logic: "Is the pendulum upright? True or False. Is the cart within bounds? True or False."

---

## Recap: Core Concepts So Far

Let's pause and summarize what you've learned:

**Number one**: Python is a programming language that you can install on any computer. It's free, open-source, and widely used for scientific computing.

**Number two**: The REPL is an interactive environment where you type Python code and immediately see results. It's perfect for experimenting and learning.

**Number three**: Variables store values with names. You create them with equals signs: "mass equals 1.5". You use them by typing their names: "mass asterisk 10".

**Number four**: Python has different data types for different kinds of information:
- Integers (whole numbers): 25
- Floats (decimals): 1.75
- Strings (text): "Alice"
- Booleans (true/false): True, False

**Number five**: You can check a variable's type with the type function: "type open-parenthesis variable close-parenthesis".

Now let's write a slightly more complex program.

---

## Your First Python Script: Calculating Pendulum Period

So far, we've been working in the REPL - typing one line at a time. But most programs are scripts: files with multiple lines of code that run in sequence.

Let's create a Python script that calculates something relevant to our double-inverted pendulum project: the period of a simple pendulum.

The period is the time for one complete swing. For small angles, it's given by:
T equals 2 pi times the square root of quantity L over g

Where:
- T is the period in seconds
- L is the pendulum length in meters
- g is gravitational acceleration, 9.81 meters per second squared

**Exit the REPL**

First, we need to get out of the REPL. Type:
exit open-parenthesis close-parenthesis

Press Enter.

You're back to your normal command line prompt.

**Open VS Code**

Launch Visual Studio Code. If you haven't installed it yet, revisit Episode 1 for instructions. It's free at code dot visualstudio dot com.

**Create a New File**

Click File menu, then New File. Or press Ctrl-N (Windows/Linux) or Command-N (Mac).

**Type the Following Code**

I'll dictate this line by line, with explanations:

Line one: Import the math library
i-m-p-o-r-t space m-a-t-h

This gives us access to mathematical functions like square root and pi.

Line two: Blank line (for readability)

Line three: Define pendulum length
L space equals space 1 point 0

This creates a variable L for length, set to 1.0 meters.

Line four: Define gravitational acceleration
g space equals space 9 point 81

Gravity on Earth.

Line five: Blank line

Line six: Calculate period
T space equals space 2 space asterisk space m-a-t-h dot p-i space asterisk space m-a-t-h dot s-q-r-t open-parenthesis L space forward-slash space g close-parenthesis

Let's break this down:
- **2 asterisk math dot pi** - 2 times pi (pi comes from the math library we imported)
- **math dot sqrt** - square root function (also from math library)
- **open-parenthesis L forward-slash g close-parenthesis** - L divided by g, inside the square root

Line seven: Blank line

Line eight: Print the result
p-r-i-n-t open-parenthesis f-quote A pendulum of open-brace L close-brace meters has a period of open-brace T colon dot 2-f close-brace seconds double-quote close-parenthesis

This is an "f-string" - a string that can include variable values. The "f" before the quote means "formatted string". Inside the string:
- **open-brace L close-brace** - Insert the value of L
- **open-brace T colon dot 2-f close-brace** - Insert T, formatted to 2 decimal places

**Save the File**

Click File, then Save. Or press Ctrl-S (Windows/Linux) or Command-S (Mac).

Navigate to your coding-practice folder from Episode 1.

Save as: pendulum underscore period dot py

The ".py" extension tells your computer this is a Python file.

**Run Your Program**

Now comes the magic moment. Go to your command line and navigate to where you saved the file:

cd space Documents forward-slash coding-practice

Then run it:

Windows: python space pendulum underscore period dot py
Mac/Linux: python3 space pendulum underscore period dot py

Press Enter.

You should see:
A pendulum of 1 dot 0 meters has a period of 2 dot 01 seconds

You just wrote and ran your first Python program that performs a real calculation!

**Experiment with It**

Go back to VS Code. Change line three:
L space equals space 0 point 5

Save (Ctrl-S or Command-S). Run again:

python pendulum underscore period dot py

You see:
A pendulum of 0 dot 5 meters has a period of 1 dot 42 seconds

Shorter pendulum, shorter period. Change it to 2.0 meters and see what happens. This is how you experiment and learn - modify, run, observe, repeat.

---

## Understanding the Code: Line by Line

Let's revisit the program and understand every part:

**import math**

This brings in Python's math library, which includes:
- math dot pi (3.14159...)
- math dot sqrt (square root function)
- math dot sin, math dot cos (trigonometry)
- And dozens more

Without this import, typing "math dot pi" would cause an error.

**L equals 1 point 0**

This creates a variable L and assigns it the value 1.0. We could have used "length" instead of "L", but in physics, single-letter variables matching standard notation (L for length, g for gravity) make the code match the equations.

**g equals 9 point 81**

Gravitational acceleration. On the Moon, this would be about 1.6. On Jupiter, about 24.8. Changing this value would show you how pendulum periods differ on different planets.

**T equals 2 asterisk math dot pi asterisk math dot sqrt open-parenthesis L forward-slash g close-parenthesis**

This is the physics formula translated directly to Python. Notice how close it is to the mathematical notation:
- Math: T = 2π√(L/g)
- Python: T = 2 * math.pi * math.sqrt(L / g)

Python's syntax is designed to be readable.

**print open-parenthesis f-quote...close-parenthesis**

The f-string formats output nicely. Without it, we'd have to write:
print open-parenthesis "A pendulum of " plus str open-parenthesis L close-parenthesis plus " meters..." close-parenthesis

Much uglier. F-strings (added in Python 3.6) make string formatting clean and readable.

---

## Common Errors and How to Fix Them

Let's talk about errors you might encounter. In programming, errors are not failures - they're learning opportunities. Every programmer sees hundreds of errors per day. The skill is recognizing and fixing them quickly.

**Error Type One: NameError**

You run your program and see:
NameError colon name quote mass quote is not defined

This means you tried to use a variable that doesn't exist. Common causes:
- Typo: You defined "mass" but typed "Mass" (capital M)
- Order: You used "mass" before the line "mass equals 1.5"

Solution: Find where you defined the variable. Check spelling matches exactly. Make sure the definition comes before you use it.

**Error Type Two: SyntaxError**

You see:
SyntaxError colon invalid syntax

This means Python couldn't understand your code. Common causes:
- Missing colon: "if x greater-than 5" instead of "if x greater-than 5 colon"
- Missing parenthesis: "print 'hello'" instead of "print open-parenthesis 'hello' close-parenthesis"
- Mismatched quotes: "hello' instead of "hello" or 'hello'

Solution: Look at the line number in the error message. Check for missing colons, parentheses, and quote marks.

**Error Type Three: TypeError**

You see:
TypeError colon unsupported operand type

This means you tried to do an operation on incompatible types. Example:
result space equals space "5" space plus space 5

You can't add a string ("5") to a number (5). You need to convert:
result space equals space int open-parenthesis "5" close-parenthesis space plus space 5

Now both are numbers, so addition works.

**Error Type Four: IndentationError**

Python uses indentation (spaces at the start of lines) to group code. If indentation is wrong, you see:
IndentationError colon unexpected indent

Solution: Make sure lines that should be grouped have the same indentation (usually 4 spaces). We'll cover this more when we learn about functions and loops in the next episode.

---

## Why This Matters for Control Systems

You might be thinking: "I wanted to learn about sliding mode control and double-inverted pendulums. Why am I calculating pendulum periods?"

Here's why these foundational skills are critical:

**Reason One: Controllers are Functions**

A sliding mode controller is, at its core, a function that takes the current state (cart position, velocities, angles) and returns a control force. Writing that function requires understanding variables, data types, and math operations.

**Reason Two: Simulations are Scripts**

When you run a simulation, you're executing a Python script that:
- Loads configuration (reading variables)
- Initializes the system (setting up data structures)
- Runs a time loop (iteration we'll learn next episode)
- Calculates physics at each step (math operations like we just did)
- Saves results (writing to files)

Every line uses concepts from this episode.

**Reason Three: Debugging is Inevitable**

When (not if) something goes wrong, you'll need to:
- Read error messages and understand them
- Check variable values at different points
- Verify calculations are correct
- Test fixes and re-run

These skills build on Python fundamentals.

**Reason Four: Experimentation is Key**

Want to see how your controller behaves with different gains? You'll modify variables in config.yaml, which means understanding types and values. Want to plot custom metrics? You'll write Python code that stores data in variables and performs calculations.

The double-inverted pendulum is the exciting destination. Python skills are the vehicle that gets you there.

---

## Pronunciation Guide

Technical terms from this episode with phonetic pronunciations:

- **REPL**: "rep-ul" or just say the letters: "R-E-P-L" (Read-Eval-Print-Loop)
- **Variable**: VAIR-ee-uh-bul (a named container for data)
- **Integer**: IN-tuh-jer (whole number)
- **Float**: FLOHT (decimal number)
- **String**: STRING (text data)
- **Boolean**: BOO-lee-un (true/false value)
- **Import**: im-PORT (bring in a library)
- **f-string**: "f-string" or "formatted string"
- **Syntax**: SIN-tax (the rules of the language)
- **Indentation**: in-den-TAY-shun (spaces at the start of a line)

---

## What's Next: Control Flow and Loops

In Episode 3, we'll learn how to make programs that make decisions and repeat actions:

- **if/else statements**: "If the angle is greater than 0.5 radians, apply maximum force. Otherwise, use proportional control."
- **for loops**: "For each time step from 0 to 10 seconds, calculate the system state."
- **while loops**: "While the pendulum is not upright, keep adjusting."
- **Functions**: Group code into reusable chunks

These control flow structures are what turn simple calculations into intelligent, adaptive programs - like controllers that respond to changing conditions.

---

## Pause and Reflect

Before moving on, test your understanding:

1. How do you check what version of Python you have installed?
2. What's the difference between an integer and a float?
3. How do you create a variable that stores your name?
4. What does the "import math" line do?
5. Why is "print(hello)" different from "print('hello')"?

If you need to review any of these, go back to the relevant section. Mastery of basics makes advanced topics easier.

---

**Episode 2 of 11** | Phase 1: Foundations

**Previous**: [Episode 1: File Systems and Command Line](phase1_episode01.md) | **Next**: [Episode 3: Control Flow and First Real Program](phase1_episode03.md)
