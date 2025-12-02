function createButton(text = "Click Me") {
    const button = document.createElement("button");
    button.textContent = text;
    button.setText = function(newText) {
        this.textContent = newText;
    };
    return button;
}

// Usage example:
// const myButton = createButton("Submit");
// document.body.appendChild(myButton);
// myButton.setText("Processing...");