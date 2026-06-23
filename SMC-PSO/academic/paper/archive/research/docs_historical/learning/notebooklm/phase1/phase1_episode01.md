# Phase 1 NotebookLM Podcast: Episode 1 - Your Computer as a Filing Cabinet

**Duration**: 18-20 minutes | **Learning Time**: 2 hours | **Difficulty**: Beginner

---

## Opening Hook

Picture yourself in a massive library with millions of books, but there's no Dewey Decimal System, no card catalog, and no signs telling you where anything is. That's what your computer would be like without understanding file systems and directories. Every time you save a document, take a screenshot, or download a file, your computer is organizing it somewhere - but where?

By the end of this episode, you'll understand how your computer stores files, how to navigate using the command line, and why these skills are essential for programming and control systems engineering. You'll never feel lost in your own computer again.

---

## What You'll Discover

By listening to this episode, you'll learn:

- How computers organize files using hierarchies (drives, folders, files)
- The difference between absolute and relative paths
- How to navigate your computer using text commands instead of clicking
- Why programmers prefer the command line for many tasks
- Platform differences between Windows, Mac, and Linux

---

## Your Computer: The Filing Cabinet Analogy

Let's start with a mental model that makes everything click. Imagine walking up to a large filing cabinet in an office.

**The filing cabinet has multiple drawers** - maybe four or five of them, each labeled. On Windows, these are your drives: C colon, D colon, maybe E colon if you have an external hard drive. On Mac or Linux, you have your root directory, which we say as "slash" or "forward slash".

Now open one of those drawers. Inside, you see hanging folders - maybe labeled "Projects", "Personal", "Photos", "Downloads". In computer terms, these are your directories or folders. The terms are interchangeable - directory is the older, more technical term, while folder is what most people say today.

Within each hanging folder, you might have manila folders creating sub-categories. "Projects" might contain "Work Projects" and "Personal Projects". "Photos" might contain "2024" and "2025". This nesting can go as deep as you want - folders within folders within folders.

Finally, inside those manila folders are the actual documents - your files. A Word document, a photo, a Python script. These are the individual pieces of content you're storing.

This hierarchy - drive, folders, subfolders, files - is how every computer organizes data. Whether you're using Windows, Mac, Linux, or even your smartphone, this same structure applies. And once you understand it, you can navigate any system.

---

## File Paths: Addresses for Your Files

Now let's talk about how to describe the location of a file. When you tell someone how to find you in a building, you might say "Third floor, Room 305". File paths work the same way - they're addresses that tell the computer exactly where to find something.

**Absolute Paths: The Full Address**

An absolute path is like giving someone your complete mailing address. It starts from the very top of the file system and works its way down to the specific file.

On Windows, an absolute path looks like this:
C colon backslash Users backslash YourName backslash Documents backslash project backslash code dot py

Let's break that down phonetically:
- **C colon** - That's the drive letter followed by a colon
- **backslash Users** - First folder level
- **backslash YourName** - Your user account folder
- **backslash Documents** - The Documents folder
- **backslash project** - A folder you created
- **backslash code dot py** - The actual Python file

On Mac or Linux, absolute paths look slightly different:
forward slash home forward slash yourname forward slash Documents forward slash project forward slash code dot py

The key difference: Windows uses backslashes and drive letters. Mac and Linux use forward slashes and no drive letters - everything starts from the root directory, which is just a single forward slash.

**Relative Paths: The Shortcut**

Relative paths are like giving directions from where you currently are. If you're already standing in the Documents folder, you don't need to say "Go to drive C, then Users, then YourName, then Documents". You can just say "Go to the project folder".

A relative path looks like this:
project forward slash code dot py

This means: "From where I am right now, go into the project folder and find code dot py."

There's a special shortcut: two dots, which we say as "dot dot". This means "go up one level" or "go to the parent folder". If you're in:
C colon backslash Users backslash YourName backslash Documents backslash project

And you want to go to Documents, you can just say:
cd space dot dot

That takes you up one level to the parent directory.

**Why This Matters for Programming**

When you're writing code, you'll constantly be telling your program where to find files. "Open this data file." "Save the results here." "Load that configuration." Understanding paths makes this natural instead of confusing.

---

## The Command Line: Talking to Your Computer in Text

Here's where things get really powerful. Up until now, you've probably been clicking on folders and files to navigate your computer. But there's another way - a way that's faster once you learn it, and essential for programming and automation.

