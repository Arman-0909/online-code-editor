document.addEventListener('DOMContentLoaded', () => {
    let editor;
    const openFiles = {}; // To store content of open files
    let activeFile = null;

    const fileListEl = document.getElementById('fileList');
    const tabsEl = document.querySelector('.tabs');
    const previewIframe = document.getElementById('preview-iframe');
    const outputEl = document.getElementById('output');

    function initializeEditor() {
        editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
            theme: 'dracula',
            lineNumbers: true,
            autoCloseBrackets: true,
            gutters: ["CodeMirror-linenumbers"],
        });

        editor.on('change', () => {
            if (activeFile && openFiles[activeFile]) {
                openFiles[activeFile].content = editor.getValue();
                updatePreview();
            }
        });
    }

    function getLanguageMode(filename) {
        const extension = filename.split('.').pop();
        switch (extension) {
            case 'html': return 'htmlmixed';
            case 'css': return 'css';
            case 'js': return 'javascript';
            case 'py': return 'python';
            case 'java': return 'text/x-java';
            case 'c': return 'text/x-csrc';
            case 'cpp': return 'text/x-c++src';
            case 'php': return 'php';
            case 'swift': return 'swift';
            case 'go': return 'go';
            default: return 'text/plain';
        }
    }

    function updatePreview() {
        if (activeFile && getLanguageMode(activeFile) === 'htmlmixed') {
            const htmlContent = openFiles[activeFile].content;
            const cssFile = Object.keys(openFiles).find(f => f.endsWith('.css'));
            const jsFile = Object.keys(openFiles).find(f => f.endsWith('.js'));

            let finalHtml = htmlContent;

            if (cssFile && openFiles[cssFile]) {
                finalHtml = `<style>${openFiles[cssFile].content}</style>${finalHtml}`;
            }
            if (jsFile && openFiles[jsFile]) {
                finalHtml = `${finalHtml}<script>${openFiles[jsFile].content}<\/script>`;
            }

            const iframeDoc = previewIframe.contentWindow.document;
            iframeDoc.open();
            iframeDoc.write(finalHtml);
            iframeDoc.close();
        }
    }

    async function openFile(filename) {
        if (openFiles[filename]) {
            switchTab(filename);
            return;
        }

        try {
            const response = await fetch(`/api/load/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify({ filename })
            });
            const data = await response.json();

            if (data.error) {
                console.error(data.error);
                return;
            }

            openFiles[filename] = { content: data.code, mode: getLanguageMode(filename) };
            createTab(filename);
            switchTab(filename);

        } catch (error) {
            console.error('Error loading file:', error);
        }
    }

    function createTab(filename) {
        const tab = document.createElement('div');
        tab.className = 'tab';
        tab.dataset.filename = filename;
        tab.textContent = filename;

        const closeBtn = document.createElement('i');
        closeBtn.dataset.feather = 'x';
        closeBtn.className = 'close-tab';
        closeBtn.onclick = (e) => {
            e.stopPropagation();
            closeTab(filename);
        };

        tab.appendChild(closeBtn);
        tab.onclick = () => switchTab(filename);
        tabsEl.appendChild(tab);
        feather.replace();
    }

    function switchTab(filename) {
        activeFile = filename;

        document.querySelectorAll('.tab').forEach(t => {
            t.classList.toggle('active', t.dataset.filename === filename);
        });

        editor.setValue(openFiles[filename].content);
        editor.setOption('mode', openFiles[filename].mode);
        CodeMirror.autoLoadMode(editor, openFiles[filename].mode);
        updatePreview();
    }

    function closeTab(filename) {
        delete openFiles[filename];
        const tabEl = document.querySelector(`.tab[data-filename="${filename}"]`);
        if (tabEl) {
            tabEl.remove();
        }

        if (activeFile === filename) {
            const nextFile = Object.keys(openFiles)[0];
            if (nextFile) {
                switchTab(nextFile);
            } else {
                editor.setValue('');
                activeFile = null;
            }
        }
    }

    async function updateFileList() {
        try {
            const response = await fetch('/api/list/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            const data = await response.json();
            fileListEl.innerHTML = '';
            if (data.files) {
                data.files.forEach(file => {
                    const fileEl = document.createElement('div');
                    fileEl.textContent = file;
                    fileEl.className = 'file-item';
                    fileEl.onclick = async () => await openFile(file);
                    fileListEl.appendChild(fileEl);
                });
            }
        } catch (error) {
            console.error('Error fetching file list:', error);
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function runCode() {
        if (!activeFile) {
            alert("Please open a file to run.");
            return;
        }

        const code = editor.getValue();
        const language = document.getElementById('languageSelect').value;

        fetch('/api/execute/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ code, language })
        })
        .then(response => response.json())
        .then(data => {
            outputEl.textContent = data.output || data.error;
        })
        .catch(error => {
            console.error('Error executing code:', error);
            outputEl.textContent = 'An error occurred.';
        });
    }

    async function saveFile() {
        if (!activeFile) {
            alert("Please open a file to save.");
            return;
        }

        const code = openFiles[activeFile].content;

        try {
            const response = await fetch('/api/save/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify({ filename: activeFile, code })
            });
            const data = await response.json();
            if (data.error) {
                alert('Error saving file: ' + data.error);
            } else {
                alert('File saved successfully!');
            }
        } catch (error) {
            console.error('Error saving file:', error);
        }
    }

    function newFile() {
        const filename = prompt("Enter filename:");
        if (filename) {
            openFiles[filename] = { content: '', mode: getLanguageMode(filename) };
            createTab(filename);
            switchTab(filename);
            updateFileList();
        }
    }

    // Event Listeners
    document.querySelector('.menu-item[title="Run"]').addEventListener('click', runCode);
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            saveFile();
        }
    });

    document.querySelector('.menu-item[title="New File"]').addEventListener('click', newFile);

    document.getElementById('languageSelect').addEventListener('change', (e) => {
        const mode = e.target.value;
        editor.setOption('mode', mode);
    });

    document.querySelector('.menu-item[title="Search"]').addEventListener('click', () => alert('Search functionality not yet implemented.'));
    document.querySelector('.menu-item[title="Source Control"]').addEventListener('click', () => alert('Source Control functionality not yet implemented.'));
    document.querySelector('.menu-item[title="Extensions"]').addEventListener('click', () => alert('Extensions functionality not yet implemented.'));
    document.querySelector('.menu-item[title="Account"]').addEventListener('click', () => alert('Account functionality not yet implemented.'));
    document.querySelector('.menu-item[title="Settings"]').addEventListener('click', () => alert('Settings functionality not yet implemented.'));


    // Initial setup
    initializeEditor();
    updateFileList();
});