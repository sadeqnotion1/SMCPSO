# E016: Attribution and Citations

**Hosts**: Dr. Sarah Chen (Control Systems) & Alex Rivera (Software Engineering)

---

## Opening Hook

**Sarah**: Academic integrity question: You implement PSO based on Kennedy & Eberhart's 1995 paper. Do you cite it?

**Alex**: Absolutely! Even if you wrote the code from scratch, the ALGORITHM isn't yours.

**Sarah**: You use the Slotine & Li textbook's derivation of SMC stability. Do you cite it?

**Alex**: Yes! Ideas have authors.

**Sarah**: But here's the tricky one: You use NumPy for matrix operations. Do you cite NumPy?

**Alex**: For a software project? Include it in `requirements.txt`. For a research paper? Cite it in the bibliography!

**Sarah**: This episode covers:
- **Academic citations**: 39 references in our bibliography
- **Software attribution**: Open-source licenses and acknowledgments
- **Code provenance**: Documenting algorithm sources
- **Citation practices**: Why we cite, what to cite, how to cite

**Alex**: Let's give credit where credit is due!

---

## Why We Cite: Standing on the Shoulders of Giants

**Sarah**: Before we dive into the *how*, let's talk about the *why*. Why do we cite?

**Alex**: Isaac Newton said it best in 1675: **"If I have seen further, it is by standing on the shoulders of giants."**

**Sarah**: Every algorithm we implement, every equation we use, every experiment we design—someone thought of it first. Someone published it. Someone made it possible for us to build on their work.

**Alex**: Classical SMC? That's Vadim Utkin in 1977. The Super-Twisting Algorithm? Arie Levant in 1993. PSO optimization? Kennedy and Eberhart in 1995. We didn't invent these—we **apply** them.

**Sarah**: Citations are how we say "thank you" to the giants whose shoulders we stand on. It's academic gratitude. It's intellectual honesty. It's the foundation of scientific progress.

**Alex**: And practically? Citations help readers:
- **Verify** our claims—they can check the original sources
- **Learn deeper**—follow citation chains to build expertise
- **Reproduce** our work—use the same algorithms and parameters

**Sarah**: So when we say we have 39 references in our bibliography, that's not to look impressive. That's 39 intellectual debts we're acknowledging. Let's explore them!

---

## Bibliography: 39 References—Our Intellectual Debts

**Sarah**: Our bibliography has 39 references covering 50 years of control theory. Rather than list them all, let me group them into three categories: **The Classics**, **Modern Research**, and **The Tools We Build With**.

### The Classics (1970s-1990s): The Founding Fathers

**Alex**: These are the papers that created the field. If you work in sliding mode control, you **must** know these names:

**Vadim Utkin (1977)** - The father of SMC. His paper "Variable Structure Systems with Sliding Modes" defined the theory. Every sliding surface we design, every reaching condition we prove? That's Utkin's legacy.

**Jean-Jacques Slotine and Weiping Li (1991)** - Their textbook "Applied Nonlinear Control" is the Bible of SMC. We use their Lyapunov approach, their control laws, even their notation. When we write equations in our paper, they're echoing Slotine and Li.

**Arie Levant (1993)** - He invented higher-order sliding modes, the foundation of our Super-Twisting controller. Before Levant, SMC was loud and chattery. After Levant? Smooth and quiet.

**Sarah**: These three names appear in **every** SMC paper written in the last 30 years. They're not optional citations—they're required acknowledgment of the giants.

### Modern Research (2000s-2020s): Refining the Craft

**Alex**: The classics gave us the foundation. Modern researchers gave us the tools to make it practical:

**Yuri Shtessel and colleagues (2014)** wrote the modern SMC encyclopedia. Their textbook "Sliding Mode Control and Observation" taught us how to reduce chattering with boundary layers. Our `boundary_layer_width` parameter? Straight from their Chapter 5.

**Jaime Moreno and Leonid Fridman's group (2008-2012)** proved rigorous stability for the Super-Twisting Algorithm. We follow their Lyapunov proof structure but extend it to the harder double-inverted pendulum problem.

