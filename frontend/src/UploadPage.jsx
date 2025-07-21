import React, { useState } from 'react';
import axios from 'axios';

export default function UploadPage() {
    const [uploadFile, setUploadFile] = useState(null);
    const [uploadMachineId, setUploadMachineId] = useState('');
    const [downloadMachineId, setDownloadMachineId] = useState('');
    const [message, setMessage] = useState('');

    const handleUpload = async () => {
        if (!uploadFile || !uploadMachineId) {
            setMessage('❗ Please select a file and enter machine ID');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', uploadFile);

            const res = await fetch(`${process.env.REACT_APP_API_URL}/fileupload?machine_id=${uploadMachineId}`, {
                method: 'POST',
                body: formData,
                // ⚠ No need to set Content-Type; browser automatically sets correct boundary
            });

            const data = await res.json();
            if (res.ok) {
                setMessage(`✅ ${data.message}`);
            } else {
                console.error(data);
                setMessage(`❌ Upload failed: ${data.error || 'Unknown error'}`);
            }
        } catch (err) {
            console.error(err);
            setMessage('❌ Upload failed');
        }
    };

    const handleDownload = () => {
        if (!downloadMachineId) {
            setMessage('❗ Please enter machine ID');
            return;
        }
        const url = `${process.env.REACT_APP_API_URL}/downloadfile?machine_id=${downloadMachineId}`;
        window.location.href = url;
        setMessage('✅ Download started');
    };

    return (
        <div style={{ maxWidth: 500, margin: 'auto', padding: 20 }}>
            <h2>⚙️ Machine File Upload & Download</h2>
            <div>
                <input type="text" placeholder="Machine ID" value={uploadMachineId} onChange={(e) => setUploadMachineId(e.target.value)} />
                <input type="file" onChange={(e) => setUploadFile(e.target.files[0])} />
                <button onClick={handleUpload}>Upload</button>
            </div>
            <div style={{ marginTop: 20 }}>
                <input type="text" placeholder="Machine ID to download" value={downloadMachineId} onChange={(e) => setDownloadMachineId(e.target.value)} />
                <button onClick={handleDownload}>Download</button>
            </div>
            <p>{message}</p>
        </div>
    );
}
