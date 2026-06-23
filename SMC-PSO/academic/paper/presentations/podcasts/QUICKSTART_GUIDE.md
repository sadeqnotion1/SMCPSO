# Quick Start: Creating 30+ Hour Podcast Series

This guide shows you how to convert your 400-slide presentation into a comprehensive 100+ episode podcast series using Google NotebookLM.

---

## The Problem with NotebookLM's 20-Minute Limit

**NotebookLM generates ~20 minutes per upload**, but you want **30+ hours (1800 minutes)**.

**Solution:** Create **100-120 micro-episodes**, each covering one specific topic in depth.

---

## Quick Start (Pilot: First 5 Episodes)

### Step 1: Generate Episode PDFs (5 minutes)

```bash
cd D:\Projects\main\academic\paper\presentations\podcasts\scripts

# Generate first 5 episodes of Part 1
python create_podcast_episodes.py --parts part1 --output ../episodes/

# Or generate a single episode
python create_podcast_episodes.py --episode E001 --output ../episodes/
```

**Output:** Creates `episodes/part1_foundations/E001_what_is_dip_smc_pso.pdf` (and 4 more)

---

### Step 2: Upload to NotebookLM (10 minutes per episode)

1. Go to **notebooklm.google.com**
2. Click "New Notebook"
3. Name it: **"DIP-SMC-PSO Episode E001"**
4. Click "+ Sources" → Upload `E001_what_is_dip_smc_pso.pdf`
5. Wait for processing (~1 minute)
6. Click **"Generate Audio Overview"** button (bottom right)
7. Wait ~3-5 minutes for audio generation
8. Click **Download** → Save as `E001_what_is_dip_smc_pso.mp3`

**Repeat for E002-E005**

---

### Step 3: Organize Audio Files (1 minute)

```bash
# Move downloaded files
mkdir -p podcasts/audio/part1_foundations
mv ~/Downloads/E00*.mp3 podcasts/audio/part1_foundations/
```

---

### Step 4: Validate Pilot (5 minutes)

Listen to E001-E005. Check:
- ✓ Audio quality is good
- ✓ Content covers the topic
- ✓ 15-20 minute duration per episode
- ✓ Conversational tone works

**If satisfied:** Scale to all 100+ episodes!

---

## Full Production Workflow

### Phase 1: Content Expansion (1-2 weeks, manual)

**Current state:** You have 25 detailed speaker scripts covering representative slides

**Goal:** Expand to 100+ episode scripts covering ALL 400 slides

**Two approaches:**

#### Option A: Write detailed scripts for all episodes (recommended for quality)

1. Use existing speaker scripts as templates
2. For each section in `sections/`, write 3-4 episode scripts
3. Follow this structure per episode:
   ```
   - Episode Overview (1 paragraph)
   - Introduction (2-3 paragraphs)
   - Technical Deep-Dive (5-8 paragraphs with examples)
   - Key Takeaways (3-5 bullet points)
   - Connections to other episodes
   - Next Episode Preview (1 paragraph)
   ```

**Time:** ~2 hours per episode × 100 episodes = 200 hours (can be split across team)

#### Option B: Use presentation slides + minimal narration (faster, less comprehensive)

1. Extract slide content from `sections/*.tex`
2. Add brief narration between slides
3. Let NotebookLM's AI "fill in the gaps" with natural dialogue

**Time:** ~30 minutes per episode × 100 episodes = 50 hours

---

### Phase 2: PDF Generation (1 day, mostly automated)

```bash
# Generate ALL episodes at once
python create_podcast_episodes.py --parts all --output episodes/

# Review generated PDFs
ls -lh episodes/*/E*.pdf | wc -l  # Should show ~100 files
```

---

### Phase 3: Batch NotebookLM Processing (2-3 weeks)

**The bottleneck:** You must upload each PDF individually and wait for audio generation

**Workflow optimization:**

1. **Batch upload strategy:**
   - Open 5 browser tabs with NotebookLM
   - Process 5 episodes in parallel
   - ~15 minutes per batch of 5 episodes
   - 100 episodes ÷ 5 = 20 batches × 15 min = 5 hours total

2. **Use the batch helper script:**
   ```bash
   python scripts/notebooklm_batch_helper.py --episodes episodes/part1_foundations/*.pdf
   ```
   (This script creates a checklist and tracks progress)

3. **Naming convention:**
   - NotebookLM downloads as generic names
   - Immediately rename: `audio-overview-123.mp3` → `E001_what_is_dip_smc_pso.mp3`

---

### Phase 4: Post-Production (1 week)

#### Add Intro/Outro (optional but recommended)