The command line is a text interface where you type commands to control your computer. On Windows, it's called Command Prompt or PowerShell. On Mac and Linux, it's called Terminal. They all do the same basic job: let you control your computer by typing instead of clicking.

**Why would programmers prefer typing over clicking?**

Three reasons:

First, **speed**. Once you know the commands, typing "cd Documents" is faster than opening File Explorer, scrolling to Documents, and double-clicking it.

Second, **automation**. You can write scripts - sequences of commands that run automatically. You can't script clicking on icons.

Third, **remote access**. When you're connecting to another computer (like a server or Raspberry Pi running your control system), you often only have text access. No mouse, no clicking, just commands.

Let's learn the essential commands.

---

## Essential Command Line Navigation (Windows)

Open Command Prompt on Windows by pressing Windows key, typing "cmd" (c-m-d), and hitting Enter.

You'll see something like:
C colon backslash Users backslash YourName greater-than

That's your prompt. It shows your current location and waits for a command.

**Command number one: cd**

C-D stands for "Change Directory". This is how you move between folders.

Type: c-d space Documents
Then press Enter.

Your prompt changes to:
C colon backslash Users backslash YourName backslash Documents greater-than

You've just navigated into your Documents folder without touching your mouse.

Want to go back up? Type: c-d space dot dot

**Command number two: dir**

D-I-R stands for "Directory". This shows you what's inside your current folder.

Type: d-i-r
Press Enter.

You'll see a list of files and folders in your current location, with details like size and date modified. It's like opening a folder in File Explorer, but as text.

**Command number three: mkdir**

M-K-D-I-R stands for "Make Directory". This creates a new folder.

Type: m-k-d-i-r coding-practice
Press Enter.

You've just created a folder called "coding dash practice" in your current location.

**Command number four: cd to go into it**

Type: c-d space coding-practice
Press Enter.

Now you're inside your new folder. Your prompt shows:
C colon backslash Users backslash YourName backslash Documents backslash coding-practice greater-than

**Command number five: cls**

C-L-S stands for "Clear Screen". If your terminal gets cluttered with old commands and output, this wipes it clean.

Type: c-l-s
Press Enter.

Screen cleared! Your prompt is back at the top.

---

## Essential Command Line Navigation (Mac and Linux)

If you're on Mac or Linux, the commands are slightly different but the concepts are identical.

Open Terminal on Mac by pressing Command-Space, typing "terminal", and hitting Enter. On Linux, it's usually Ctrl-Alt-T.

**pwd: Print Working Directory**

Type: p-w-d
Press Enter.

This shows your current location. Maybe:
forward slash home forward slash yourname

That's where you are right now.

**ls: List**

L-S stands for "List". This is like Windows' dir command.

Type: l-s
Press Enter.

You see all files and folders in your current directory.

Want more details? Type: l-s space dash l-a

That's "list" with two flags: dash L for "long format" (shows permissions, size, date) and dash A for "all" (includes hidden files).

**cd: Change Directory**

Same as Windows!

Type: c-d space Documents
Press Enter.

You're now in Documents.

**mkdir: Make Directory**

Also the same as Windows!

Type: m-k-d-i-r space coding-practice
Press Enter.

New folder created.

**clear: Clear Screen**

On Unix systems, the command to clear the screen is "clear" (not "cls" like Windows).

Type: c-l-e-a-r
Press Enter.

Screen cleared!

---

## Practical Exercise: Navigate Your Computer

Let's put this together. Pause here if you want to follow along on your own computer.

Your mission: Create a folder structure for organizing a project.

**Step one**: Open your command line (Command Prompt on Windows, Terminal on Mac/Linux)

**Step two**: Navigate to your Documents folder
- Windows: c-d space Documents
- Mac/Linux: c-d space Documents

**Step three**: Create a project folder
- mkdir space dip-project-practice

**Step four**: Go into that folder
- cd space dip-project-practice

**Step five**: Create three subfolders
- mkdir space code
- mkdir space data
- mkdir space results

**Step six**: List what you created
- Windows: dir
- Mac/Linux: ls

You should see three folders: code, data, results.

**Step seven**: Go into the code folder
- cd space code

**Step eight**: Check where you are
- Windows: cd (just "cd" with no arguments shows current location)
- Mac/Linux: pwd

You should see something like:
C colon backslash Users backslash YourName backslash Documents backslash dip-project-practice backslash code

