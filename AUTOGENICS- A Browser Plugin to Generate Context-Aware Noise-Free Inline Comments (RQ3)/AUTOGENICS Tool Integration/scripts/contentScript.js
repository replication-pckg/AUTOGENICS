document.querySelectorAll('.answer .js-code-block, .answer .s-code-block').forEach(block => {
    // Create button for generating comments
    const btn = document.createElement('button');
    btn.textContent = 'AUTOGENICS';
    btn.classList.add('btn', 'btn-primary', 'btn-sm');
    btn.style.cssText = 'margin: 10px; font-size: 0.9rem; padding: 5px 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); background-color: black; color: white;';

    // Get the question context
    const questionElement = document.querySelector('.question .post-text, .js-post-body');
    if (questionElement) {
        const question = questionElement.textContent;

        // Button click event
        btn.onclick = function () {
            const code = block.textContent;
            chrome.runtime.sendMessage({ action: "generateComment", code: code, question: question }, function (response) {
                if (response && response.comments) {
                    const commentDiv = document.createElement('pre');
                    commentDiv.textContent = response.comments;
                    commentDiv.style.cssText = 'background-color: #F8F9FA; padding: 10px; margin-top: 10px; white-space: pre-wrap; border-left: 3px solid #007BFF; font-family: monospace;';
                    block.parentNode.insertBefore(commentDiv, block.nextSibling);
                } else {
                    console.error('No comments returned from background script');
                }
            });
        };

        // Insert the button after the code block
        block.parentNode.insertBefore(btn, block.nextSibling);
    } else {
        console.error('Question context not found. Make sure the selector is correct.');
    }
});

