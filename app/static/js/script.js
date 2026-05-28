const videoInput = document.getElementById("videoInput");
const processBtn = document.getElementById("processBtn");

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
      clearInterval(interval);

      // TODO: Only display results block after results returned from server
      setTimeout(() => {
        resultsCard.style.display = "block";
        resultsCard.scrollIntoView({
          behavior: "smooth",
        });
      }, 500);
    }
  }, 1000);
}

/*
let progress = 0;

const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const processBtn = document.getElementById("processBtn");
const resultsCard = document.getElementById("resultsCard");

processBtn.addEventListener("click", () => {
  progress = 0;
  resultsCard.style.display = "none";

  const interval = setInterval(() => {
    if (progress < 100) {
      progress += 5;
      progressBar.style.width = progress + "%";
      progressText.innerText = progress + "%";
    } else {
      clearInterval(interval);

      setTimeout(() => {
        resultsCard.style.display = "block";
        resultsCard.scrollIntoView({
          behavior: "smooth",
        });
      }, 500);
    }
  }, 200);
});
*/