Or on Mac/Linux:
forward slash home forward slash yourname forward slash Documents forward slash dip-project-practice forward slash code

Congratulations! You've just navigated your computer entirely with text commands.

---

## Key Takeaways: What You've Learned So Far

Let's recap the core concepts from the first half of this episode:

**Number one**: Your computer organizes files in a hierarchy - drives contain folders, folders contain subfolders, subfolders contain files. This is true across all operating systems.

**Number two**: An absolute path is a complete address from the drive root to the file. A relative path is a shortcut from your current location.

**Number three**: The command line is a text interface for controlling your computer. It's faster for many tasks and essential for programming.

**Number four**: Basic navigation commands differ slightly between Windows and Unix, but the concepts are the same:
- Move between folders: cd
- See what's here: dir (Windows) or ls (Unix)
- Create a folder: mkdir
- Go up one level: cd dot dot
- Clear screen: cls (Windows) or clear (Unix)

Now let's talk about where you'll be writing your code.

---

## Text Editors: Your Code Workshop

You can't write code in Microsoft Word or Google Docs. Those are word processors designed for formatted documents - bold text, different fonts, images. Code needs to be plain text with no formatting.

That's what a text editor does: edit plain text files. Every character you type is exactly what's saved. No hidden formatting, no style rules, just raw text.

**Why not just use Notepad?**

Technically, you could. But dedicated code editors have features that make programming much easier:

- **Syntax highlighting**: Python keywords appear in different colors, making code easier to read
- **Auto-indentation**: Code blocks automatically indent correctly
- **Error detection**: The editor can flag obvious mistakes before you even run the code
- **Extensions**: Add support for new languages, tools, and workflows

Think of it like this: you could chop vegetables with a butter knife, but a chef's knife makes the job faster, easier, and safer. Code editors are chef's knives for programming.

---

## Recommended Editors for Beginners

**Visual Studio Code (VS Code)**

This is the most popular code editor today, and for good reason. It's free, works on Windows, Mac, and Linux, and has thousands of extensions.

To install VS Code:
1. Go to code dot visualstudio dot com
2. Download the installer for your operating system
3. Run the installer with default settings
4. Launch VS Code

When you first open it, you'll see a welcome screen with tutorials. You don't need to watch them all right now - we'll learn by doing.

**Key Features**:
- **File explorer on the left**: Shows your project folder structure
- **Editor in the middle**: Where you write code
- **Terminal at the bottom**: Built-in command line (no need to switch windows!)
- **Extensions panel**: Add Python support, themes, linters, formatters

**Other Options**

If VS Code feels too heavy or complex, consider:

**Sublime Text**: Minimal interface, very fast startup, free trial (nag screen to buy license). Great for quick edits.

**Notepad plus plus (Windows only)**: Lightweight, fast, good syntax highlighting. Free and open source.

**Vim (Unix systems)**: Terminal-based, steep learning curve, but incredibly powerful once mastered. Already installed on Mac and Linux.

For this beginner roadmap, we'll assume you're using VS Code since it's the most popular and beginner-friendly.

---

## Your First Text File: Hello World

Let's create your first code file. This won't be Python yet - just a simple text file to get comfortable with the editor.

**Open VS Code**

**Create a new file**:
- Click File menu, then New File
- Or press Ctrl-N (Windows/Linux) or Command-N (Mac)

**Type this**:
```
Hello, I'm learning to code!
Today I learned about:
- File systems and directories
- Absolute vs relative paths
- Command line navigation
- Text editors

Next up: Python programming!
```

**Save the file**:
- Click File menu, then Save As
- Or press Ctrl-S (Windows/Linux) or Command-S (Mac)

**Navigate to your coding-practice folder**:
Remember the folder we created earlier? Find it:
- Windows: C colon backslash Users backslash YourName backslash Documents backslash coding-practice
- Mac/Linux: forward slash home forward slash yourname forward slash Documents forward slash coding-practice

**Save as**: hello dot txt

**Verify it worked**:
Go back to your command line, navigate to that folder:
- cd space Documents forward slash coding-practice

List the files:
- Windows: dir
- Mac/Linux: ls

You should see hello dot txt.

View the file contents from command line:
- Windows: type space hello dot txt
- Mac/Linux: cat space hello dot txt

You should see your message printed in the terminal!

---

## Why This Matters for Control Systems

You might be wondering: "I just want to control a double-inverted pendulum. Why am I learning about file systems and text editors?"

