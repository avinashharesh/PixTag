import React, { useState } from 'react';

const HomePage = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (selectedFile) {
      try {
        const response = await fetch(
          `https://oc1sw1qko4.execute-api.us-east-1.amazonaws.com/prod/pixtag-original-images/${selectedFile.name}`, 
          {
            method: 'PUT',
            body: selectedFile, // The file is already a binary blob
            headers: {
              'Content-Type': 'image/png', // Set the content type to octet-stream
            },
          }
        );

        if (response.ok) {
          console.log('File uploaded successfully:', selectedFile.name);
          alert('File uploaded successfully!');
        } else {
          const responseText = await response.text();
          console.error('Failed to upload file:', response.statusText, responseText);
          alert(`Failed to upload file: ${response.statusText}`);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error uploading file.');
      }
    } else {
      alert('Please select a file to upload.');
    }
  };

  return (
    <div className="home-container">
      <h1>PixTag</h1>
      <div className="upload-container">
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload To S3 Bucket</button>
      </div>
    </div>
  );
};

export default HomePage;