**Kennedy and Eberhart (1995)**, **Shi and Eberhart (1998)**, and **Maurice Clerc (2002)** form the PSO trinity. The original algorithm, the inertia weight improvement, and the mathematical stability proof. Our PSO parameters—w=0.729, c1=c2=1.494—come from Clerc's convergence analysis. They're not arbitrary; they're **proven** to work.

**Sarah**: Notice a pattern? We don't just cite papers and forget them. We cite **specific chapters**, **equation numbers**, **parameter values**. If a reader wants to verify our work, they can trace every decision back to a source.

### The Tools We Build With: Software Giants

**Alex**: Here's where citation practices get interesting. Should you cite NumPy?

**Sarah**: In a software project's README? Just list it in dependencies. In a research paper? **Absolutely cite it!**

**Alex**: The **NumPy team** (Harris et al., 2020, published in *Nature*)—over 1,000 contributors built the foundation of scientific Python. We use it for every matrix operation. They deserve credit.

**SciPy** (Virtanen et al., 2020)—their RK45 ODE solver is the **engine** of our simulations. We didn't write our own integrator. We stood on their shoulders.

**Matplotlib** (Hunter, 2007)—all 100+ figures in our paper? Generated with Matplotlib. Their documentation explicitly requests citation. We comply.

**Sarah**: Why cite software?
- **Credit**: Developers rarely get academic recognition. Citations help.
- **Reproducibility**: Readers know **exact versions** (NumPy 1.24.3, not just "NumPy").
- **Transparency**: We're honest about what we built vs. what we used.

**Alex**: Our bibliography has 39 entries. Fourteen are foundational theory papers. Twelve are modern research extensions. Seven are software tools. Six are pendulum dynamics benchmarks for validation.

**Sarah**: Every citation answers the question: "Whose shoulders am I standing on for this specific piece of work?"

---

## Citation Practices: Managing 39 References Without Losing Your Mind

**Alex**: Okay, we've talked about **who** to cite and **why**. Now let's talk about **how** to manage 39 references without going insane.

### The Magic of BibTeX

**Sarah**: BibTeX is like a contact list for papers. You create one master file—ours is called `references.bib`—with all 39 entries. Then every paper, thesis, or presentation you write can pull from that master list.

**Alex**: Each entry has a **citation key**—a short nickname for the paper. We use the format: first author, year, keyword. Like `utkin1977variable` for Utkin's 1977 paper on variable structure systems. Or `kennedy1995particle` for the PSO paper.

**Sarah**: Why does the nickname matter? Because when you're writing, you just type "cite kennedy1995particle" and the bibliography software handles the rest. No copying titles, no formatting author names, no tracking page numbers. It's automatic.

### DOI: The Permanent Address for Papers

**Alex**: Here's a problem: URLs break. Publishers move papers. Websites go down. In 10 years, your link to "ieeexplore.ieee.org/document/12345" might be dead.

**Sarah**: Solution: **DOI**—Digital Object Identifier. It's like a permanent forwarding address. The DOI "10.1109/TAC.2020.12345" will **always** redirect to the paper, even if the publisher changes platforms.

**Alex**: We use DOIs for every reference that has one. Thirty-seven of our 39 references have DOIs. The two that don't? They're old textbooks from before DOIs existed.

### Tools: Zotero and Better BibTeX

**Sarah**: We use **Zotero** as our bibliography manager. It's like iTunes for papers. You add a paper once, and Zotero stores the PDF, extracts the metadata (authors, title, journal), and syncs it to the cloud.

**Alex**: We pair it with the **Better BibTeX plugin**, which auto-generates those citation keys. Click "add to Zotero," and it creates `slotine1991applied` automatically. No manual typing. No typos.

**Sarah**: The master file—`references.bib`—is 39 entries. Our thesis uses 47 (includes extra background). Our conference paper uses 25 (a focused subset). All sourced from the same master list. Update once, update everywhere.

