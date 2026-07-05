# College Branding Features 🎓

## New Features Added

Your timetable generator now supports college branding with name and logo display!

### 1. **College Information Section**
   - **Input Fields**:
     - 🏫 **College Name** (optional): Enter your institution name (e.g., "GITAM Institute of Technology")
     - 🖼️ **College Logo** (optional): Upload a college logo image

### 2. **Logo Preview**
   - After uploading, you'll see a preview of your logo in the form
   - Supported formats: PNG, JPG, GIF, WebP

### 3. **Timetable Header Display**
   - When you generate a timetable with college branding:
     - Logo appears on the left (circular display)
     - College name and "Official Timetable Schedule" text appears on the right
     - Beautiful gradient background (purple to pink)
     - Displays above each class timetable

### 4. **Input Form Structure**

```
┌─────────────────────────────────────────┐
│  🎓 College Timetable Generator         │
│  Add college info, classes, teachers... │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🏫 College Information (Optional)      │
│  ✓ College Name: [GITAM]               │
│  ✓ College Logo: [Upload]              │
│    Logo Preview: [Image]                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  📚 Add Classes                         │
│  (existing functionality)               │
└─────────────────────────────────────────┘

[... more sections ...]
```

### 5. **Generated Timetable Display**

```
┌──────────────────────────────────────────────────┐
│  [Logo]  GITAM                                   │
│          📚 Official Timetable Schedule          │
└──────────────────────────────────────────────────┘

┌─────────┬───────────┬───────────┬──────────────┐
│ Time    │ Monday    │ Tuesday   │ Wednesday... │
├─────────┼───────────┼───────────┼──────────────┤
│10:00-11 │ Math(T1)  │ Physics   │ Chemistry    │
│11:00-12 │ Lab(T2)   │ Seminar   │ Project      │
└─────────┴───────────┴───────────┴──────────────┘
```

## How to Use

### Step 1: Enter College Information
1. Click on the **"🏫 College Information (Optional)"** section
2. Enter your college name (e.g., "GITAM Institute of Technology")
3. Upload a college logo (recommended size: square, 200x200px or larger)
4. See the logo preview

### Step 2: Add Classes & Teachers (as before)
- Add classes with lectures, practicals, batches
- Add teachers with abbreviations and subjects
- Add optional subjects if needed

### Step 3: Generate Timetable
- Click **"🚀 Generate Timetable"**
- Your college header will appear above the timetable!

### Step 4: Export with Branding (Optional)
- Click **"📄 Export PDF"** to save the timetable with college branding

## Styling Details

### College Header Styles
- **Background**: Gradient purple (#667eea) to pink (#764ba2)
- **Logo**: Circular display (80x80px), centered
- **Text**: White color, clear hierarchy
- **Responsive**: Works on all screen sizes

### Logo Preview
- **Size**: 100x100px during input
- **Border**: Dashed border to indicate upload area
- **Format**: Automatically scales and crops to square

## Database Integration (Optional)

To persist college branding:
1. Update the Flask backend to accept `college_name` and `college_logo_base64`
2. Store in the `timetable` data returned by API
3. Retrieve on page load

Currently, branding is **per-session** (cleared on page refresh).

## Example Input

**College Name**: "GITAM Institute of Technology"

**Logo**: Upload `gitam-logo.png` (will show as circular badge)

**Class**: SE (Software Engineering)

**Teachers**: 
- T1: Dr. John Doe (Math, DBMS)
- T2: Dr. Jane Smith (OS, Networks)

**Result**: Timetable with GITAM header + purple gradient background!

## Features Not Yet Implemented (Optional Enhancements)

- [ ] Save college branding to backend/database
- [ ] Branding persistence across sessions
- [ ] Custom colors for college header
- [ ] Department name in header
- [ ] Semester/Year in header
- [ ] Multi-language support for "Official Timetable Schedule"

---

**Tech Stack Update**: 
- Svelte 4 + Vite 5
- File upload via HTML5 FileReader API
- Base64 image encoding for preview
- CSS gradients for header styling
