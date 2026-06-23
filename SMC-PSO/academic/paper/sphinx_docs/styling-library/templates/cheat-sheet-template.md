# React Bits - Quick Reference Cheat Sheet

One-page reference for the most useful components. 📋



## 🔥 Top 20 Most Useful Components

### Text & Typography (⭐ Essential)

| Component | Use Case | Props |
|-----------|----------|-------|
| **ShinyText** | Hero headings, highlights | `text`, `className` |
| **GlitchText** | Error states, attention | `text`, `glitchSpeed` |
| **CountUp** | Animated numbers, stats | `from`, `to`, `duration` |
| **TextType** | Typewriter effect | `text`, `speed` |
| **GradientText** | Colorful headings | `text`, `colors[]` |

### UI Components (⭐ Essential)

| Component | Use Case | Props |
|-----------|----------|-------|
| **MagicBento** | Card grid layout | `items[]`, `columns` |
| **TiltedCard** | Interactive cards | `children`, `tiltDegree` |
| **Dock** | macOS-style menu | `items[]`, `position` |
| **AnimatedList** | Lists with animation | `items[]`, `delay` |
| **Stepper** | Progress indicator | `steps[]`, `current` |

### Backgrounds (⭐ Essential)

| Component | Use Case | Props |
|-----------|----------|-------|
| **Aurora** | Hero backgrounds | `className`, `colors[]` |
| **Galaxy** | Space theme | `density`, `className` |
| **Particles** | Floating particles | `count`, `speed` |
| **Waves** | Wave patterns | `amplitude`, `frequency` |
| **DotGrid** | Minimalist background | `spacing`, `color` |

### Animations (⭐ Essential)

| Component | Use Case | Props |
|-----------|----------|-------|
| **BlobCursor** | Custom cursor | `size`, `color` |
| **ClickSpark** | Click effects | `color`, `count` |
| **Magnet** | Magnetic pull | `strength`, `radius` |
| **FadeContent** | Fade transitions | `children`, `duration` |
| **PixelTransition** | Pixel effects | `from`, `to`, `speed` |



## 🎯 By Use Case

### Dashboard Hero Section

```tsx
import Aurora from '@/components/react-bits/Aurora'
import ShinyText from '@/components/react-bits/ShinyText'

<div className="relative">
  <Aurora className="absolute inset-0 -z-10" />
  <ShinyText text="I'm OK - You're OK" />
</div>
```

### Animated Statistics

```tsx
import CountUp from '@/components/react-bits/CountUp'

<CountUp from={0} to={100} duration={2} />
```

### Interactive Cards

```tsx
import TiltedCard from '@/components/react-bits/TiltedCard'
import MagicBento from '@/components/react-bits/MagicBento'

<MagicBento>
  <TiltedCard>{/* content */}</TiltedCard>
</MagicBento>
```

### Navigation Menu

```tsx
import Dock from '@/components/react-bits/Dock'

<Dock items={[
  { icon: Home, label: "Home" },
  { icon: Chart, label: "Stats" }
]} />
```

### Progress Tracking

```tsx
import Stepper from '@/components/react-bits/Stepper'

<Stepper steps={[
  { label: "Chapter 1", completed: true },
  { label: "Chapter 2", completed: false }
]} />
```



## 📦 Quick Copy Commands

### Copy Popular Components

```bash
cd "D:\Lifestyle\Book\Im OK Youre OK\im-ok-youre-ok-study\react-bits-library"

# Text animations
cp src/content/TextAnimations/ShinyText/component.tsx ../study-dashboard/components/react-bits/ShinyText.tsx
cp src/content/TextAnimations/CountUp/component.tsx ../study-dashboard/components/react-bits/CountUp.tsx
cp src/content/TextAnimations/GlitchText/component.tsx ../study-dashboard/components/react-bits/GlitchText.tsx

# UI components
cp src/content/Components/MagicBento/component.tsx ../study-dashboard/components/react-bits/MagicBento.tsx
cp src/content/Components/TiltedCard/component.tsx ../study-dashboard/components/react-bits/TiltedCard.tsx
cp src/content/Components/Dock/component.tsx ../study-dashboard/components/react-bits/Dock.tsx

# Backgrounds
cp src/content/Backgrounds/Aurora/component.tsx ../study-dashboard/components/react-bits/Aurora.tsx
cp src/content/Backgrounds/Galaxy/component.tsx ../study-dashboard/components/react-bits/Galaxy.tsx
cp src/content/Backgrounds/Particles/component.tsx ../study-dashboard/components/react-bits/Particles.tsx
```