---

## Software Licenses: The Legal Side of "Thank You"

**Alex**: Now let's talk licenses. When you use open-source software, you're bound by its license. And when you **release** open-source software, you need to choose a license.

### Our License: MIT ("Do Whatever You Want, Just Don't Sue Me")

**Sarah**: Our repository uses the **MIT License**. What does that mean?

**Alex**: In plain English? **"Do whatever you want with this code—use it, modify it, sell it—just don't sue me if it breaks."**

**Sarah**: The MIT License is 171 words. The GPL—another popular license—is 5,645 words. MIT is **simple**. It's **permissive**. It's the standard for academic code.

**Alex**: Why MIT over GPL? GPL has "copyleft" rules—if you modify GPL code, you **must** open-source your modifications. Great for some projects, but it complicates commercial use. MIT says "take it, do whatever, just give credit."

**Sarah**: Perfect for research. A company can take our pendulum controller and use it in a product. A student can modify it for their thesis. No restrictions, no legal headaches.

### Dependency Licenses: Documenting What We Use

**Alex**: We use 36 open-source libraries. Each has its own license. We document them all in a file called `LICENSES.md`.

**Sarah**: Why bother? Three reasons:

**1. Legal compliance** - Some licenses require attribution. BSD and MIT licenses say "include our copyright notice." We comply.

**2. Transparency** - Users know what they're getting. NumPy is BSD-licensed. Matplotlib uses a Python Software Foundation-based license. All compatible with MIT.

**3. Audit trail** - If someone questions our license choices, we can point to `LICENSES.md` and show: "Here are all 36 dependencies, their licenses, and their copyright holders."

**Alex**: We also run an automated check in our CI pipeline. It scans every dependency and flags anything with a **GPL** or **AGPL** license—those are copyleft licenses incompatible with MIT. If a GPL dependency sneaks in, the build fails. No exceptions.

**Sarah**: Bottom line: Licenses are how the open-source community says "Here are the rules." We follow them, we document them, and we enforce them automatically.

---

## Code Provenance: Tracing Every Line Back to Its Source

**Alex**: Citations aren't just for papers. Every algorithm in our codebase cites its source **in the code itself**.

### In-Code Citations: Comments That Give Credit

**Sarah**: Open our Classical SMC controller file. The very first thing you see? A citation.

**Alex**: The docstring says: "Based on the control law from Slotine and Li (1991), Applied Nonlinear Control, Chapter 7: Sliding Control. Control law from Equation 7.18."

**Sarah**: Then, in the actual code, we mark specific lines with comments: "Equation 7.12" on the sliding surface calculation, "Equation 7.18" on the control law.

**Alex**: Why? **Traceability**. If a developer wonders "Where did this formula come from?", the comment answers immediately. No hunting through documentation. The citation is **right there** in the code.

**Sarah**: Same for the Super-Twisting controller—cites Levant (1993), Equation 12. Same for PSO—cites Kennedy and Eberhart (1995), Shi and Eberhart (1998), Clerc (2002). Every algorithm, every equation, every parameter.

### Documentation Citations: Explaining the Why

**Alex**: Our documentation goes deeper. For PSO, we explain:
- **Position update**: Kennedy and Eberhart (1995), Equation 1
- **Velocity update**: Shi and Eberhart (1998), Equation 3
- **Parameters**: w=0.729, c1=c2=1.494 from Clerc (2002)

**Sarah**: And we emphasize: **These aren't arbitrary!** Clerc's 2002 paper proved these values guarantee convergence. They're not "tuned by trial and error"—they're mathematically justified.

**Alex**: Every formula in our documentation includes the paper **and** the equation number. A reader can pull up Slotine and Li's textbook, flip to page 285, look at Equation 7.18, and verify: "Yep, they implemented it correctly."

**Sarah**: That's intellectual honesty. That's reproducible research. That's giving credit where it's due.

---

## Citation Formatting: How It Looks in the Paper

