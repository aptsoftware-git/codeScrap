# Event Types - Quick Reference

## ✅ Updated Event Types (23 Total)

### 📊 Categories Overview

| Category | Count | Types |
|----------|-------|-------|
| Violence & Security | 8 | protest, demonstration, attack, explosion, bombing, shooting, theft, kidnapping |
| Cyber Events | 3 | cyber_attack, cyber_incident, data_breach |
| Meetings & Conferences | 3 | conference, meeting, summit |
| Disasters & Accidents | 2 | accident, natural_disaster |
| Political & Military | 3 | election, political_event, military_operation |
| Crisis Events | 3 | terrorist_activity, civil_unrest, humanitarian_crisis |
| Other | 1 | other |

---

## 🔍 Complete Event Type List

### Violence & Security Events
1. **protest** - Organized public demonstrations
2. **demonstration** - Public displays of opinion
3. **attack** - Violent assaults or strikes
4. **explosion** - Detonations and blasts
5. **bombing** - Explosive attacks
6. **shooting** - Firearm-related incidents
7. **theft** - Stealing and robbery
8. **kidnapping** - Abduction events

### Cyber Events
9. **cyber_attack** - Malicious cyber operations
10. **cyber_incident** - Cyber security incidents
11. **data_breach** - Unauthorized data access

### Meetings & Conferences
12. **conference** - Large formal gatherings
13. **meeting** - Formal assemblies
14. **summit** - High-level meetings

### Disasters & Accidents
15. **accident** - Unintentional incidents
16. **natural_disaster** - Natural catastrophes

### Political & Military
17. **election** - Voting events
18. **political_event** - Political activities
19. **military_operation** - Military actions

### Crisis Events
20. **terrorist_activity** - Terror-related acts
21. **civil_unrest** - Social disorder
22. **humanitarian_crisis** - Humanitarian emergencies

### Other
23. **other** - Uncategorized events

---

## 💻 Usage Examples

### Backend (Python)
```python
from app.models import EventType

# Use in queries
event_type = EventType.CYBER_ATTACK
print(event_type.value)  # "cyber_attack"

# Validate event type
if my_type in [e.value for e in EventType]:
    print("Valid event type")
```

### Frontend (TypeScript)
```typescript
import { EventType } from './types/events';

// Use in forms
const selectedType: EventType = EventType.PROTEST;

// Display label
const label = getEventTypeLabel(selectedType);  // "Protest"
```

### API Request
```json
{
  "phrase": "cyber attack in Mumbai",
  "event_type": "cyber_attack",
  "date_from": "2025-01-01"
}
```

---

## 🎨 UI Display

### Search Form Dropdown Structure
```
Event Type: [Select ▼]
├─ All Types
│
├─ Violence & Security
│   ├─ Protest
│   ├─ Demonstration
│   ├─ Attack
│   ├─ Explosion
│   ├─ Bombing
│   ├─ Shooting
│   ├─ Theft
│   └─ Kidnapping
│
├─ Cyber Events
│   ├─ Cyber Attack
│   ├─ Cyber Incident
│   └─ Data Breach
│
├─ Meetings & Conferences
│   ├─ Conference
│   ├─ Meeting
│   └─ Summit
│
├─ Disasters & Accidents
│   ├─ Accident
│   └─ Natural Disaster
│
├─ Political & Military
│   ├─ Election
│   ├─ Political Event
│   └─ Military Operation
│
├─ Crisis Events
│   ├─ Terrorist Activity
│   ├─ Civil Unrest
│   └─ Humanitarian Crisis
│
└─ Other
    └─ Other
```

---

## 📝 Label Mappings

| Technical Value | UI Label |
|----------------|----------|
| `protest` | Protest |
| `demonstration` | Demonstration |
| `attack` | Attack |
| `explosion` | Explosion |
| `bombing` | Bombing |
| `shooting` | Shooting |
| `theft` | Theft |
| `kidnapping` | Kidnapping |
| `cyber_attack` | Cyber Attack |
| `cyber_incident` | Cyber Incident |
| `data_breach` | Data Breach |
| `conference` | Conference |
| `meeting` | Meeting |
| `summit` | Summit |
| `accident` | Accident |
| `natural_disaster` | Natural Disaster |
| `election` | Election |
| `political_event` | Political Event |
| `military_operation` | Military Operation |
| `terrorist_activity` | Terrorist Activity |
| `civil_unrest` | Civil Unrest |
| `humanitarian_crisis` | Humanitarian Crisis |
| `other` | Other |

---

## 🔧 Testing Commands

### Test Backend Event Types
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -c "from app.models import EventType; print([e.value for e in EventType])"
```

### Test Frontend Build
```bash
cd frontend
npm run build
# Should compile without errors
```

### Test API Endpoint
```bash
curl http://127.0.0.1:8000/docs
# Check /api/v1/search schema for event_type enum
```

---

## 📋 Migration Guide

### Old to New Type Mapping

If you have old data with these types, map them:

| Old Type | New Type | Category |
|----------|----------|----------|
| workshop | meeting | Meetings & Conferences |
| seminar | conference | Meetings & Conferences |
| webinar | conference | Meetings & Conferences |
| forum | meeting | Meetings & Conferences |
| symposium | conference | Meetings & Conferences |
| hackathon | meeting | Meetings & Conferences |
| networking | meeting | Meetings & Conferences |
| training | meeting | Meetings & Conferences |
| exhibition | other | Other |
| competition | other | Other |

---

## 🎯 Search Query Examples

### By Event Type

**Protests:**
```json
{
  "phrase": "protest",
  "event_type": "protest",
  "location": "India"
}
```

**Cyber Incidents:**
```json
{
  "phrase": "data breach",
  "event_type": "data_breach",
  "date_from": "2025-01-01"
}
```

**Natural Disasters:**
```json
{
  "phrase": "earthquake",
  "event_type": "natural_disaster",
  "location": "Turkey"
}
```

**Political Events:**
```json
{
  "phrase": "election results",
  "event_type": "election",
  "date_from": "2025-01-01",
  "date_to": "2025-12-31"
}
```

---

## 📚 Files Modified

1. ✅ `backend/app/models.py`
2. ✅ `frontend/src/types/events.ts`
3. ✅ `frontend/src/components/SearchForm.tsx`

---

## 🚀 Quick Start

### View in Browser
1. Open: http://localhost:5173
2. Click "Event Type" dropdown
3. See categorized event types
4. Select type and search

### Test API
1. Open: http://127.0.0.1:8000/docs
2. Try POST /api/v1/search
3. Use event_type parameter
4. Check results

---

## ✅ Validation Checklist

- [x] Backend EventType updated (23 types)
- [x] Frontend EventType updated (23 types)
- [x] Labels mapped correctly
- [x] Categories organized logically
- [x] SearchForm dropdown enhanced
- [x] No TypeScript errors
- [x] No Python errors
- [x] Both servers running
- [x] Documentation updated

---

**Status:** ✅ COMPLETE

**Date:** December 2, 2025

---

**End of Quick Reference**
