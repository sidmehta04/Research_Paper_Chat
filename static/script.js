document.addEventListener('DOMContentLoaded', function() {
    const downloadBtn = document.getElementById('downloadBtn');
    const processBtn = document.getElementById('processBtn');
    const askBtn = document.getElementById('askBtn');
    const pdfDir = document.getElementById('pdfDir');
    const pdfFile = document.getElementById('pdfFile');

    let currentSummary = '';
    let currentContent = '';

    if (downloadBtn) downloadBtn.addEventListener('click', downloadPapers);
    if (processBtn) processBtn.addEventListener('click', processPDF);
    if (askBtn) askBtn.addEventListener('click', askQuestion);
    if (pdfDir) pdfDir.addEventListener('change', loadPDFFiles);

    loadPDFDirs();

    function showLoading(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'flex';
        } else {
            console.warn(`Loading element with id '${id}' not found.`);
        }
    }

    function hideLoading(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        } else {
            console.warn(`Loading element with id '${id}' not found.`);
        }
    }

    function downloadPapers() {
        const targetDate = document.getElementById('targetDate')?.value;
        const paperLimit = parseInt(document.getElementById('paperLimit')?.value || '0');
        
        showLoading('downloadLoading');
        fetch('/download_papers', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({date: targetDate, paperLimit: paperLimit})
        })
        .then(response => response.json())
        .then(data => {
            const downloadStatus = document.getElementById('downloadStatus');
            if (downloadStatus) {
                downloadStatus.textContent = `Papers downloaded to ${data.downloadDir}`;
            }
            loadPDFDirs();
        })
        .catch(error => console.error('Error:', error))
        .finally(() => hideLoading('downloadLoading'));
    }

    function loadPDFDirs() {
        fetch('/get_pdf_dirs')
        .then(response => response.json())
        .then(dirs => {
            if (pdfDir) {
                pdfDir.innerHTML = dirs.map(dir => `<option value="${dir}">${dir}</option>`).join('');
                loadPDFFiles();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function loadPDFFiles() {
        const selectedDir = pdfDir?.value;
        if (!selectedDir) return;

        fetch('/get_pdf_files', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({selectedDir: selectedDir})
        })
        .then(response => response.json())
        .then(files => {
            if (pdfFile) {
                pdfFile.innerHTML = files.map(file => `<option value="${file}">${file}</option>`).join('');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function processPDF() {
        const selectedDir = pdfDir?.value;
        const selectedFile = pdfFile?.value;
        if (!selectedDir || !selectedFile) return;
        
        showLoading('processLoading');
        fetch('/process_pdf', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({selectedDir: selectedDir, selectedFile: selectedFile})
        })
        .then(response => response.json())
        .then(data => {
            const summaryContent = document.getElementById('summaryContent');
            if (summaryContent) {
                if (data.status === 'success') {
                    summaryContent.textContent = data.summary;
                    currentSummary = data.summary;
                    currentContent = data.content;
                } else {
                    summaryContent.textContent = data.message;
                }
            }
        })
        .catch(error => console.error('Error:', error))
        .finally(() => hideLoading('processLoading'));
    }

    function askQuestion() {
        const question = document.getElementById('question')?.value;
        if (!question) return;
        
        showLoading('askLoading');
        fetch('/ask_question', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: question, summary: currentSummary, content: currentContent})
        })
        .then(response => response.json())
        .then(data => {
            const answerElement = document.getElementById('answer');
            if (answerElement) {
                answerElement.textContent = data.answer;
            }
        })
        .catch(error => console.error('Error:', error))
        .finally(() => hideLoading('askLoading'));
    }
});