## 🎨 Common Props Patterns

### Text Components

```tsx
// Standard pattern
<Component
  text="Your text"
  className="text-4xl font-bold"
  speed={1000}        // Animation speed (ms)
  delay={500}         // Start delay (ms)
/>
```

### Background Components

```tsx
// Standard pattern
<Component
  className="absolute inset-0 -z-10"
  colors={['#hex1', '#hex2']}
  density={0.5}       // Particle/element density
  speed={1}           // Animation speed
/>
```

### Card/UI Components

```tsx
// Standard pattern
<Component
  children={<>...</>}
  className="..."
  variant="default"
  size="md"
/>
```



## 🚀 One-Liner Integrations

### Replace Text

```tsx
// Before
<h1>I'm OK - You're OK</h1>

// After
<ShinyText text="I'm OK - You're OK" />
```

### Add Background

```tsx
// Before
<div className="min-h-screen">

// After
<div className="relative min-h-screen">
  <Aurora className="absolute inset-0 -z-10" />
  <div className="relative z-10">
```

### Animate Numbers

```tsx
// Before
<span>{stats.count}</span>

// After
<CountUp to={stats.count} />
```

### Wrap Cards

```tsx
// Before
<Card>...</Card>

// After
<TiltedCard><Card>...</Card></TiltedCard>
```



## 🔧 Required Dependencies

### Minimal Setup (Works Immediately)

- ✅ Framer Motion - Already in your dashboard
- ✅ React - Already installed
- ✅ Tailwind CSS - Already configured

### Optional (For Advanced Components)

```bash
# 3D effects
npm install three @react-three/fiber @react-three/drei

# GSAP animations
npm install gsap

# Spring animations
npm install @react-spring/web
```



## 📂 Component Locations

Quick reference map:

```
src/content/
├── TextAnimations/     # Text effects
│   ├── ShinyText/
│   ├── CountUp/
│   ├── GlitchText/
│   └── ...
├── Components/         # UI components
│   ├── MagicBento/
│   ├── TiltedCard/
│   ├── Dock/
│   └── ...
├── Backgrounds/        # Backgrounds
│   ├── Aurora/
│   ├── Galaxy/
│   ├── Particles/
│   └── ...
└── Animations/         # Effects
    ├── BlobCursor/
    ├── ClickSpark/
    └── ...
```



## 💡 Pro Tips

1. **Always use "use client"** directive for interactive components
   ```tsx
   "use client"
   import Component from './Component'
   ```

2. **Lazy load heavy components**
   ```tsx
   const Aurora = dynamic(() => import('./Aurora'), { ssr: false })
   ```

3. **Combine with existing UI**
   ```tsx
   <Card>
     <ShinyText text="Title" />
     <CountUp to={100} />
   </Card>
   ```

4. **Override styles easily**
   ```tsx
   <Component className="!text-primary !bg-transparent" />
   ```

5. **Check dark mode**
   ```tsx
   <Component className="dark:opacity-50 dark:text-white" />
   ```



## 🎯 Just Ask Claude!

Instead of manually copying, simply say:

> "Add **ShinyText** from React Bits to the dashboard header"

> "Add **Aurora** background to the main page"

> "Replace the progress number with **CountUp** animation"

> "Add **MagicBento** grid for the stats cards"

Claude will automatically find and integrate the component! 🚀



## 📚 Full Documentation

- **Component Index**: [`COMPONENTS_INDEX.md`](./COMPONENTS_INDEX.md) - All 115+ components
- **Quick Start**: [`QUICK_START.md`](./QUICK_START.md) - Getting started guide
- **Integration Guide**: [`INTEGRATION_GUIDE.md`](./INTEGRATION_GUIDE.md) - Dashboard integration
- **Official Docs**: [reactbits.dev](https://reactbits.dev)



**Save this cheat sheet for quick reference!** 📌
