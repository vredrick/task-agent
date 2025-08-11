# PulseHabits Design System & AI UI Prompts
**High-Fidelity Implementation Package** | v1.0

## 1. Visual Style Brief

### Brand Personality
**Calm • Focused • Optimistic**
- Soft gradients with subtle depth
- Generous whitespace for breathing room
- Celebratory moments with controlled energy

### Extended Token System
```css
/* Base Colors */
--primary: #6366F1
--primary-hover: #5558E3
--primary-pressed: #4A4DD6
--primary-disabled: #6366F140

--success: #10B981
--warning: #F59E0B
--error: #EF4444
--info: #3B82F6

/* Surfaces - Light Mode */
--surface-base: #FFFFFF
--surface-elevated: #FAFAFA
--surface-overlay: #00000008
--surface-pressed: #00000005
--border: #E5E7EB
--border-focus: #6366F1

/* Surfaces - Dark Mode */
--surface-base-dark: #1F2937
--surface-elevated-dark: #374151
--surface-overlay-dark: #FFFFFF08
--border-dark: #4B5563

/* Typography */
--text-primary: #1F2937
--text-secondary: #6B7280
--text-tertiary: #9CA3AF
--text-inverse: #FFFFFF

/* Shadows */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05)
--shadow-md: 0 4px 6px rgba(0,0,0,0.07)
--shadow-lg: 0 10px 15px rgba(0,0,0,0.10)
--shadow-focus: 0 0 0 3px rgba(99,102,241,0.15)
```

## 2. Component Inventory

### App Bar
- Height: 56px
- Padding: 16px horizontal
- States: Default, scrolled (add shadow)
- A11y: role="banner", aria-label="App navigation"

### Tab Bar
- Height: 64px
- Icons: 24x24px
- Active indicator: 2px top border
- A11y: role="tablist", aria-selected states

### Habit Card
```
Layout: 16px padding, 12px radius
States:
- Default: white bg, border
- Pressed: scale(0.98), shadow-sm
- Completed: success border, checkmark
- Disabled: 0.5 opacity
Spacing: 8px between elements
A11y: role="button", aria-pressed state
```

### Hold-to-Check Control
- Size: 64x64px circle
- Progress: 2-second hold duration
- Visual: Radial progress fill
- Haptic: Light→Medium→Success
- A11y: aria-live="polite" for progress

### Streak Badge
- Min size: 32x32px
- Fire emoji + number
- Pulse animation at milestones
- A11y: aria-label="7 day streak"

### Calendar Heatmap
- Cell: 12x12px, 2px gap
- Colors: 5-step gradient (gray→primary)
- Touch target: 44x44px overlay
- A11y: role="grid", aria-label per cell

## 3. Screen Blueprints

### Create Habit Screen
```
Grid: 16px margins, 8px vertical spacing
Header: Back arrow + "New Habit" title
Content:
- Input field (full width - 32px)
- Time selector (3 radio options)
- Reminder toggle + time picker
- Primary CTA bottom-fixed
Critical copy: "What do you want to build?"
```

### Today Dashboard
```
Grid: 16px margins, 12px card gaps
Header: "Today" + streak badge right
Content:
- Progress ring (120px, centered)
- Habit cards list
- FAB (+) bottom-right 16px
Critical copy: "2 of 3 completed"
```

### Check-in Screen
```
Layout: Center-aligned, 24px padding
Elements:
- Habit title (size-xl)
- Description (size-base, secondary)
- Hold-to-check control (centered)
- Skip link bottom
Critical copy: "Hold to complete"
```

### Habit Detail
```
Grid: 16px margins
Sections:
- Stats row (3 columns)
- Calendar heatmap
- Edit/Delete actions
Critical copy: "Best streak: 14 days"
```

## 4. Interaction & Motion

### Navigation Transitions
- Push: 300ms ease-out, slide + fade
- Modal: 250ms bottom sheet slide
- Tab switch: 200ms crossfade

