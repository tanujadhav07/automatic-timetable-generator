<script>
  import { onMount } from 'svelte'
  
  // Navigation
  let currentPage = 'home' // 'home', 'class-view', 'teacher-view', 'setup'
  
  // Welcome notification
  let welcomeMessage = ''
  let showWelcome = false
  
  // Core Data
  let timetableData = null
  let classes = []
  let teachers = []
  let error = null
  
  // Teacher View State
  let selectedTeacher = ''
  let teacherTimetable = {}

  // Class View State
  let selectedClass = ''

  // Setup Form State
  let formClasses = []
  let formTeachers = []
  let formElectiveSubjects = []
  let collegeName = 'College Timetable Generator'
  let collegeLogoPreview = null
  let includeProject = false

  // Form Inputs
  let newClass = { name: '', lectures: '', practicals: '', batches: '' }
  let newTeacher = { name: '', fullName: '', subjects: '' }
  let newElective = { className: '', lectureSubject: '', practicalSubject: '', lectureTeachers: '', practicalTeachers: '' }

  const DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
  const TIMESLOTS = ["10:00 - 11:00", "11:00 - 12:00", "12:00 - 13:00", "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00", "16:00 - 17:00"]

  onMount(() => {
    // Load data from localStorage if available
    const savedClasses = localStorage.getItem('formClasses')
    const savedTeachers = localStorage.getItem('formTeachers')
    const savedElectives = localStorage.getItem('formElectiveSubjects')
    const savedCollege = localStorage.getItem('collegeName')
    
    if (savedClasses) formClasses = JSON.parse(savedClasses)
    if (savedTeachers) formTeachers = JSON.parse(savedTeachers)
    if (savedElectives) formElectiveSubjects = JSON.parse(savedElectives)
    if (savedCollege) collegeName = savedCollege
    
    // Check for welcome message from login/register
    const msg = sessionStorage.getItem('welcomeMessage')
    if (msg) {
      welcomeMessage = msg
      showWelcome = true
      sessionStorage.removeItem('welcomeMessage')
      // Auto-hide after 5 seconds
      setTimeout(() => showWelcome = false, 5000)
    }
  })

  $: {
    // Auto-save to localStorage
    if (formClasses.length) localStorage.setItem('formClasses', JSON.stringify(formClasses))
    if (formTeachers.length) localStorage.setItem('formTeachers', JSON.stringify(formTeachers))
    if (formElectiveSubjects.length) localStorage.setItem('formElectiveSubjects', JSON.stringify(formElectiveSubjects))
    localStorage.setItem('collegeName', collegeName)
  }

  // --- API Functions ---
  async function generateTimetable() {
    if(!formClasses.length || !formTeachers.length) {
      error = 'Please add at least one class and one teacher in Setup'
      currentPage = 'setup'
      return
    }
    try {
      error = null
      const bulkRes = await fetch('/api/bulk-add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bulkClasses: JSON.stringify(formClasses),
          bulkTeachers: JSON.stringify(formTeachers),
          bulkElectiveSubjects: JSON.stringify(formElectiveSubjects)
        })
      })
      if(!bulkRes.ok) throw new Error('Failed to save data')
      
      const ttRes = await fetch(`/api/timetable?project=${includeProject}`)
      if(!ttRes.ok) throw new Error('Failed to generate timetable')
      
      timetableData = await ttRes.json()
      classes = Object.keys(timetableData.timetable || {})
      teachers = timetableData.teachers || []
      
      if(classes.length) selectedClass = classes[0]
      if(teachers.length) selectedTeacher = teachers[0].name
      
      currentPage = 'class-view'
    } catch(e) {
      error = e.message
    }
  }

  // --- Logic Helpers ---
  function format12h(range) {
    const to12 = (hm) => {
      const [hStr, mStr] = hm.split(':')
      let h = parseInt(hStr, 10)
      const ampm = h >= 12 ? 'PM' : 'AM'
      h = h % 12 || 12
      return `${h}:${mStr} ${ampm}`
    }
    return range.includes(' - ') ? range.split(' - ').map(to12).join(' - ') : to12(range)
  }

  function getTeacherSchedule(teacherName) {
    const schedule = {}
    DAYS.forEach(day => {
      schedule[day] = {}
      TIMESLOTS.forEach(slot => {
        let found = ''
        Object.entries(timetableData.timetable).forEach(([cls, days]) => {
          const val = days[day]?.[slot]
          if (val && val.includes(`Teacher ${teacherName}`)) {
            found = `${cls}: ${val.split(' | ')[0]}`
          } else if (val === "Lunch Break") {
            found = "Lunch Break"
          }
        })
        schedule[day][slot] = found
      })
    })
    return schedule
  }

  function isProjectDay(cls, day) {
    const slots = timetableData?.timetable[cls]?.[day]
    return slots && Object.values(slots).every(v => v === "Project Day")
  }

  // Reactive statement for teacher schedule
  $: teacherSchedule = selectedTeacher && timetableData ? getTeacherSchedule(selectedTeacher) : {}

  // --- Form Handlers ---
  function addClass() {
    if(newClass.name) {
      formClasses = [...formClasses, {
        name: newClass.name,
        lectures: newClass.lectures.split(',').map(s => s.trim()),
        practicals: newClass.practicals.split(',').map(s => s.trim()),
        batches: newClass.batches.split(',').map(s => s.trim())
      }]
      newClass = { name: '', lectures: '', practicals: '', batches: '' }
    }
  }

  function addTeacher() {
    if(newTeacher.name) {
      formTeachers = [...formTeachers, {
        name: newTeacher.name,
        fullName: newTeacher.fullName || newTeacher.name,
        subjects: newTeacher.subjects.split(',').map(s => s.trim())
      }]
      newTeacher = { name: '', fullName: '', subjects: '' }
    }
  }

  function exportPDF(title, elementId) {
    const doc = new window.jspdf.jsPDF({orientation: 'landscape', unit: 'pt', format: 'a4'})
    doc.setFontSize(20)
    doc.text(title, 40, 40)
    doc.autoTable({ html: `#${elementId}`, startY: 60, theme: 'grid', styles: { fontSize: 8 } })
    doc.save(`${title.replace(/\s+/g, '_')}.pdf`)
  }
