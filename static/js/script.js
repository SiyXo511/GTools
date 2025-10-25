// This file is ready for your JavaScript code.
// We can add form submission handling with Fetch API later.
document.addEventListener('DOMContentLoaded', () => {
    const listForm = document.getElementById('list-form');
    const jsonForm = document.getElementById('json-form');
    const fromJsonForm = document.getElementById('from-json-form');
    const resultContainer = document.getElementById('result-container');
    const resultContent = document.getElementById('result-content');
    const copyBtn = document.getElementById('copy-btn');
    const submitBtn = listForm ? listForm.querySelector('button[type="submit"]') : null;
    const originalBtnText = submitBtn ? submitBtn.innerHTML : '';

    const handleFormSubmit = async (event, form, url) => {
        event.preventDefault();
        
        const formData = new FormData(form);
        const submitButton = form.querySelector('button');
        const originalButtonText = submitButton.textContent;
        const copyBtn = document.getElementById('copy-btn');

        submitButton.textContent = 'Processing...';
        submitButton.disabled = true;
        resultContainer.style.display = 'none';
        if (copyBtn) copyBtn.style.display = 'none'; // Hide on new submission

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (response.ok && resultContent) {
                resultContent.innerHTML = ''; // Clear previous results
                if (result.download_url) {
                    const downloadLink = document.createElement('a');
                    downloadLink.id = 'download-link';
                    downloadLink.href = result.download_url;
                    downloadLink.textContent = `Download ${result.download_url.split('/').pop()}`;
                    downloadLink.setAttribute('download', '');
                    resultContent.appendChild(downloadLink);
                } else if (result.data) {
                    const pre = document.createElement('pre');
                    pre.className = 'result-display';
                    // Check if data is an object/array to stringify, or a pre-formatted string
                    if (typeof result.data === 'object' && result.data !== null) {
                        pre.textContent = JSON.stringify(result.data, null, 2);
                    } else {
                        pre.textContent = result.data;
                    }
                    resultContent.appendChild(pre);
                    if (copyBtn) copyBtn.style.display = 'inline-block'; // Show button when display
                }
                resultContainer.style.display = 'block';
            } else {
                alert(`Error: ${result.error || 'An unknown error occurred.'}`);
            }
        } catch (error) {
            console.error('Submission error:', error);
            alert('An error occurred while submitting the form. Please check the console.');
        } finally {
            submitButton.textContent = originalButtonText;
            submitButton.disabled = false;
        }
    };

    if (listForm) {
        listForm.addEventListener('submit', (event) => {
            handleFormSubmit(event, listForm, '/convert/list');
        });
    }

    if (jsonForm) {
        jsonForm.addEventListener('submit', (event) => {
            handleFormSubmit(event, jsonForm, '/convert/json');
        });
    }

    if (fromJsonForm) {
        fromJsonForm.addEventListener('submit', (event) => {
            handleFormSubmit(event, fromJsonForm, '/convert/from-json');
        });
    }

    const listFileInput = document.getElementById('list-file');
    if (listFileInput) {
        listFileInput.addEventListener('change', (e) => handleFileSelect(e, 'columns-container'));
    }

    const jsonFileInput = document.getElementById('json-file');
    if (jsonFileInput) {
        jsonFileInput.addEventListener('change', (e) => handleFileSelect(e, 'json-columns-container', 'json-select-all-btn', 'checkbox'));
    }

    const selectAllBtn = document.getElementById('json-select-all-btn');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            const columnsContainer = document.getElementById('json-columns-container');
            const checkboxes = columnsContainer.querySelectorAll('input[type="checkbox"]');
            if (checkboxes.length === 0) return;

            const allSelected = Array.from(checkboxes).every(cb => cb.checked);

            checkboxes.forEach(cb => {
                cb.checked = !allSelected;
            });

            selectAllBtn.textContent = allSelected ? 'Select All' : 'Deselect All';
        });
    }

    // --- Added for Copy Button ---
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const resultContent = document.querySelector('#result-content pre');
            if (resultContent) {
                navigator.clipboard.writeText(resultContent.textContent).then(() => {
                    const originalIcon = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        copyBtn.innerHTML = originalIcon;
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    alert('Failed to copy text.');
                });
            }
        });
    }
});

