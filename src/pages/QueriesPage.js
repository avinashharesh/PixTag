import React, { useState } from 'react';

const QueriesPage = () => {
  const [responses, setResponses] = useState({
    API1: null,
    API2: null,
    API3: null,
    API4: null,
    API5: null,
  });
  const [inputValues, setInputValues] = useState({
    API1_tags: '',
    API1_min_repetition: '',
    API2_thumbnail_url: '',
    API3_urls: '',
    API3_type: '',
    API3_tags: '',
    API4_urls: '',
  });
  const [api5File, setApi5File] = useState(null);

  const handleInputChange = (field, value) => {
    setInputValues((prevState) => ({
      ...prevState,
      [field]: value,
    }));
  };

  const handleFileChange = (event) => {
    setApi5File(event.target.files[0]);
  };

  const handleApiCall = async (apiType) => {
    let apiUrl;
    let requestBody;

    switch (apiType) {
      case 'API1':
        apiUrl = 'https://oc1sw1qko4.execute-api.us-east-1.amazonaws.com/prod/query/imagetags';
        requestBody = {
          tags: inputValues.API1_tags.split(',').map(tag => tag.trim()),
          min_repetition: parseInt(inputValues.API1_min_repetition, 10),
        };
        break;
      case 'API2':
        apiUrl = 'https://oc1sw1qko4.execute-api.us-east-1.amazonaws.com/prod/query/imagethumbnailurl';
        requestBody = {
          thumbnail_url: inputValues.API2_thumbnail_url,
        };
        break;
      case 'API3':
        apiUrl = 'https://oc1sw1qko4.execute-api.us-east-1.amazonaws.com/prod/query/tagadditionremoval';
        requestBody = {
          url: inputValues.API3_urls.split(',').map(url => url.trim()),
          type: parseInt(inputValues.API3_type, 10),
          tags: inputValues.API3_tags.split(',').map(tag => tag.trim()),
        };
        break;
      case 'API4':
        apiUrl = 'https://oc1sw1qko4.execute-api.us-east-1.amazonaws.com/prod/query/imagedelete';
        requestBody = {
          url: inputValues.API4_urls.split(',').map(url => url.trim()),
        };
        break;
      case 'API5':
        apiUrl = 'https://oc1sw1qko4.execute-api.us-east-1.amazonaws.com/prod/query/findimagesbytags';
        requestBody = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            resolve({ image: reader.result.split(',')[1] }); // Get only the Base64 part
          };
          reader.onerror = reject;
          if (api5File) {
            reader.readAsDataURL(api5File);
          } else {
            reject('No file selected');
          }
        });
        break;
      default:
        apiUrl = '';
    }

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();
      setResponses((prevResponses) => ({
        ...prevResponses,
        [apiType]: data,
      }));
      console.log(data);
    } catch (error) {
      console.error('Error:', error);
      setResponses((prevResponses) => ({
        ...prevResponses,
        [apiType]: error.message,
      }));
    }
  };

  const renderLinks = (links) => {
    return links.map((link, index) => (
      <div key={index}>
        <a href={link} target="_blank" rel="noopener noreferrer">{link}</a>
      </div>
    ));
  };

  const renderResponse = (response, apiType) => {
    if (!response) return null;

    try {
      const parsedResponse = typeof response.body === 'string' ? JSON.parse(response.body) : response.body;

      if (apiType === 'API1' || apiType === 'API5') {
        if (!parsedResponse.links || parsedResponse.links.length === 0) {
          return <div>No Images</div>;
        }
        return renderLinks(parsedResponse.links);
      }

      if (parsedResponse.links) {
        return renderLinks(parsedResponse.links);
      } else if (parsedResponse.source_url) {
        return (
          <div>
            <a href={parsedResponse.source_url} target="_blank" rel="noopener noreferrer">
              {parsedResponse.source_url}
            </a>
          </div>
        );
      } else if (parsedResponse.message) {
        return <div>{parsedResponse.message}</div>;
      }

      return <pre>{JSON.stringify(parsedResponse, null, 2)}</pre>;
    } catch (error) {
      return <pre>{JSON.stringify(response, null, 2)}</pre>;
    }
  };

  return (
    <div className="queries-container">
      <h1>Queries Page</h1>
      <div className="card">
        <div className="form-group">
          <input
            type="text"
            placeholder="Tags (comma separated)"
            value={inputValues.API1_tags}
            onChange={(e) => handleInputChange('API1_tags', e.target.value)}
          />
          <button onClick={() => handleApiCall('API1')}>Find Image By Tags</button>
        </div>
        {responses.API1 && (
          <div className="response-container">
            <h2>Response from Finding Images By Tags:</h2>
            {renderResponse(responses.API1, 'API1')}
          </div>
        )}
      </div>
      <div className="card">
        <div className="form-group">
          <input
            type="text"
            placeholder="Thumbnail URL"
            value={inputValues.API2_thumbnail_url}
            onChange={(e) => handleInputChange('API2_thumbnail_url', e.target.value)}
          />
          <button onClick={() => handleApiCall('API2')}>Find Image By Thumbnail URL</button>
        </div>
        {responses.API2 && (
          <div className="response-container">
            <h2>Response from Finding Image By Thumbnail URL:</h2>
            {renderResponse(responses.API2, 'API2')}
          </div>
        )}
      </div>
      <div className="card">
        <div className="form-group">
          <input
            type="text"
            placeholder="Thumbnail URL"
            value={inputValues.API3_urls}
            onChange={(e) => handleInputChange('API3_urls', e.target.value)}
          />
          <input
            type="number"
            placeholder="Type (1-Add/0-Remove)"
            value={inputValues.API3_type}
            onChange={(e) => handleInputChange('API3_type', e.target.value)}
          />
          <input
            type="text"
            placeholder="Tags (comma separated)"
            value={inputValues.API3_tags}
            onChange={(e) => handleInputChange('API3_tags', e.target.value)}
          />
          <button onClick={() => handleApiCall('API3')}>Adding/Removing Tags</button>
        </div>
        {responses.API3 && (
          <div className="response-container">
            <h2>Response from Adding/Removing Tags:</h2>
            {renderResponse(responses.API3, 'API3')}
          </div>
        )}
      </div>
      <div className="card">
        <div className="form-group">
          <input
            type="text"
            placeholder="Thumbnail URLs (comma separated)"
            value={inputValues.API4_urls}
            onChange={(e) => handleInputChange('API4_urls', e.target.value)}
          />
          <button onClick={() => handleApiCall('API4')}>Delete Image</button>
        </div>
        {responses.API4 && (
          <div className="response-container">
            <h2>Response from Delete Image:</h2>
            {renderResponse(responses.API4, 'API4')}
          </div>
        )}
      </div>
      <div className="card">
        <div className="form-group">
          <input type="file" accept="image/*" onChange={handleFileChange} />
          <button onClick={() => handleApiCall('API5')}>Finding Images By Object Detection</button>
        </div>
        {responses.API5 && (
          <div className="response-container">
            <h2>Response from Finding Images By Object Detection:</h2>
            {renderResponse(responses.API5, 'API5')}
          </div>
        )}
      </div>
    </div>
  );
};

export default QueriesPage;