**Sarah**: Okay, we've talked about managing citations. What does it actually look like in the finished paper?

### In-Text Citations: Two Styles

**Alex**: There are two ways to cite in LaTeX:

**Parenthetical** - The citation is in parentheses at the end of the sentence. Example: "Sliding mode control guarantees finite-time convergence to the sliding surface (Utkin, 1977)."

**Narrative** - The authors are part of the sentence. Example: "Slotine and Li (1991) derive the reaching condition for sliding mode control."

**Sarah**: Use parenthetical when the paper is supporting evidence. Use narrative when the authors **did** something you're referencing.

**Alex**: You can also cite multiple papers at once: "Higher-order sliding modes reduce chattering (Levant, 1993; Shtessel et al., 2014; Moreno and Osorio, 2012)."

### The Bibliography Section

**Sarah**: At the end of the paper, LaTeX auto-generates the bibliography. All 39 references, alphabetically sorted, consistently formatted.

**Alex**: Each entry shows: authors, year, title, journal or conference, volume, page numbers, and DOI. The reader can find **any** paper we cite.

**Sarah**: And because we used BibTeX, the formatting is automatic. No manual alignment. No typos. No inconsistencies. The computer does it all.

---

## Citation Ethics: When You MUST Cite (And When You Don't)

**Alex**: Let's talk ethics. When **must** you cite?

### Always Cite These Four Things

**Sarah**: **1. Direct quotes or paraphrases** - If an idea came from a paper, cite it. Even if you rephrase. "The sliding surface is defined as..." Slotine and Li said that first. Cite them.

**Alex**: **2. Specific formulas or algorithms** - You implement Utkin's control law? Cite Utkin. You use the PSO algorithm? Cite Kennedy and Eberhart. Even if you wrote the code yourself, the **idea** isn't yours.

**Sarah**: **3. Experimental methods** - If you're copying someone's methodology, cite them. "We use 50 Monte Carlo runs for statistical validation." Where did that number come from? Graichen et al. (2007). Cite them.

**Alex**: **4. Software libraries in your Methods section** - "All simulations were implemented in Python using NumPy for numerical arrays, SciPy for ODE integration, and Matplotlib for visualization." Three citations. Non-negotiable.

### Never Cite These Three Things

**Sarah**: Not everything needs a citation!

**Alex**: **1. Textbook fundamentals** - "The derivative of x-squared is 2x." No citation. That's basic calculus, taught in every textbook for 300 years. It's general knowledge.

**Sarah**: **2. Your own original work** - You invent a new metric for quantifying chattering? That's **your** contribution. No citation needed. That's the work you're **adding** to the field.

**Alex**: **3. Common software patterns** - "import numpy as np" doesn't need a citation. It's standard practice. Every Python programmer does this.

### Self-Citation: The 20% Rule

**Sarah**: Can you cite your own previous papers? Yes! But don't overdo it.

**Alex**: **Appropriate**: "We previously demonstrated (Degachi, 2024) that adaptive SMC outperforms classical SMC." You're building on your own prior work. That's fine.

**Sarah**: **Excessive**: Citing six of your own papers in a single sentence. Journals will flag that. It looks like you're gaming citation counts.

**Alex**: Rule of thumb: Keep self-citations **under 20%** of your bibliography. If you have 39 references, no more than 8 should be your own papers. Ours? Zero self-citations, because this is our first paper on this topic.

---

## Acknowledgments: The People Who Helped (But Aren't Authors)

**Sarah**: Citations are for **ideas**. Acknowledgments are for **people**.

**Alex**: Who do you acknowledge? Five categories:

**1. Funding sources** - "This research was supported by the University of Kaiserslautern-Landau." Money made the work possible. Say thank you.

**2. Technical assistance** - "We thank Dr. XYZ for providing access to the HIL experimental setup." They didn't write the paper, but they provided critical resources.

**3. Software tools** - "We thank the open-source community for NumPy, SciPy, and Matplotlib." We cited them in the bibliography, but we also acknowledge the broader community.