async function handleFileSelect(event, containerId, selectAllBtnId = null, inputType = 'radio') {
    const file = event.target.files[0];
    const columnsContainer = document.getElementById(containerId);
    const selectAllBtn = selectAllBtnId ? document.getElementById(selectAllBtnId) : null;
    
    if (!file || !columnsContainer) return;

    columnsContainer.innerHTML = '<p class="placeholder-text">Loading columns...</p>';
    if (selectAllBtn) selectAllBtn.style.display = 'none';
    
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/get-headers', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (response.ok) {
            columnsContainer.innerHTML = ''; // Clear container
            if (result.headers && result.headers.length > 0) {
                result.headers.forEach(header => {
                    const selectionWrapper = document.createElement('div');
                    selectionWrapper.classList.add('selection-wrapper');
                    
                    const input = document.createElement('input');
                    input.type = inputType;
                    input.id = `col-${containerId}-${header.replace(/\s+/g, '-')}`;
                    input.name = inputType === 'radio' ? 'column_name' : 'column_names';
                    input.value = header;

                    const label = document.createElement('label');
                    label.htmlFor = input.id;
                    label.textContent = header;

                    selectionWrapper.appendChild(input);
                    selectionWrapper.appendChild(label);
                    columnsContainer.appendChild(selectionWrapper);
                });
                if (selectAllBtn) {
                    selectAllBtn.style.display = 'inline-block';
                    selectAllBtn.textContent = 'Select All';
                }
            } else {
                columnsContainer.innerHTML = '<p class="placeholder-text error-text">No columns found in the file.</p>';
            }
        } else {
            columnsContainer.innerHTML = `<p class="placeholder-text error-text">Error: ${result.error || 'Could not parse file.'}</p>`;
        }
    } catch (error) {
        console.error('Error fetching headers:', error);
        columnsContainer.innerHTML = '<p class="placeholder-text error-text">An unexpected error occurred. Check console for details.</p>';
    }
}

// Clipboard form handling
document.addEventListener('DOMContentLoaded', () => {
    const clipboardForm = document.getElementById('clipboard-form');
    const actionToList = document.getElementById('action-to-list');
    const actionFromJson = document.getElementById('action-from-json');
    const toListOptions = document.getElementById('to-list-options');
    const fromJsonOptions = document.getElementById('from-json-options');
    const listFileFormatGroup = document.getElementById('list-file-format-group');
    const jsonFileFormatGroup = document.getElementById('json-file-format-group');
    const listOutputFile = document.getElementById('list-output-file');
    const jsonOutputFile = document.getElementById('json-output-file');

    // Handle action selection
    if (actionToList && actionFromJson) {
        actionToList.addEventListener('change', () => {
            toListOptions.style.display = 'block';
            fromJsonOptions.style.display = 'none';
        });

        actionFromJson.addEventListener('change', () => {
            toListOptions.style.display = 'none';
            fromJsonOptions.style.display = 'block';
        });
    }

    // Handle output method changes for list conversion
    if (listOutputFile) {
        listOutputFile.addEventListener('change', () => {
            listFileFormatGroup.style.display = 'block';
        });
    }

    const listOutputDisplay = document.getElementById('list-output-display');
    if (listOutputDisplay) {
        listOutputDisplay.addEventListener('change', () => {
            listFileFormatGroup.style.display = 'none';
        });
    }

    // Handle output method changes for JSON conversion
    if (jsonOutputFile) {
        jsonOutputFile.addEventListener('change', () => {
            jsonFileFormatGroup.style.display = 'block';
        });
    }

    const jsonOutputDisplay = document.getElementById('json-output-display');
    if (jsonOutputDisplay) {
        jsonOutputDisplay.addEventListener('change', () => {
            jsonFileFormatGroup.style.display = 'none';
        });
    }

    // Handle clipboard form submission
    if (clipboardForm) {
        clipboardForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const formData = new FormData(clipboardForm);
            const submitButton = clipboardForm.querySelector('button');
            const originalButtonText = submitButton.textContent;
            const resultContainer = document.getElementById('result-container');
            const resultContent = document.getElementById('result-content');
            const copyBtn = document.getElementById('copy-btn');

            submitButton.textContent = 'Processing...';
            submitButton.disabled = true;
            resultContainer.style.display = 'none';
            if (copyBtn) copyBtn.style.display = 'none';

            try {
                const response = await fetch('/convert/clipboard', {
                    method: 'POST',
                    body: formData,
                });

                const result = await response.json();

                if (response.ok && resultContent) {
                    resultContent.innerHTML = '';
                    if (result.download_url) {
                        const downloadLink = document.createElement('a');
                        downloadLink.id = 'download-link';
                        downloadLink.href = result.download_url;
                        downloadLink.textContent = `Download ${result.download_url.split('/').pop()}`;
                        downloadLink.setAttribute('download', '');
                        resultContent.appendChild(downloadLink);
                    } else if (result.data) {
                        const pre = document.createElement('pre');
                        pre.className = 'result-display';
                        if (typeof result.data === 'object' && result.data !== null) {
                            pre.textContent = JSON.stringify(result.data, null, 2);
                        } else {
                            pre.textContent = result.data;
                        }
                        resultContent.appendChild(pre);
                        if (copyBtn) copyBtn.style.display = 'inline-block';
                    }
                    resultContainer.style.display = 'block';
                } else {
                    alert(`Error: ${result.error || 'An unknown error occurred.'}`);
                }
            } catch (error) {
                console.error('Submission error:', error);
                alert('An error occurred while submitting the form. Please check the console.');
            } finally {
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
            }
        });
    }
});
