# Episode 07 - Statistical Analysis: What the Numbers Actually Mean

**Series:** Advisor Progress Report - Deep Dive
**Duration:** 8-10 minutes
**Narrator:** Single host

---

**[AUDIO NOTE: This episode is about statistical credibility - not just presenting numbers, but defending the methodology. Know why Welch was chosen, know what Cohen's d means, and know where the analysis has gaps. Advisors probe statistical choices hard.]**

## Opening: Numbers Without Context Are Dangerous

The Monte Carlo study produced a table of numbers: Classical SMC settles in 2.15 seconds, STA settles in 1.82 seconds. Is that difference real? Is it meaningful? Could it have happened by chance?

Statistical analysis exists to answer exactly that. Two controllers can produce different sample means just from randomness. To claim STA is genuinely faster - not just luckier - you need to establish statistical significance. And to claim the difference matters in practice, you need to establish practical significance. These are not the same thing.

The MT-5 study used three statistical methods: bootstrap confidence intervals, Welch's t-test for pairwise comparisons, and Cohen's d for effect size. Let us go through each one.

## Bootstrap Confidence Intervals

A confidence interval answers the question: given the 100 samples we observed, what range of values for the true mean is consistent with this data?

The bootstrap method constructs this interval empirically. Take the 100 settling time values. Resample them with replacement 10,000 times, each time computing the mean of the resample. The distribution of those 10,000 means gives you the bootstrap distribution. The 95 percent confidence interval is the 2.5th to 97.5th percentile of that distribution.

For Classical SMC settling time: 1.97 to 2.33 seconds. For STA-SMC: 1.67 to 1.97 seconds. These intervals do not overlap. That is strong evidence the difference in settling times is real.

Why bootstrap rather than a normal distribution formula? Because we do not know whether settling times are normally distributed. The bootstrap makes no distributional assumption - it uses the data itself to estimate the sampling distribution. With 100 samples, this is both reliable and defensible.

Why 10,000 resamples? This is a standard choice. Fewer resamples produce unstable interval estimates - the interval width itself has sampling variability. At 10,000, the stability of the interval estimate is well-established by simulation studies in the literature. An advisor asking "is 10,000 enough?" can be answered yes, with citation to Efron and Hastie 2016.

## Welch's t-Test

For each pairwise comparison - Classical versus STA, Classical versus Adaptive - a Welch t-test was used to produce a p-value.

The question: why Welch, not Student's t?

Student's t-test assumes both groups have equal variance. Looking at the data: Classical SMC energy has standard deviation 7,518. STA energy has standard deviation 15,749. Those are not equal - STA energy varies roughly twice as much as Classical energy. When variances are unequal, Student's t can be anti-conservative - it underestimates the p-value, making results look more significant than they are. Welch's t corrects for this by adjusting the degrees of freedom.

An advisor may ask: why not ANOVA with post-hoc correction instead of multiple pairwise Welch tests? ANOVA is appropriate when the goal is to test whether any group differs from any other. Here the comparisons were pre-planned - we specifically wanted to compare STA versus Classical, Adaptive versus Classical, and so on - not to hunt for any significant difference. Pre-planned comparisons are a recognized justification for not applying Bonferroni correction.

That said, the report acknowledges this explicitly: no Bonferroni correction was applied, and the rationale is pre-planned comparisons. If an advisor disagrees and insists on correction, the conservative response is: apply Bonferroni, and the STA settling time advantage remains significant.

## Cohen's d: Effect Size

The key comparison: STA versus Classical SMC settling time.

Cohen's d equals the difference in means divided by the pooled standard deviation. Numerically: 2.15 minus 1.82 divided by the pooled standard deviation of approximately 0.165, giving d approximately 2.0.

Cohen's d of 2.0 is a large effect by standard conventions - large is typically d greater than 0.8. This is not a marginally significant result driven by large sample size. The 0.33 second difference in settling time represents two standard deviations. Even with a sample of 10 instead of 100, this would be statistically significant.

The formula uses pooled standard deviation: square root of the average of the two variances, weighted by sample size. With equal sample sizes of 100 each, the pooled SD simplifies to the square root of the average of the two variances.

This matters for advisor confidence. A p-value of 0.001 alone tells you the difference is unlikely to be random. Cohen's d of 2.0 tells you the difference is large enough to matter practically - 0.33 seconds faster settlement is meaningful in a real control application.

## What Was Not Done: The Gaps

Two limitations are worth knowing before an advisor raises them.

First: no normality test plots. The bootstrap is robust to non-normality, and Welch's t-test is known to be reasonably robust to moderate departures from normality at n equals 100. But the report does not include QQ-plots or Shapiro-Wilk tests to formally verify the distributional assumptions. An advisor might ask for these. The honest answer: the methods chosen are appropriate for the data, and adding normality checks to the supplemental material is a reasonable thesis finalization item.

Second: Bonferroni correction. With multiple pairwise comparisons - three controllers compared against Classical, so three tests - there is an inflated false-positive rate if you treat each test as independent. Pre-planned comparisons justify the omission, but a conservative reviewer may still request it. Running Welch with Bonferroni at the alpha equals 0.05/3 level: the settling time STA versus Classical comparison remains significant. The energy comparison does not, because STA energy is actually much higher than Classical.

## The Full Results Picture

To cement the statistical picture: what are the actual findings?

Settling time: STA 1.82 seconds versus Classical 2.15 seconds, 95 percent CI non-overlapping, Cohen's d approximately 2.0 - statistically and practically significant.

Overshoot: STA 2.3 percent versus Classical 5.8 percent - again non-overlapping CIs, STA substantially better.

Energy: STA 202,907 N-squared-seconds versus Classical 9,843 - Classical wins by a factor of 20. STA's continuous control comes at dramatically higher energy cost. This is a core tradeoff: STA achieves faster, smoother settling, but the STA mechanism burns far more energy to do it.

Chattering by FFT index: STA 2.1 versus Classical 8.2 - STA is 74 percent lower. This is the central claim of the STA design, validated empirically.

Compute time: Classical 18.5 microseconds, STA 24.2, Adaptive 31.6. All well within the 100 microsecond real-time deadline. At the 10 millisecond control period, even the slowest controller uses 31.6 percent of the available budget.

## Takeaway

The statistical analysis is sound: bootstrap CIs for uncertainty quantification, Welch's t for significance testing, Cohen's d for effect size. The methodology choices are defensible. The gaps - no normality tests, no Bonferroni - are acknowledged explicitly and can be addressed in thesis finalization without changing the main conclusions.

Next episode: a closer look at the boundary layer study and why the original chattering reduction claim had to be corrected.

---

*Report references: Section 5.1, Section 5.4.*
