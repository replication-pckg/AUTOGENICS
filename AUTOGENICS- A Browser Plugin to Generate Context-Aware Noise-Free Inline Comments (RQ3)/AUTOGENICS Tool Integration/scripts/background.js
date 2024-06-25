chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
      if (request.action === "generateComment") {
          fetch('http://localhost:5000/comment', { 
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ code: request.code, question: request.question })
          })
          .then(response => response.json())
          .then(data => sendResponse({comments: data}))
          .catch(error => console.error('Error:', error));
          return true; 
      }
  }
);