# Increment 10 - UI Component Guide

## Visual Component Overview

This document describes the visual appearance and behavior of each component in the Results Display implementation.

---

## 1. EventCard Component

### Unselected State
```
┌────────────────────────────────────────────────────────────┐
│ □  AI and Machine Learning Conference 2025    [conference] │
│                                                             │
│    Join us for three days of cutting-edge AI research...   │
│                                                             │
│    📅 April 15, 2025    📍 San Francisco, CA, USA          │
│    🏢 Tech Institute                                        │
│                                                             │
│    Relevance: 87%     Source →                             │
└────────────────────────────────────────────────────────────┘
```

### Selected State
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ← Blue border
┃ ☑  AI and Machine Learning Conference 2025    [conference] ┃
┃                                                             ┃
┃    Join us for three days of cutting-edge AI research...   ┃
┃                                                             ┃
┃    📅 April 15, 2025    📍 San Francisco, CA, USA          ┃
┃    🏢 Tech Institute                                        ┃
┃                                                             ┃
┃    Relevance: 87%     Source →                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Features
- **Checkbox (□/☑)**: Click to select/deselect
- **Title**: Clickable link to source (opens new tab)
- **Event Type Chip**: Shows category (conference, meeting, etc.)
- **Description**: Brief summary from article
- **Date Icon (📅)**: Formatted date display
- **Location Icon (📍)**: City, State, Country
- **Organizer Icon (🏢)**: Organization name
- **Relevance Badge**: Color-coded score
  - 🟢 Green: ≥70% (high relevance)
  - 🟠 Orange: 50-69% (medium)
  - ⚪ Gray: <50% (low)
- **Source Link**: Link to original article

### Interactions
- Click checkbox → Toggle selection
- Click anywhere on card → Toggle selection
- Click title/source links → Open in new tab
- Hover → Elevated shadow effect

---

## 2. EventList Component

### Header Section
```
┌──────────────────────────────────────────────────────────────┐
│  Search Results                                              │
│                                                              │
│  Found 12 matching events from 15 extracted events           │
│  (23 articles scraped). Processing time: 45.32s             │
│                                                              │
│  ┌─────────────┐  ┌────────────┐ ┌────────────┐            │
│  │ Sort By:    │  │ Select All │ │ Export All │            │
│  │ Relevance ▼ │  │            │ │ to Excel   │            │
│  └─────────────┘  └────────────┘ └────────────┘            │
│                    ┌────────────┐                           │
│                    │   Clear    │                           │
│                    └────────────┘                           │
└──────────────────────────────────────────────────────────────┘
```

### With Selection
```
┌──────────────────────────────────────────────────────────────┐
│  Search Results                                              │
│                                                              │
│  Found 12 matching events from 15 extracted events           │
│  (23 articles scraped). Processing time: 45.32s             │
│                                                              │
│  ┌─────────────┐  ┌────────────┐ ┌─────────────────────┐   │
│  │ Sort By:    │  │ Select All │ │ Export 5 Selected   │   │
│  │ Relevance ▼ │  │            │ │ to Excel            │   │
│  └─────────────┘  └────────────┘ └─────────────────────┘   │
│                    ┌────────────┐                           │
│                    │   Clear    │                           │
│                    └────────────┘                           │
│                                                              │
│  ℹ️ 5 events selected for export                            │
└──────────────────────────────────────────────────────────────┘
```

### Controls Layout

**Grid Structure (Desktop):**
```
┌─────────────────────────────────────────────────────────────┐
│  [Sort Dropdown]    [Select All] [Clear]    [Export Button] │
│     (25% width)         (25% width)           (50% width)   │
└─────────────────────────────────────────────────────────────┘
```

**Mobile Layout:**
```
┌────────────┐
│ Sort       │ (100% width)
├────────────┤
│ Select All │ (50% width)
│   Clear    │ (50% width)
├────────────┤
│   Export   │ (100% width)
└────────────┘
```