### Hold-to-Check Micro-interaction
```
0ms: Touch down - scale(0.95)
0-2000ms: Radial fill animation
1000ms: Haptic tick
2000ms: Success haptic + confetti
2100ms: Navigate back
```

### Success Celebration
- Confetti: 5 emitters, 2s duration
- Badge: Scale(1.2) + rotate(5deg)
- Card: Checkmark draw SVG animation

## 5. Accessibility

### Requirements
- **Contrast**: 4.5:1 minimum (7:1 for small text)
- **Touch targets**: 44x44pt minimum
- **Focus order**: Logical top-to-bottom, left-to-right
- **VoiceOver**: "{Habit name}, {completion status}, button"
- **Dynamic type**: Support 85%-200% scaling
- **Motion**: Respect prefers-reduced-motion

## 6. AI UI Prompts

### Prompt Template Structure
```
Create a [screen name] for PulseHabits habit tracker app.
Design: Calm, focused, optimistic. Soft gradients, generous whitespace.
Frame: iPhone 13 (390x844px) and Pixel 6 (412x915px).
Mode: Light and dark variants.
[Specific screen details]
Export: Production-ready React Native components.
```

### Today Dashboard Prompt
```
Create Today Dashboard for PulseHabits. Center progress ring showing "2 of 3 completed". Below: vertical list of habit cards with circular checkboxes, habit names, and durations. Each card: white background, 12px radius, subtle border, 16px padding. Completed habits show green checkmark and border. Header shows "Today" left, flame+streak badge right. FAB with plus icon bottom-right. Use colors: primary #6366F1, success #10B981, surface #FFFFFF, borders #E5E7EB. Include both iPhone 13 (390x844) and Pixel 6 (412x915) frames with dark mode using #1F2937 background.
```

### Create Habit Prompt
```
Create New Habit screen. Large text input "What do you want to build?" with 16px padding, 12px radius border. Below: three radio options for Morning/Afternoon/Evening timing. Reminder toggle with inline time picker (shows when enabled). Fixed bottom button "Create Habit" with primary color #6366F1. Include back navigation header. Soft keyboard visible state. Both device frames with dark variant.
```

### Check-in Prompt
```
Create Check-in screen centered layout. Large habit title "Meditate" (28px), subtitle "5 minutes" (16px, gray). Center: 64px circular hold-to-check button with dashed border, "Hold to complete" inside. Radial progress indicator ready. Bottom: "Skip today" text link. Minimalist design, lots of whitespace. Export with pressed state showing filled progress.
```

## 7. Prototype Map

```
App Launch
    ├→ Onboarding (first-time)
    │   └→ Create First Habit → Today
    └→ Today Dashboard (returning)
        ├→ Habit Card Tap → Check-in
        │   ├→ Complete → Today (updated)
        │   └→ Skip → Today
        ├→ FAB → Create Habit
        └→ Tab Navigation
            ├→ Progress View
            └→ Settings

Conditional Flows:
- Offline: Show local state + sync icon
- Empty: Show illustration + CTA
- Streak milestone: Trigger celebration
```

## 8. Export Guidelines

### Icons
- Base: 24x24px
- Densities: @1x, @2x, @3x
- Format: SVG preferred, PNG fallback
- Stroke: 2px consistent

### Assets
```
habit-icons/
  ├── meditation.svg
  ├── exercise.svg
  └── reading.svg
animations/
  ├── confetti.json (Lottie)
  ├── progress-ring.json
  └── checkmark-draw.json
```

### Responsive Breakpoints
- Compact: 320-389px
- Regular: 390-429px
- Large: 430px+

### Platform Specifics
- iOS: SF Symbols where possible
- Android: Material Icons baseline
- Haptics: Native APIs per platform

---

**Implementation Notes**: Components built with React Native + Styled Components. State management via Context API. Animations using Reanimated 3. Local storage with AsyncStorage, sync with GraphQL.