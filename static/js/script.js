document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const directionElement = document.getElementById('direction');
    const attemptsElement = document.getElementById('attempts');
    const remainingElement = document.getElementById('remaining');
    const warningModal = document.getElementById('warning-modal');
    const closeWarning = document.getElementById('close-warning');
    
    let gazeTrackingWorker;
    let lastDirection = 'center';
    
    // Initialize webcam
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                video.srcObject = stream;
                
                // Load gaze tracking worker
                gazeTrackingWorker = new Worker('/static/js/gaze_tracking_worker.js');
                
                gazeTrackingWorker.onmessage = function(e) {
                    const data = e.data;
                    
                    if (data.direction && data.direction !== lastDirection) {
                        lastDirection = data.direction;
                        directionElement.textContent = `Looking ${data.direction}`;
                        
                        // Log gaze direction to server
                        fetch('/log_gaze', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ direction: data.direction })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'warning') {
                                warningModal.classList.remove('hidden');
                            } else if (data.status === 'success') {
                                attemptsElement.textContent = 
                                    parseInt(remainingElement.textContent) - data.remaining;
                                remainingElement.textContent = data.remaining;
                            }
                        });
                    }
                    
                    if (data.annotatedFrame) {
                        const img = new Image();
                        img.onload = function() {
                            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                        };
                        img.src = data.annotatedFrame;
                    }
                };
                
                // Process frames
                function processFrame() {
                    if (video.readyState === video.HAVE_ENOUGH_DATA) {
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                        gazeTrackingWorker.postMessage({ frame: imageData });
                    }
                    requestAnimationFrame(processFrame);
                }
                
                processFrame();
            })
            .catch(function(err) {
                console.error("Error accessing webcam: ", err);
            });
    }
    
    closeWarning.addEventListener('click', function() {
        warningModal.classList.add('hidden');
        window.location.href = '/warning';
    });
});