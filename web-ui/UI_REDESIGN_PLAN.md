# Task Agent Web UI Redesign Plan
## Claude Desktop UI Clone with Dark Blue Accents

### Overview
Complete redesign of the Task Agent Web UI to match Claude Desktop's layout, typography, and styling exactly - replacing orange accents with dark blue (#1e40af). Using existing AI Elements components but restyling them to match Claude's visual patterns.

## Design Reference
- **Base**: Claude Desktop UI (Screenshot 2025-09-08 at 9.52.04 PM.png)
- **Color Change**: Orange → Dark Blue (#1e40af)
- **Target**: Exact replication of Claude's compact, professional design

---

## Phase 1: Message System Redesign

### User Messages
- **Container**: Dark rounded bubble (like Claude's user messages)
- **Background**: Dark gray/charcoal color
- **Position**: left-aligned
- **Typography**: Match Claude's user message font size and weight
- **Padding**: Compact padding matching Claude's spacing
- **Border radius**: Rounded corners like Claude

### AI Messages  
- **Container**: NO background container
- **Display**: Plain text directly on main background
- **Position**: Left-aligned, natural flow
- **Typography**: Match Claude's response text exactly
- **Spacing**: Natural line spacing, no artificial containers

### Implementation Strategy
- Modify AI Elements `Message` and `MessageContent` components
- Add conditional styling based on message role
- Custom CSS classes for Claude-like appearance

---

## Phase 2: Tool Usage Containers

### Collapsible Tool Sections
- **Style**: Match Claude's "VPS getVirtualMachineListV1" expandable sections
- **Header**: Dark background with tool name and dark blue chevron
- **Content**: Expandable content area with proper syntax highlighting
- **Animation**: Smooth expand/collapse like Claude
- **Border**: Subtle borders matching Claude's container styling

### Request/Response Sections
- **Request Container**: "Request" header with JSON/parameter display
- **Response Container**: "Response" header with formatted output
- **Syntax Highlighting**: Match Claude's JSON highlighting colors
- **Copy Button**: Dark blue accent for copy functionality (non-functional initially)

### Implementation Strategy
- Enhance AI Elements `Tool`, `ToolHeader`, `ToolContent` components
- Add custom collapsible styling to match Claude exactly
- Dark blue accent colors for interactive elements

---

## Phase 3: Input Area Enhancement

### Input Field Design
- **Size**: Large, prominent input field matching Claude's "Reply to Claude..." area
- **Styling**: Same background, border, and shadow as Claude
- **Placeholder**: Match Claude's placeholder text styling
- **Auto-resize**: Expand height as user types (like Claude)

### Integrated Controls
- **Model Selection**: Dropdown with dark blue accent, styled like Claude
- **File Upload**: Button with dark blue styling (placeholder functionality)
- **Send Button**: Dark blue background with proper hover states
- **Layout**: All controls integrated within input area container

### Bottom Bar Design
- **Position**: Fixed bottom with proper spacing
- **Container**: Match Claude's input container styling exactly
- **Shadow**: Subtle shadow like Claude's input area

---

## Phase 4: Header & Layout

### Header Redesign
- **Height**: Compact ~48px height (like Claude)
- **Agent Name**: Display like Claude's "VPS Root SSH Access" format
- **Description**: Subtle, smaller text below agent name
- **Navigation**: Minimal back button styling
- **Authentication**: Small badge/pill instead of large button

### Overall Layout
- **Spacing**: Match Claude's tight, efficient spacing throughout
- **Margins**: Consistent with Claude's layout margins
- **Padding**: Compact padding matching Claude's density
- **Scrolling**: Smooth scroll behavior like Claude

---

## Phase 5: Typography & Color System

### Typography System
- **Font Family**: System fonts matching Claude Desktop
  - `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto'`
- **Font Sizes**: 
  - Body text: 14px (match Claude)
  - Small text: 12px 
  - Headers: 16px-18px
- **Line Height**: 1.4-1.5 (compact like Claude)
- **Font Weight**: Match Claude's weight hierarchy

### Color Palette
```css
/* Primary Colors */
--background: #0f1419;           /* Main background */
--surface: #1a1f2e;             /* Cards/containers */
--surface-hover: #242936;       /* Hover states */

/* Text Colors */  
--text-primary: #ffffff;        /* Main text */
--text-secondary: #9ca3af;      /* Secondary text */
--text-muted: #6b7280;          /* Muted text */

/* Accent Colors */
--accent-primary: #1e40af;      /* Dark blue (replaces orange) */
--accent-hover: #1d4ed8;        /* Dark blue hover */
--accent-subtle: #1e40af20;     /* Subtle accent background */

/* Borders */
--border: #374151;              /* Subtle borders */
--border-strong: #4b5563;       /* Stronger borders */

/* User Message */
--user-message-bg: #2d3748;     /* Dark user message background */
--user-message-text: #ffffff;   /* User message text */
```

---

## Phase 6: Component-Specific Implementation

### AI Elements Component Modifications

#### Conversation Component
- Remove default padding/margins
- Match Claude's conversation container styling
- Proper scroll behavior and positioning

#### Message Components
- **User messages**: Apply dark bubble styling
- **AI messages**: Remove all background styling
- **Avatar**: Smaller size (24px), positioned like Claude
- **Spacing**: Tight spacing between messages

#### Tool Components
- **Tool Container**: Match Claude's expandable sections
- **Tool Header**: Dark blue chevron, proper typography
- **Tool Content**: Syntax highlighted content areas
- **Collapsible**: Smooth animations matching Claude

### Custom CSS Classes
```css
.message-user {
  /* Dark bubble styling for user messages */
}

.message-assistant {
  /* Plain text styling for AI messages */
}

.tool-section {
  /* Claude-style collapsible tool sections */
}

.input-area {
  /* Claude-style input container */
}

.header-compact {
  /* Compact header styling */
}
```

---

## Phase 7: Interactive Elements

### Buttons & Controls
- **Primary Button**: Dark blue background with proper hover
- **Secondary Button**: Transparent with dark blue border
- **Icon Buttons**: Minimal styling with dark blue accent on hover
- **Dropdown**: Claude-style dropdown with dark blue accents

### Hover States
- **Subtle animations**: Match Claude's micro-interactions
- **Color transitions**: Smooth transitions to dark blue accents
- **Focus states**: Proper keyboard navigation styling

### Loading States
- **Spinners**: Dark blue colored loading indicators
- **Skeleton**: Subtle loading states matching Claude's style
- **Progress**: Any progress indicators use dark blue

---

## Phase 8: Final Polish & Testing

### Responsive Design
- **Mobile optimization**: Ensure compact design works on smaller screens
- **Tablet adaptation**: Proper scaling for medium screens
- **Desktop optimization**: Full Claude Desktop experience

### Performance
- **Smooth animations**: 60fps animations for all interactions
- **Memory efficiency**: Optimize for long conversations
- **Load times**: Fast rendering of messages and components

### Consistency Check
- **Cross-component styling**: Ensure all components follow the same patterns
- **Color usage**: Consistent use of dark blue accents throughout
- **Typography**: Consistent font sizing and spacing
- **Spacing system**: 4px, 8px, 12px, 16px grid system

---

## Implementation Order

1. **Phase 1**: Message styling (user bubbles + plain AI text)
2. **Phase 2**: Tool usage collapsible containers  
3. **Phase 3**: Input area with controls
4. **Phase 4**: Compact header design
5. **Phase 5**: Typography and color system
6. **Phase 6**: Component modifications
7. **Phase 7**: Interactive elements and states
8. **Phase 8**: Final polish and testing

## Success Criteria
- [ ] UI matches Claude Desktop visual patterns exactly
- [ ] User messages have dark bubble containers
- [ ] AI messages are plain text without backgrounds
- [ ] Tool usage in proper collapsible containers
- [ ] Dark blue accents replace all orange elements
- [ ] Typography matches Claude's font system
- [ ] Input area styled like Claude's input
- [ ] Compact, efficient use of space throughout
- [ ] Smooth interactions and animations
- [ ] Professional, polished appearance

## Notes
- Preserve existing AI Elements component structure
- Focus on CSS styling rather than component rebuilding
- Maintain existing WebSocket functionality
- Keep all existing features while improving visual design
- Test across different screen sizes and browsers