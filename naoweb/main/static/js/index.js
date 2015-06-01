
var buttons = [
    { node: document.getElementById('button-up'), action: 'forward' },
    { node: document.getElementById('button-left'), action: 'left' },
    { node: document.getElementById('button-right'), action: 'right' },
    { node: document.getElementById('button-down'), action: 'backward' }
];

buttons.forEach(function(button) {
    button.node.addEventListener('click', function() {
        var request = qwest.get('/action/' + button.action, { dataType: 'json' });

        request.then(function(response) {
            console.log(response);
        });
    });
});