Here's why:

**Reason one: Project Organization**

The DIP-SMC-PSO project has hundreds of files organized in a specific structure:
- src folder contains source code
- tests folder contains test code
- docs folder contains documentation
- config dot yaml contains configuration settings

Without understanding folders and paths, you'd be lost trying to find anything.

**Reason two: Running Simulations**

To run a simulation, you'll open a command line, navigate to the project folder, and type:
python space simulate dot py space dash dash ctrl space classical underscore smc space dash dash plot

Every word in that command assumes you understand: paths, commands, arguments, flags. Now you do.

**Reason three: Editing Code**

When you want to modify controller gains or experiment with parameters, you'll open the source code in a text editor, make changes, save, and re-run. This workflow is how all programming happens.

**Reason four: Debugging**

When something goes wrong (and it will - that's normal), error messages will reference file paths and line numbers:
File "C colon backslash Projects backslash dip-smc-pso backslash src backslash controllers backslash classical underscore smc dot py", line 87

Understanding paths means you can quickly find that file and line to fix the problem.

These foundational skills are like learning to hold a pencil before learning to write. They seem basic, but they enable everything that comes next.

---

## Common Pitfalls and How to Avoid Them

Before we wrap up, let's address five mistakes that trip up beginners:

**Pitfall one: Spaces in paths**

If a folder name has spaces, like "My Projects", the command line gets confused:
cd My Projects  <-- This tries to cd into "My" and then run a command called "Projects"

Solution: Use quotes:
cd space "My Projects"

Or avoid spaces in folder names entirely. Use hyphens or underscores:
my-projects or my_projects

**Pitfall two: Confusing slashes**

Windows uses backslashes: C colon backslash Users
Unix uses forward slashes: forward slash home

But Python code uses forward slashes even on Windows! The language handles the conversion.

When typing paths in the command line, use the right slash for your system. When writing Python code, use forward slashes.

**Pitfall three: Not knowing where you are**

Lost in the file system? Run:
- Windows: cd (no arguments)
- Mac/Linux: pwd

This shows your current location.

**Pitfall four: Typos in commands**

Command line is unforgiving. "CD" might work, but "c d" (with a space) won't. "dir1" is not "dir". There's no autocorrect.

Solution: Use Tab completion! Type the first few letters of a file or folder name, then press Tab. The command line fills in the rest.

Example: Type "cd Doc" then press Tab. It autocompletes to "cd Documents".

**Pitfall five: Editing code in Word**

We mentioned this before, but it's worth repeating: NEVER edit code in Microsoft Word, Google Docs, or any word processor. They add hidden formatting characters that break code.

Always use a text editor: VS Code, Sublime, Notepad++, Vim.

---

## Pronunciation Guide

Here are the technical terms from this episode with phonetic pronunciations:

- **Directory**: dih-REKT-or-ee (not "direct tree")
- **Absolute**: AB-suh-loot (complete path)
- **Relative**: REL-uh-tiv (shortcut path)
- **cd**: Just say the letters: "c-d" or "see dee"
- **mkdir**: "make dir" or "m-k-dir"
- **pwd**: "p-w-d" or "pee double-you dee" (print working directory)
- **Visual Studio Code**: "visual studio code" or just "VS code"
- **Sublime**: suh-BLIME (not "sub-lime")
- **CLI**: "c-l-i" (command line interface)

---

## What's Next: Python Programming

In the next episode, we'll take these foundational skills and start writing actual Python code. You'll learn:

- How to install Python and verify it works
- Variables: storing information
- Data types: numbers, text, true/false
- Basic operators: math and logic
- Your first Python program beyond "Hello World"

By the end of Episode 2, you'll be writing code that calculates, makes decisions, and prints results. The building blocks of any program.

---

## Pause and Reflect

Before moving on, try to answer these questions without looking back:

1. What's the difference between an absolute path and a relative path?
2. How do you move up one directory level from the command line?
3. Why do programmers use text editors instead of word processors?
4. What command shows your current location on Mac/Linux?
5. What's one advantage of the command line over clicking?

If you struggled with any of these, go back and review that section. There's no rush - understanding beats speed every time.

---

**Episode 1 of 11** | Phase 1: Foundations

**Previous**: [Phase 1 Overview](../beginner-roadmap/phase-1-foundations.md) | **Next**: [Episode 2: Python Installation and First Program](phase1_episode02.md)