**4. AI assistance** - "Claude Code (Anthropic) provided development assistance and documentation." Some journals **require** AI tool disclosure. We do it for transparency.

**5. Reviewers** - "We thank anonymous reviewers for their constructive feedback." They improved the paper. Give credit.

**Sarah**: **Why acknowledge AI?** Three reasons:

**Alex**: **Transparency** - Readers know what tools you used. **Ethics** - Journals increasingly require disclosure. **Reproducibility** - Future researchers can replicate your workflow.

**Sarah**: Bottom line: Acknowledgments are about gratitude. If someone helped, say thank you.

---

## Version Control: Citations in Git Commits

**Alex**: Here's something most people don't think about: **Git commits** are part of attribution!

**Sarah**: When we implement an algorithm from a paper, the commit message cites the source. Example: "Implement Super-Twisting Algorithm based on Levant (1993) and Moreno and Osorio (2012). Uses Levant's formulation (Equation 12) with strict Lyapunov function from Moreno and Osorio."

**Alex**: Why? Six months later, a developer looks at that code and wonders: "Where did this come from?" The Git history answers immediately. No archaeology required.

**Sarah**: Same reason we cite in code comments. **Traceability**. Every line of code has a story. Commit messages tell that story.

### README: Teaching Others How to Cite You

**Alex**: Our README includes a "Citations" section. It tells users: "If you use this code, here's how to cite it."

**Sarah**: We provide a BibTeX entry for the **software** itself—author, title, year, GitHub URL. Plus guidance: "For the algorithms, cite Slotine and Li (1991) for Classical SMC, Levant (1993) for STA-SMC, Kennedy and Eberhart (1995) for PSO."

**Alex**: Why make it easy? Because if someone uses your code and can't figure out how to cite it, they might **not cite it**. Remove that friction. Give them the exact citation format.

**Sarah**: It's like leaving a tip jar on the counter. Make it obvious. Make it easy. Increase the chances they'll give credit.

---

## Summary: Standing on the Shoulders of Giants

**Sarah**: Let's bring it all back to where we started. **Why do we cite?**

**Alex**: Because we're standing on the shoulders of giants. Every algorithm, every formula, every tool—someone built it before us. Citations are how we say "thank you" and how we trace the genealogy of ideas.

**Sarah**: Our 39 references tell a story:

**The Classics** - Utkin (1977), Slotine and Li (1991), Levant (1993). The founding fathers of sliding mode control. We cite them because their ideas are embedded in every line of our code.

**Modern Research** - Shtessel et al. (2014), Moreno and Osorio (2012), Clerc (2002). They refined the craft, proved stability, optimized parameters. We cite them because they made the theory **practical**.

**The Tools** - NumPy, SciPy, Matplotlib. The software giants. We cite them because our work is impossible without them.

**Alex**: **How do we cite?**

BibTeX manages 39 references automatically. DOIs provide permanent links. Zotero syncs everything to the cloud. Git commits trace algorithm sources. README files teach others how to cite us.

**Sarah**: **When do we cite?**

**Always**: algorithms, formulas, methods, software libraries. **Never**: general knowledge, your own original work. **Carefully**: self-citations under 20%.

**Alex**: **Key numbers:**
- 39 bibliography entries, all DOI-linked
- 36 dependency licenses documented and automated
- 100% algorithm provenance tracked in code
- Zero license conflicts (enforced by CI)

**Sarah**: **The philosophy?** Ideas have authors. Algorithms have inventors. Software has maintainers. **Give credit where credit is due.**

**Alex**: Because someday, someone will cite **you**. And when they do, you'll be grateful they remembered whose shoulders they stood on.

**Sarah**: That's the social contract of science. That's how knowledge grows. That's standing on the shoulders of giants.

---

## Resources

- **Repository:** https://github.com/theSadeQ/dip-smc-pso.git
- **Documentation:** `docs/` directory
- **Getting Started:** `docs/guides/getting-started.md`

---

*Educational podcast episode generated from comprehensive presentation materials*