### Empty State
```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                  No events found matching                    │
│                     your criteria                            │
│                                                              │
│        Try adjusting your search filters or using           │
│               different keywords                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Sort Dropdown

### Closed State
```
┌─────────────────┐
│ 🔤 Relevance ▼  │
└─────────────────┘
```

### Open State
```
┌─────────────────┐
│ 🔤 Relevance ▼  │
├─────────────────┤
│ ✓ Relevance     │ ← Selected
│   Date          │
│   Title         │
└─────────────────┘
```

### Options
1. **Relevance** - Highest score first (default)
2. **Date** - Earliest date first
3. **Title** - Alphabetical order (A-Z)

---

## 4. Action Buttons

### Select All Button
```
┌────────────────┐
│ ☑ Select All   │  ← Normal state
└────────────────┘

┌────────────────┐
│ ☑ Select All   │  ← Disabled (no events)
└────────────────┘
```

### Clear Button
```
┌────────────────┐
│ ⊗  Clear       │  ← Normal state
└────────────────┘

┌────────────────┐
│ ⊗  Clear       │  ← Disabled (nothing selected)
└────────────────┘
```

### Export Button States

**No Selection:**
```
┌─────────────────────────────┐
│ ⬇  Export All to Excel      │  ← Default
└─────────────────────────────┘
```

**With Selection:**
```
┌─────────────────────────────┐
│ ⬇  Export 5 Selected to     │  ← Shows count
│    Excel                     │
└─────────────────────────────┘
```

**During Export:**
```
┌─────────────────────────────┐
│ ⏳ Exporting...              │  ← Disabled with spinner
└─────────────────────────────┘
```

**Disabled State:**
```
┌─────────────────────────────┐
│ ⬇  Export All to Excel      │  ← Grayed out
└─────────────────────────────┘
```

---

## 5. Feedback Notifications

### Success Snackbar
```
                    ┌────────────────────────────────┐
                    │ ✓  Excel file exported         │ ← Green
                    │    successfully!         [X]   │
                    └────────────────────────────────┘
                          ↑ Bottom center
```

### Error Snackbar
```
                    ┌────────────────────────────────┐
                    │ ✗  Failed to export results.   │ ← Red
                    │    Please try again.     [X]   │
                    └────────────────────────────────┘
                          ↑ Bottom center
```

### Selection Info Alert
```
┌──────────────────────────────────────────────────────────┐
│ ℹ️  5 events selected for export                         │ ← Blue
└──────────────────────────────────────────────────────────┘
```

**Features:**
- Auto-dismiss after 6 seconds
- Click [X] to close immediately
- Shows at bottom center of screen
- Doesn't block interaction

---

## 6. Complete Layout Example

### Full Page Layout
```
┌─────────────────────────────────────────────────────────────┐
│  Event Scraper & Analyzer                                   │ ← App Bar
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Search Form Component - Already implemented]             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Search Results                               ← EventList  │
│                                                             │
│  Statistics: 12 matched, 15 extracted, 23 scraped          │
│                                                             │
│  [Sort] [Select All] [Clear]      [Export Button]         │
│                                                             │
│  ℹ️ 5 events selected                                      │
│  ┌───────────────────────────────────────────────┐         │
│  │ ☑ Event 1                        [chip]       │ ← Card  │
│  │   Description...                              │         │
│  │   📅 Date    📍 Location    🏢 Organizer      │         │
│  │   Relevance: 87%    Source →                 │         │
│  └───────────────────────────────────────────────┘         │
│  ┌───────────────────────────────────────────────┐         │
│  │ □ Event 2                        [chip]       │         │
│  │   Description...                              │         │
│  └───────────────────────────────────────────────┘         │
│  ┌───────────────────────────────────────────────┐         │
│  │ ☑ Event 3                        [chip]       │         │
│  │   Description...                              │         │
│  └───────────────────────────────────────────────┘         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Event Scraper - Powered by Ollama & spaCy     ← Footer    │
└─────────────────────────────────────────────────────────────┘
                    ┌────────────────────────┐
                    │ ✓ Export successful!   │ ← Snackbar
                    └────────────────────────┘
