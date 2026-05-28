const dropZone = document.querySelector(".drop-zone");
const videoInput = document.getElementById("videoInput");
const processBtn = document.getElementById("processBtn");

// Drop zone for drag & drop
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragging");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragging");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragging");

  const files = e.dataTransfer.files;

  if (files.length > 0) {
    videoInput.files = files;

    console.log("File selected:", files[0].name);

    updateDropUI(files[0]);
  }
});

function updateDropUI(file) {
  const title = document.querySelector(".drop-title");
  title.textContent = `Selected: ${file.name}`;
}

// Upload and process video button

processBtn.onclick = async () => {
  // Ensure a file is selected
  if (videoInput.files.length === 0) {
    alert("Please select a file first!");
    return;
  }

  // Create form data
  const formData = new FormData();

  // Add video
  formData.append("video", videoInput.files[0]);

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    const jobId = data.job_id;

    trackProgress(jobId);

    processBtn.disabled = true;
    processBtn.innerText = "Processing...";
  } catch (err) {
    console.error(err);
    alert("Upload failed.");
  }
};

const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");

async function trackProgress(jobId) {
  const interval = setInterval(async () => {
    const res = await fetch(`/api/progress/${jobId}`);
    const data = await res.json();

    console.log(data.progress);

    const visualProgress = Math.max(Math.min(data.progress, 100), 0);

    progressBar.style.width = visualProgress + "%";
    progressText.innerText = visualProgress + "%";

    if (data.progress === 100 || data.status !== "ok") {
      processBtn.disabled = false;
      processBtn.innerText = "Upload & Process";
      clearInterval(interval);
      await retrieveResult(jobId);
    }
  }, 1000);
}

const congestionLabels = {
  [-1]: "Unknown",
  0: "Light",
  1: "Moderate",
  2: "Heavy",
};

async function retrieveResult(jobId) {
  const res = await fetch(`/api/result/${jobId}`);

  if (!res.ok) {
    console.error("Failed to retrieve result");
    return;
  }

  const data = await res.json();

  /*
  data format {
    "status": "ok" | "unknown",
    "video_url": String,
    "total_cars": Number,
    "cars_per_min": Number,
    "congestion_rating": -1 | 0 | 1 | 2
  }
  */

  const valueTotalCars = document.getElementById("valueTotalCars");

  const valueCarsPerMin = document.getElementById("valueCarsPerMin");

  const valueCongestionRating = document.getElementById(
    "valueCongestionRating",
  );

  const resultVideo = document.getElementById("resultVideo");

  valueTotalCars.textContent = data.total_cars;

  valueCarsPerMin.textContent = data.cars_per_min;

  // Update text
  const rating = data.congestion_rating || "unknown";
  valueCongestionRating.textContent =
    rating.charAt(0).toUpperCase() + rating.slice(1);

  // Overwrite classes
  valueCongestionRating.className = "stat-value";
  valueCongestionRating.classList.add(`congestion-${data.congestion_rating}`);

  resultVideo.src = data.video_url;
  resultVideo.load();

  setTimeout(() => {
    resultsCard.style.display = "block";
    resultsCard.scrollIntoView({
      behavior: "smooth",
    });
  }, 500);
}

// Handle reset button

const resetBtn = document.getElementById("resetBtn");

resetBtn.addEventListener("click", () => {
  // Clear file input
  videoInput.value = "";

  // Reset drop zone text
  document.querySelector(".drop-title").textContent =
    "Drag & Drop Your Video File";

  // Reset progress
  progressBar.style.width = "0%";
  progressText.textContent = "0%";

  // Hide results
  resultsCard.style.display = "none";

  // Clear video
  const resultVideo = document.getElementById("resultVideo");
  resultVideo.pause();
  resultVideo.removeAttribute("src");
  resultVideo.load();

  // Reset stats
  document.getElementById("valueTotalCars").textContent = "0";
  document.getElementById("valueCarsPerMin").textContent = "0";
  document.getElementById("valueCongestionRating").textContent = "Unknown";

  const ratingEl = document.getElementById("valueCongestionRating");
  ratingEl.className = "stat-value congestion-unknown";

  console.log("UI reset complete");
});