</script>

<div class="app-container">
  <!-- Sidebar Navigation -->
  <nav class="sidebar">
    <div class="logo-area">
      {#if collegeLogoPreview}
        <img src={collegeLogoPreview} alt="Logo" class="nav-logo" />
      {/if}
      <span class="college-title">{collegeName}</span>
    </div>
    
    <ul class="nav-links">
      <li>
        <button class:active={currentPage === 'home'} on:click={() => currentPage = 'home'}>
          <i class="icon-home"></i> Dashboard
        </button>
      </li>
      <li>
        <button class:active={currentPage === 'setup'} on:click={() => currentPage = 'setup'}>
          <i class="icon-settings"></i> System Setup
        </button>
      </li>
      {#if timetableData}
        <li>
          <button class:active={currentPage === 'class-view'} on:click={() => currentPage = 'class-view'}>
            <i class="icon-table"></i> Class Timetables
          </button>
        </li>
        <li>
          <button class:active={currentPage === 'teacher-view'} on:click={() => currentPage = 'teacher-view'}>
            <i class="icon-user"></i> Teacher Schedules
          </button>
        </li>
      {/if}
    </ul>

    <div class="nav-footer">
      <button class="generate-btn" on:click={generateTimetable}>
        Generate New
      </button>
    </div>
  </nav>

  <!-- Main Content Area -->
  <main class="content">
    {#if error}
      <div class="error-banner">{error}</div>
    {/if}

    {#if showWelcome}
      <div class="welcome-notification">
        <span class="welcome-icon">👋</span>
        <span class="welcome-text">{welcomeMessage}</span>
        <button class="welcome-close" on:click={() => showWelcome = false}>×</button>
      </div>
    {/if}
    
    {#if currentPage === 'home'}
      <div class="dashboard">
        <header>
          <h1>Welcome to {collegeName}</h1>
          <p>Professional Timetable Management System</p>
        </header>

        <div class="stats-grid">
          <div class="stat-card">
            <h3>{formClasses.length}</h3>
            <p>Total Classes</p>
          </div>
          <div class="stat-card">
            <h3>{formTeachers.length}</h3>
            <p>Faculty Members</p>
          </div>
          <div class="stat-card">
            <h3>{timetableData ? 'Ready' : 'Not Generated'}</h3>
            <p>Schedule Status</p>
          </div>
        </div>

        <div class="quick-actions">
          <h2>Quick Actions</h2>
          <div class="action-buttons">
            <button on:click={() => currentPage = 'setup'}>Configure System</button>
            <button on:click={generateTimetable} class="primary">Run Scheduler</button>
          </div>
        </div>
      </div>

    {:else if currentPage === 'setup'}
      <div class="setup-page">
        <h1>System Configuration</h1>
        
        <section class="config-card">
          <h2>College Branding</h2>
          <div class="form-row">
            <div class="input-group">
              <label for="college-name">College Name</label>
              <input id="college-name" type="text" bind:value={collegeName} />
            </div>
          </div>
        </section>

        <div class="setup-grid">
          <section class="config-card">
            <h2>Add Class</h2>
            <input type="text" placeholder="Class Name (e.g. SE)" bind:value={newClass.name} />
            <textarea placeholder="Subjects (comma separated)" bind:value={newClass.lectures}></textarea>
            <textarea placeholder="Practicals (comma separated)" bind:value={newClass.practicals}></textarea>
            <input type="text" placeholder="Batches (A,B,C)" bind:value={newClass.batches} />
            <button on:click={addClass}>Add Class</button>
            
            <div class="list-preview">
              {#each formClasses as cls, i}
                <div class="item">
                  <span>{cls.name}</span>
                  <button on:click={() => formClasses = formClasses.filter((_, idx) => idx !== i)}>×</button>
                </div>
              {/each}
            </div>
          </section>

          <section class="config-card">
            <h2>Add Teacher</h2>
            <input type="text" placeholder="Short Name" bind:value={newTeacher.name} />
            <input type="text" placeholder="Full Name" bind:value={newTeacher.fullName} />
            <textarea placeholder="Expertise Subjects" bind:value={newTeacher.subjects}></textarea>
            <button on:click={addTeacher}>Add Teacher</button>

            <div class="list-preview">
              {#each formTeachers as t, i}
                <div class="item">
                  <span>{t.name}</span>
                  <button on:click={() => formTeachers = formTeachers.filter((_, idx) => idx !== i)}>×</button>
                </div>
              {/each}
            </div>
          </section>
        </div>
      </div>

    {:else if currentPage === 'class-view'}
      <div class="timetable-page">
        <header class="view-header">
          <h1>Weekly Class Timetable</h1>
          <div class="controls">
            <select bind:value={selectedClass}>
              {#each classes as cls}
                <option value={cls}>{cls}</option>
              {/each}
            </select>
            <button class="export-btn" on:click={() => exportPDF(`${selectedClass} Timetable`, 'class-tt')}>
              Download PDF
            </button>
          </div>
        </header>

        <div class="table-container">
          <table id="class-tt">
            <thead>
              <tr>
                <th>Time Slot</th>
                {#each DAYS as day}
                  <th>{day}</th>
                {/each}
              </tr>
            </thead>
            <tbody>
              {#each TIMESLOTS as slot}
                <tr>
                  <td class="time-col">{format12h(slot)}</td>
                  {#each DAYS as day}
                    {#if isProjectDay(selectedClass, day)}
                      {#if slot === TIMESLOTS[0]}
                        <td rowspan={TIMESLOTS.length} class="project-cell">
                          PROJECT DAY
                        </td>
                      {/if}
                    {:else}
                      <td class:lunch={timetableData.timetable[selectedClass][day][slot] === 'Lunch Break'}>
                        {timetableData.timetable[selectedClass][day][slot] || '-'}
                      </td>
                    {/if}
                  {/each}
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>

    {:else if currentPage === 'teacher-view'}
      <div class="timetable-page">
        <header class="view-header">
          <h1>Weekly Teacher Schedule</h1>
          <div class="controls">
            <select bind:value={selectedTeacher}>
              {#each teachers as t}
                <option value={t.name}>{t.fullName}</option>
              {/each}
            </select>
            <button class="export-btn" on:click={() => exportPDF(`${selectedTeacher} Schedule`, 'teacher-tt')}>
              Download PDF
            </button>
          </div>
        </header>

        <div class="table-container">
          <table id="teacher-tt">
            <thead>
              <tr>
                <th>Time Slot</th>
                {#each DAYS as day}
                  <th>{day}</th>
                {/each}
              </tr>
            </thead>
            <tbody>
              {#each TIMESLOTS as slot}
                <tr>
                  <td class="time-col">{format12h(slot)}</td>
                  {#each DAYS as day}
                    <td class:busy={teacherSchedule[day]?.[slot] && teacherSchedule[day]?.[slot] !== 'Lunch Break'}
                        class:lunch={teacherSchedule[day]?.[slot] === 'Lunch Break'}>
                      {teacherSchedule[day]?.[slot] || 'Free'}
                    </td>
                  {/each}
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
  </main>
</div>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background-color: #f8fafc;
    color: #1e293b;
    font-size: 16px;
    line-height: 1.6;
  }

  .app-container {
    display: flex;
    min-height: 100vh;
  }

  /* Sidebar */
  .sidebar {
    width: 260px;
    background: #1e293b;
    color: white;
    display: flex;
    flex-direction: column;
    padding: 1.5rem;
    position: fixed;
    height: 100vh;
    box-shadow: 4px 0 10px rgba(0,0,0,0.1);
  }

  .logo-area {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 2.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }

  .college-title {
    font-weight: 700;
    font-size: 1.2rem;
    line-height: 1.3;
  }

  .nav-links {
    list-style: none;
    padding: 0;
    margin: 0;
    flex-grow: 1;
  }

  .nav-links button {
    width: 100%;
    text-align: left;
    background: none;
    border: none;
    color: #94a3b8;
    padding: 0.85rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.2s;
    margin-bottom: 0.5rem;
    line-height: 1.5;
  }

  .nav-links button:hover {
    background: rgba(255,255,255,0.05);
    color: white;
  }

  .nav-links button.active {
    background: #3b82f6;
    color: white;
  }

  .nav-footer {
    margin-top: auto;
    padding-top: 1rem;
  }

  .generate-btn {
    width: 100%;
    background: #10b981;
    color: white;
    border: none;
    padding: 0.75rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .generate-btn:hover { background: #059669; }

  /* Main Content */
  .content {
    flex-grow: 1;
    margin-left: 260px;
    padding: 2.5rem;
    max-width: 1200px;
  }

  .error-banner {
    background: #fee2e2;
    color: #dc2626;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    border: 1px solid #fecaca;
  }

  /* Dashboard */
  .dashboard header h1 { font-size: 2.2rem; margin-bottom: 0.5rem; line-height: 1.3; }
  .dashboard header p { color: #64748b; font-size: 1.1rem; line-height: 1.5; }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2.5rem 0;
  }

  .stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    text-align: center;
  }

  .stat-card h3 { font-size: 2.2rem; color: #3b82f6; margin: 0; line-height: 1.2; }
  .stat-card p { color: #64748b; margin-top: 0.5rem; font-size: 1rem; line-height: 1.5; }

  /* Config Cards */
  .config-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
  }

  .config-card h2 { font-size: 1.4rem; margin-bottom: 1.25rem; color: #334155; line-height: 1.4; }
  
  input, textarea, select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    margin-bottom: 1rem;
    font-size: 1rem;
    line-height: 1.5;
  }

  .setup-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }

  .list-preview {
    margin-top: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .item {
    background: #f1f5f9;
    padding: 0.4rem 0.85rem;
    border-radius: 999px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.95rem;
    line-height: 1.5;
  }

  .item button {
    border: none;
    background: none;
    color: #ef4444;
    cursor: pointer;
    font-weight: bold;
  }

  /* Timetable View */
  .view-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .controls { display: flex; gap: 1rem; }
  .controls select { width: auto; margin: 0; }

  .export-btn {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.5rem 1.25rem;
    border-radius: 6px;
    cursor: pointer;
  }

  .table-container {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
    line-height: 1.5;
  }

  th {
    background: #f8fafc;
    padding: 1rem;
    text-align: left;
    border-bottom: 2px solid #e2e8f0;
    font-weight: 600;
  }

  td {
    padding: 1rem;
    border-bottom: 1px solid #f1f5f9;
    vertical-align: top;
  }

  .time-col {
    background: #f8fafc;
    font-weight: 600;
    width: 150px;
    color: #64748b;
  }

  .project-cell {
    background: #fef2f2;
    color: #ef4444;
    font-weight: 700;
    text-align: center;
    vertical-align: middle;
    letter-spacing: 0.1em;
  }

  .lunch {
    background: #fffbeb;
    color: #d97706;
    font-style: italic;
    text-align: center;
  }

  .busy {
    background: #eff6ff;
    color: #2563eb;
    font-weight: 500;
  }

  .welcome-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    z-index: 1000;
    animation: slideIn 0.3s ease;
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  .welcome-icon {
    font-size: 1.8rem;
  }

  .welcome-text {
    font-weight: 500;
    font-size: 1rem;
    line-height: 1.5;
  }

  .welcome-close {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.2rem;
    line-height: 1;
    margin-left: 0.5rem;
    transition: background 0.2s;
  }

  .welcome-close:hover {
    background: rgba(255, 255, 255, 0.3);
  }

  @media (max-width: 1024px) {
    .setup-grid { grid-template-columns: 1fr; }
    .sidebar { width: 80px; padding: 1rem 0.5rem; }
    .college-title { display: none; }
    .content { margin-left: 80px; }
  }
</style>