```

---

## 7. Responsive Behavior

### Desktop (≥1200px)
- 3-column control layout
- Full metadata displayed
- Hover effects enabled
- Large buttons

### Tablet (768-1199px)
- 2-column control layout
- Full metadata displayed
- Touch-friendly buttons
- Medium sizing

### Mobile (<768px)
- Single-column layout
- Stacked controls
- Condensed metadata
- Full-width buttons
- Touch-optimized

---

## 8. Color Scheme

### Material-UI Theme Colors

**Primary (Blue)**
- Buttons: Search, Select All
- Selected border
- Links

**Success (Green)**
- Export button
- High relevance (≥70%)
- Success snackbar

**Warning (Orange)**
- Medium relevance (50-69%)

**Error (Red)**
- Error snackbar
- Form validation errors

**Info (Light Blue)**
- Selection alert
- Information messages

**Gray**
- Low relevance (<50%)
- Disabled states
- Secondary text

---

## 9. Icons Used

### Material-UI Icons
- 📥 **FileDownload**: Export button
- 🔤 **SortByAlpha**: Sort dropdown
- ☑️  **SelectAll**: Select All button
- ⊗  **Deselect**: Clear button
- 🎯 **Event**: Event type chip
- 📍 **LocationOn**: Location field
- 📅 **CalendarToday**: Date field
- 🏢 **Business**: Organizer field
- 🔍 **Search**: Search button (in SearchForm)
- ⏳ **CircularProgress**: Loading spinner

---

## 10. Typography

### Font Hierarchy
- **h5** (24px): Section headers ("Search Results")
- **h6** (20px): Event titles
- **body1** (16px): Descriptions
- **body2** (14px): Metadata, labels
- **caption** (12px): Source links, timestamps

### Font Weights
- **Regular (400)**: Body text
- **Medium (500)**: Labels
- **Bold (600)**: Headers

---

## 11. Spacing System

### Material-UI Spacing (8px base)
- **xs** (4px): Tight spacing
- **sm** (8px): Default spacing
- **md** (16px): Section spacing
- **lg** (24px): Component spacing
- **xl** (32px): Page spacing

### Component Padding
- Cards: 16px (md)
- Buttons: 8px vertical, 16px horizontal
- Containers: 24px (lg)

---

## 12. Animation & Transitions

### Hover Effects
- Card shadow elevation: 0.2s ease-in-out
- Button color change: 0.2s ease
- Link underline: 0.2s ease

### Loading States
- Spinner rotation: Continuous smooth
- Button disable transition: 0.15s

### Snackbar
- Slide in from bottom: 0.3s ease-out
- Fade out on close: 0.2s ease-in

---

## 13. Accessibility Features

### Keyboard Navigation
- Tab through all interactive elements
- Enter to activate buttons/links
- Space to toggle checkboxes
- Escape to close dropdowns

### Screen Reader
- ARIA labels on all controls
- Role attributes for interactive elements
- Alt text for icons (via aria-label)
- Semantic HTML structure

### Visual Indicators
- Focus rings on keyboard navigation
- High contrast text
- Clear disabled states
- Color + text for status (not color alone)

---

## 14. User Interaction Patterns

### Click Behaviors
- **Checkbox**: Toggle selection only
- **Card area**: Toggle selection
- **Title link**: Open source (new tab)
- **Source link**: Open article (new tab)
- **Buttons**: Execute action

### Event Propagation
- Card click doesn't trigger when:
  - Clicking checkbox directly
  - Clicking title link
  - Clicking source link
- Proper stopPropagation() on nested elements

---

## 15. Performance Indicators

### Visual Feedback
- Search: "Searching..." + spinner
- Export: "Exporting..." + spinner
- Form: Fields disabled during operation
- Results: Processing time displayed

### Progress Communication
- "Searching and analyzing events... This may take a minute."
- "X events selected for export"
- "Found X matching events from Y extracted"

---

**End of UI Component Guide**
