document.addEventListener("DOMContentLoaded", function() {
  let expCount = document.querySelectorAll(".experience-item").length || 1;
  let eduCount = document.querySelectorAll(".education-item").length || 1;
  let projCount = document.querySelectorAll(".projects-item").length || 1;
  let certCount = document.querySelectorAll(".certification-item").length || 1;

  document.getElementById("add-experience-btn").addEventListener("click", () => {
    const container = document.getElementById("experience-container");
    let div = document.createElement("div");
    div.classList.add("border", "rounded", "mb-3", "p-3", "experience-item");
    div.dataset.index = expCount;
    div.innerHTML = `
      <input type="text" name="experience-${expCount}-title" placeholder="Job Title" class="form-control mb-1" required>
      <input type="text" name="experience-${expCount}-company" placeholder="Company" class="form-control mb-1">
      <input type="text" name="experience-${expCount}-start_date" placeholder="Start Date" class="form-control mb-1">
      <input type="text" name="experience-${expCount}-end_date" placeholder="End Date" class="form-control mb-1">
      <div class="bullets mb-1" data-exp-index="${expCount}">
        <label class="small">Achievements:</label>
        <input type="text" name="experience-${expCount}-bullets-0" required class="form-control form-control-sm my-1">
        <button type="button" class="btn btn-link btn-sm add-bullet-btn" data-exp-index="${expCount}">Add Bullet</button>
      </div>
      <button type="button" class="btn btn-danger btn-sm remove-experience-btn" data-exp-index="${expCount}">Remove</button>
      <hr>
    `;
    container.appendChild(div);
    expCount++;
  });
  document.getElementById("add-education-btn").addEventListener("click", () => {
    const container = document.getElementById("education-container");
    let div = document.createElement("div");
    div.classList.add("border", "rounded", "mb-3", "p-3", "education-item");
    div.dataset.index = eduCount;
    div.innerHTML = `
      <input type="text" name="education-${eduCount}-degree" placeholder="Degree" class="form-control mb-1">
      <input type="text" name="education-${eduCount}-school" placeholder="School" class="form-control mb-1">
      <input type="text" name="education-${eduCount}-start_date" placeholder="Start Date" class="form-control mb-1">
      <input type="text" name="education-${eduCount}-end_date" placeholder="End Date" class="form-control mb-1">
      <textarea name="education-${eduCount}-description" class="form-control mb-1" placeholder="Details"></textarea>
      <button type="button" class="btn btn-danger btn-sm remove-education-btn" data-edu-index="${eduCount}">Remove</button>
      <hr>
    `;
    container.appendChild(div);
    eduCount++;
  });
  document.getElementById("add-project-btn").addEventListener("click", () => {
    const container = document.getElementById("projects-container");
    let div = document.createElement("div");
    div.classList.add("border", "rounded", "mb-3", "p-3", "projects-item");
    div.dataset.index = projCount;
    div.innerHTML = `
      <input type="text" name="projects-${projCount}-title" placeholder="Title" class="form-control mb-1">
      <input type="text" name="projects-${projCount}-date" placeholder="Date" class="form-control mb-1">
      <textarea name="projects-${projCount}-description" class="form-control mb-1" placeholder="Description"></textarea>
      <button type="button" class="btn btn-danger btn-sm remove-project-btn" data-proj-index="${projCount}">Remove</button>
      <hr>
    `;
    container.appendChild(div);
    projCount++;
  });
  document.getElementById("add-certification-btn").addEventListener("click", () => {
    const container = document.getElementById("certifications-container");
    let div = document.createElement("div");
    div.classList.add("border", "rounded", "mb-3", "p-3", "certification-item");
    div.dataset.index = certCount;
    div.innerHTML = `
      <input type="text" name="certifications-${certCount}-name" placeholder="Certification Name" class="form-control mb-1">
      <input type="text" name="certifications-${certCount}-authority" placeholder="Authority" class="form-control mb-1">
      <input type="text" name="certifications-${certCount}-date" placeholder="Date" class="form-control mb-1">
      <button type="button" class="btn btn-danger btn-sm remove-certification-btn" data-cert-index="${certCount}">Remove</button>
      <hr>
    `;
    container.appendChild(div);
    certCount++;
  });
  document.body.addEventListener("click", function(e) {
    if (e.target.classList.contains("remove-experience-btn")) {
      const idx = e.target.dataset.expIndex;
      document.querySelector(`.experience-item[data-index="${idx}"]`).remove();
    } else if (e.target.classList.contains("remove-education-btn")) {
      const idx = e.target.dataset.eduIndex;
      document.querySelector(`.education-item[data-index="${idx}"]`).remove();
    } else if (e.target.classList.contains("remove-project-btn")) {
      const idx = e.target.dataset.projIndex;
      document.querySelector(`.projects-item[data-index="${idx}"]`).remove();
    } else if (e.target.classList.contains("remove-certification-btn")) {
      const idx = e.target.dataset.certIndex;
      document.querySelector(`.certification-item[data-index="${idx}"]`).remove();
    } else if (e.target.classList.contains("add-bullet-btn")) {
      const expId = e.target.dataset.expIndex;
      const bulletsDiv = document.querySelector(`.experience-item[data-index="${expId}"] .bullets`);
      const bulletCount = bulletsDiv.querySelectorAll("input").length;
      let input = document.createElement("input");
      input.type = "text";
      input.name = `experience-${expId}-bullets-${bulletCount}`;
      input.classList.add("form-control", "form-control-sm", "my-1");
      bulletsDiv.insertBefore(input, e.target);
      bulletsDiv.insertBefore(document.createElement("br"), e.target);
    }
  });
});
