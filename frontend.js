async function handleSubmit(event) {
    event.preventDefault();
    
    // Gather the form data
    const symptoms = document.getElementById('symptoms').value;
    const allergies = document.getElementById('allergies').value || 'None';
    const whatsapp = document.getElementById('whatsapp').value;
    const emergency = document.getElementById('emergency').value;

    const medEntries = [];
    document.querySelectorAll('.med-entry').forEach((row) => {
        const inputs = row.querySelectorAll('input');
        medEntries.push({
            medicine: inputs[0].value,
            frequency: parseInt(inputs[1].value, 10),
            time: inputs[2].value
        });
    });

    const payload = {
        symptoms,
        allergies,
        whatsapp,
        emergency,
        medications: medEntries
    };
    async function triggerBotMessage(event) {
    event.preventDefault();
    
    if (symptoms.length === 0) {
        alert("Please add at least one symptom first.");
        return;
    }

    // Prepare the data to match your FastAPI "HealthData" model
    const payload = {
        symptoms: symptoms.join(", "),
        allergies: "Not specified", // You can add an input for this later
        whatsapp: "your_number_here", // Add your verified WhatsApp number
        emergency: "emergency_number_here",
        medications: [] // You can populate this if needed
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/api/activate-bot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Symptoms sent to HealthBot via WhatsApp & Telegram!");
        } else {
            alert("Bot service is currently unavailable.");
        }
    } catch (error) {
        console.error("Connection error:", error);
        alert("Could not connect to the backend server.");
    }
}
    try {
        const response = await fetch('http://127.0.0.1:8000/api/activate-bot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            alert('Bot successfully linked! A WhatsApp confirmation has been sent.');
            console.log('Success:', result);
        } else {
            alert('Error creating bot: ' + result.detail);
        }
    } catch (error) {
        console.error('Error connecting to the backend:', error);
        alert('Could not connect to the server. Is the backend running?');
    }
}