```bash
# Create intro/outro music (10 sec each)
# Use tools like Epidemic Sound, Artlist, or free options (YouTube Audio Library)

# Add to each episode with ffmpeg
for episode in audio/*.mp3; do
    ffmpeg -i intro.mp3 -i "$episode" -i outro.mp3 \
           -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1" \
           "processed/$(basename $episode)"
done
```

#### Normalize Audio Levels

```bash
# Ensure consistent volume across all episodes
ffmpeg-normalize audio/*.mp3 -o normalized/ -c:a libmp3lame -b:a 192k
```

#### Create Metadata/Show Notes

```bash
python scripts/generate_show_notes.py --episodes audio/*.mp3 --output metadata/
```

---

## Timeline Breakdown

| Phase | Duration | Bottleneck |
|-------|----------|------------|
| Content expansion | 1-2 weeks | Manual writing |
| PDF generation | 1 day | Automated |
| NotebookLM processing | 2-3 weeks | Manual uploads (15 min × 20 batches = 5 hours active work, rest is waiting) |
| Post-production | 1 week | Audio editing |
| **Total** | **5-7 weeks** | **Content writing (Phase 1)** |

---

## Shortcut: Start with Existing Materials

**Can't spend 1-2 weeks writing?** Use what you already have:

### Immediate Podcast Series (This Weekend!)

1. **Use existing speaker scripts directly** (25 episodes, ~4 hours)
   ```bash
   # Compile each speaker script individually
   cd speaker_scripts
   for script in part*.tex appendix.tex; do
       pdflatex "$script"
   done

   # Upload 5 PDFs to NotebookLM → 5 episodes, 1.5-2 hours of audio
   ```

2. **Use presentation sections as-is** (35 episodes, ~12 hours)
   ```bash
   # Compile each section from sections/ directory
   cd sections
   for section in part*/*.tex; do
       # Create wrapper .tex file with speaker_config
       # Compile to PDF
       # Upload to NotebookLM
   done
   ```

3. **Hybrid approach** (60 episodes, ~20 hours)
   - Use 25 detailed speaker scripts (4 hours)
   - Add 35 section-level podcasts (12 hours)
   - Fills in gaps without full script writing

**Result:** 20+ hours of podcast content THIS WEEKEND using existing materials only!

---

## Optimization Tips

### Parallel Processing

- Use multiple Google accounts (if allowed) to process 10+ episodes simultaneously
- NotebookLM has no published rate limits (as of Jan 2025)

### Content Reuse

- One detailed section script can become 3-4 episodes with minor editing
- Existing speaker scripts already have 8-10 min content → perfect for 15-20 min episodes

### Quality vs. Speed Tradeoff

- **High quality:** Write detailed scripts (200 hours)
- **Medium quality:** Expand existing scripts (50 hours)
- **Fast:** Use presentation slides as-is (10 hours)

**Recommended for 30+ hours:** Medium quality approach targeting 100 episodes

---

## FAQ

**Q: Can I automate the NotebookLM uploads?**
A: Not officially. NotebookLM has no public API (as of Jan 2025). Manual uploads are required.

**Q: Does NotebookLM support longer episodes?**
A: No, ~20 minutes is the hard limit per audio generation. Multiple sources in one notebook still generate ~20 min total.

**Q: Can I edit the generated audio?**
A: Yes! Download the .mp3 and edit with Audacity, Adobe Audition, or any audio editor.

**Q: What if I want 60-minute episodes instead of 20-minute episodes?**
A: Concatenate 3 related episodes: `ffmpeg -i E001.mp3 -i E002.mp3 -i E003.mp3 -filter_complex concat=n=3:v=0:a=1 Part1_Sec01_Full.mp3`

**Q: Can I use a different TTS service instead of NotebookLM?**
A: Yes! See `PODCAST_PRODUCTION_PLAN.md` for alternatives (ElevenLabs, Podcastle, open-source options)

---

## Next Steps

1. **Run pilot:** Generate and test E001-E005 (today)
2. **Evaluate quality:** Does NotebookLM output meet your standards?
3. **Choose approach:** Full scripts (2 weeks) or existing materials (this weekend)?
4. **Scale production:** Create remaining 95 episodes
5. **Publish:** Upload to Spotify, Apple Podcasts, YouTube, etc.

---

**Ready to start?**

```bash
cd D:\Projects\main\academic\paper\presentations\podcasts\scripts
python create_podcast_episodes.py --episode E001 --output ../episodes/
```

Then upload `episodes/part1_foundations/E001_*.pdf` to NotebookLM!

---

**Questions? Check:**
- `PODCAST_PRODUCTION_PLAN.md` - Full 100-episode breakdown
- `scripts/create_podcast_episodes.py` - Automation script
- `.ai_workspace/guides/` - Project documentation guides

**Status:** Ready to generate pilot episodes
**Last Updated:** 2026-01-23
