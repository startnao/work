
$(function() {
    var buttons = [
        { node: $('#button-up'), action: 'moveforward' },
        { node: $('#button-left'), action: 'turnleft' },
        { node: $('#button-right'), action: 'turnright' },
        { node: $('#button-down'), action: 'movebackward' }
    ];

    var image = $('#image-camera');

    var status = {
        button: $('#button-onoff'),
        current: 'off',
        overlay: $('.overlay')
    };


    // On load
    setTimeout(function() { refreshImage(); }, 1000);

    buttons.forEach(function(button) {
        button.node.on('click', function() {
            executeAction(button.action).done(function(response) {
                console.log(response);
            });
        });
    });

    status.button.on('click', function() {
        if (status.current == 'off') {
            status.button.attr('disabled', true);

            executeAction('motor', 'on').done(function() {
                status.current = 'on';
                status.button.text('OFF');
                status.button.attr('disabled', false);
                status.overlay.hide();
            });
        } else {
            status.button.attr('disabled', true);

            executeAction('motor', 'off').done(function() {
                status.current = 'off';
                status.button.text('ON');
                status.button.attr('disabled', false);
                status.overlay.show();
            });
        }
    });


    function executeAction(name, parameters) {
        var cmd = name;

        if (typeof parameters != 'undefined') {
            cmd += '-' + parameters;
        }

        return $.getJSON('/action/' + cmd);
    }

    function refreshImage() {
        image.html('<img src="/image?d=' + Date.now() +'" />');
    }
});