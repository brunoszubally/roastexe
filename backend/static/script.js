document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('drop-area');
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');
    const roastButton = document.getElementById('roastButton');
    const roastMessage = document.getElementById('roastMessage');
    const roastContent = document.querySelector('.roast-content');
    const downloadButton = document.getElementById('downloadButton');
    const logoUrl = 'performate.png'; // PNG logó, hogy működjön a letöltés

    // Drag & Drop események
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('highlight');
    }

    function unhighlight() {
        dropArea.classList.remove('highlight');
    }

    // Kép feltöltés kezelése
    dropArea.addEventListener('click', (event) => {
        if (event.target !== dropArea) return;
        imageUpload.click();
    });

    dropArea.addEventListener('drop', handleDrop, false);
    imageUpload.addEventListener('change', handleFileSelect, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                    imagePreview.style.display = 'block';
                    roastButton.style.display = 'block';
                    roastMessage.style.display = 'none';
                    
                    // Animáció hozzáadása
                    imagePreview.classList.add('fade-in');
                    roastButton.classList.add('fade-in');
                }
                reader.readAsDataURL(file);
            } else {
                alert('Kérlek, csak képet tölts fel!');
            }
        }
    }

    // Roast generálás
    roastButton.addEventListener('click', async () => {
        try {
            roastButton.classList.add('loading');
            roastButton.disabled = true;
            roastContent.textContent = 'Generálom a roast-ot...';
            roastMessage.style.display = 'block';

            // Kép elküldése formdata-ban
            const file = imageUpload.files[0];
            if (!file) {
                roastContent.textContent = 'Előbb tölts fel egy képet!';
                return;
            }
            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch('/api/roast-image', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            roastContent.textContent = data.roast;
            roastMessage.classList.add('fade-in');

        } catch (error) {
            console.error('Hiba történt:', error);
            roastContent.textContent = 'Sajnálom, nem sikerült generálni a roast-ot. Kérlek, próbáld újra!';
        } finally {
            roastButton.classList.remove('loading');
            roastButton.disabled = false;
        }
    });

    // Szöveg tördelő segédfüggvény
    function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
        const words = text.split(' ');
        let line = '';
        for (let n = 0; n < words.length; n++) {
            const testLine = line + words[n] + ' ';
            const metrics = ctx.measureText(testLine);
            const testWidth = metrics.width;
            if (testWidth > maxWidth && n > 0) {
                ctx.fillText(line, x, y);
                line = words[n] + ' ';
                y += lineHeight;
            } else {
                line = testLine;
            }
        }
        ctx.fillText(line, x, y);
    }

    // Reszponzív viselkedés
    function handleResize() {
        const width = window.innerWidth;
        if (width <= 768) {
            document.body.classList.add('mobile');
        } else {
            document.body.classList.remove('mobile');
        }
    }

    window.addEventListener('resize', handleResize);
    handleResize();
});
