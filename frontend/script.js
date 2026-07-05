let classIndex = 0;
let teacherIndex = 0;
let optionalIndex = 0;

function addClassForm() {
  const container = document.getElementById("classesContainer");
  const div = document.createElement("div");
  div.innerHTML = `
    <h3>Class</h3>
    <label>Name:</label><input name="className${classIndex}" placeholder="Class name"><br>
    <label>Lectures (comma separated):</label><input name="classLectures${classIndex}" placeholder="Lecture1, Lecture2"><br>
    <label>Practicals (comma separated):</label><input name="classPracticals${classIndex}" placeholder="Practical1, Practical2"><br>
    <label>Batches (comma separated):</label><input name="classBatches${classIndex}" placeholder="B1, B2, B3, B4"><br><hr>`;
  container.appendChild(div);
  classIndex++;
}

function addTeacherForm() {
  const container = document.getElementById("teachersContainer");
  const div = document.createElement("div");
  div.innerHTML = `
    <h3>Teacher</h3>
    <label>Short Name:</label><input name="teacherName${teacherIndex}" placeholder="Short name"><br>
    <label>Full Name:</label><input name="teacherFullName${teacherIndex}" placeholder="Full name"><br>
    <label>Subjects (comma separated):</label><input name="teacherSubjects${teacherIndex}" placeholder="Sub1, Sub2"><br><hr>`;
  container.appendChild(div);
  teacherIndex++;
}

function addOptionalSubjectForm() {
  const container = document.getElementById("optionalSubjectsContainer");
  const div = document.createElement("div");
  div.innerHTML = `
    <h3>Optional Subject</h3>
    <label>Class Name:</label><input name="optionalClassName${optionalIndex}" placeholder="Class name"><br>
    <label>Batch Name:</label><input name="optionalBatch${optionalIndex}" placeholder="Batch name"><br>
    <label>Subject Name:</label><input name="optionalSubject${optionalIndex}" placeholder="Subject name"><br><hr>`;
  container.appendChild(div);
  optionalIndex++;
}

function submitData() {
  const classes = [];
  for (let i = 0; i < classIndex; i++) {
    const name = document.querySelector(`input[name="className${i}"]`).value.trim();
    const lectures = document.querySelector(`input[name="classLectures${i}"]`).value.split(',').map(s => s.trim()).filter(Boolean);
    const practicals = document.querySelector(`input[name="classPracticals${i}"]`).value.split(',').map(s => s.trim()).filter(Boolean);
    const batches = document.querySelector(`input[name="classBatches${i}"]`).value.split(',').map(s => s.trim()).filter(Boolean);
    if (name) {
      classes.push({ name, lectures, practicals, batches });
    }
  }

  const teachers = [];
  for (let i = 0; i < teacherIndex; i++) {
    const name = document.querySelector(`input[name="teacherName${i}"]`).value.trim();
    const fullName = document.querySelector(`input[name="teacherFullName${i}"]`).value.trim();
    const subjects = document.querySelector(`input[name="teacherSubjects${i}"]`).value.split(',').map(s => s.trim()).filter(Boolean);
    if (name) {
      teachers.push({ name, fullName, subjects });
    }
  }

  const optionalSubjects = [];
  for (let i = 0; i < optionalIndex; i++) {
    const className = document.querySelector(`input[name="optionalClassName${i}"]`).value.trim();
    const batch = document.querySelector(`input[name="optionalBatch${i}"]`).value.trim();
    const subject = document.querySelector(`input[name="optionalSubject${i}"]`).value.trim();
    if (className && batch && subject) {
      optionalSubjects.push({ className, batch, subject });
    }
  }

  fetch("/api/bulk-add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      bulkClasses: JSON.stringify(classes),
      bulkTeachers: JSON.stringify(teachers),
      bulkOptionalSubjects: JSON.stringify(optionalSubjects)
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      alert("Error: " + data.error);
    } else {
      alert(data.message);
      generateTimetable();
    }
  })
  .catch(err => {
    alert("Error: " + err);
  });
}

function generateTimetable() {
  fetch("/api/timetable")
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        document.getElementById("timetable").innerHTML = `<p style="color:red">${data.error}</p>`;
      } else {
        renderTimetableTable(data.timetable);
        renderTeacherReference(data.teachers);
      }
    });
}

function renderTimetableTable(data) {
  const timeslots = [
    "10:00 - 11:00","11:00 - 12:00","12:00 - 13:00",
    "13:00 - 14:00","14:00 - 15:00","15:00 - 16:00","16:00 - 17:00"
  ];
  let html = "";
  for (let cls in data) {
    html += `<h2>${cls} Timetable</h2>`;
    html += `<table border="1" cellpadding="5" cellspacing="0">`;
    html += "<tr><th>Day</th>";
    for (let slot of timeslots) html += `<th>${slot}</th>`;
    html += "</tr>";
    for (let day of ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]) {
      html += `<tr><td>${day}</td>`;
      for (let slot of timeslots) {
        let activity = data[cls][day][slot] || "Free";
        if (activity === "MERGED") continue; // skip merged slot
        if (activity.includes("/") && slot === "10:00 - 11:00") {
          html += `<td colspan="2">${activity}</td>`;
        } else {
          html += `<td>${activity}</td>`;
        }
      }
      html += "</tr>";
    }
    html += "</table><br>";
  }
  document.getElementById("timetable").innerHTML = html;
}

function renderTeacherReference(teachers) {
  if (!teachers || teachers.length === 0) {
    document.getElementById("teacherReference").innerHTML = "<p>No teachers available</p>";
    return;
  }
  let html = "<table border='1' cellpadding='5' cellspacing='0'>";
  html += "<tr><th>Short Name</th><th>Full Name</th><th>Subjects</th></tr>";
  for (let t of teachers) {
    html += `<tr><td>${t.name}</td><td>${t.fullName || "-"}</td><td>${t.subjects ? t.subjects.join(", ") : "-"}</td></tr>`;
  }
  html += "</table>";
  document.getElementById("teacherReference").innerHTML = html;
}

// Export timetable + teacher reference to PDF
function exportPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  doc.setFontSize(16);
  doc.text("University Timetable", 14, 20);

  const tables = document.getElementById("timetable").querySelectorAll("table");
  let yPos = 30;
  tables.forEach((table) => {
    doc.autoTable({ html: table, startY: yPos, theme: "grid", headStyles: { fillColor: [52, 152, 219] }, styles: { fontSize: 8 } });
    yPos = doc.lastAutoTable.finalY + 15;
  });

  const teacherRef = document.getElementById("teacherReference").querySelector("table");
  if (teacherRef) {
    doc.text("Teacher Reference", 14, yPos);
    doc.autoTable({ html: teacherRef, startY: yPos + 5, theme: "grid", headStyles: { fillColor: [39, 174, 96] }, styles: { fontSize: 9 } });
  }

  doc.save("University_Timetable.pdf");
}
