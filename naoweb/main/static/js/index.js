
$(function() {
    var buttons = [
        { node: $('#button-up'), action: 'moveforward' },
        { node: $('#button-left'), action: 'turnleft' },
        { node: $('#button-right'), action: 'turnright' },
        { node: $('#button-down'), action: 'movebackward' },
        { node: $('#button-standup'), action: 'standup' },
        { node: $('#button-sitdown'), action: 'sitdown' },
        { node: $('#button-riddle'), action: 'riddle' }
    ];

    var image = $('#image-camera');

    var status = {
        button: $('#button-onoff'),
        current: 'off',
        overlay: $('.overlay')
    };

    var say = $('#button-say');
    var actionDisabled = false;

    // On load
    refreshImage();
    setInterval(function() { refreshImage(); }, 500);

    buttons.forEach(function(button) {
        button.node.on('click', function() {
            executeAction(button.action);
        });
    });

    status.button.on('click', function() {
        if (status.current == 'off') {
            status.button.attr('disabled', true);

            executeAction('motor', 'on').done(function() {
                status.current = 'on';
                status.button.text('STOP');
                status.button.attr('disabled', false);
                status.overlay.hide();
            });
        } else {
            status.button.attr('disabled', true);

            executeAction('motor', 'off').done(function() {
                status.current = 'off';
                status.button.text('START');
                status.button.attr('disabled', false);
                status.overlay.show();
            });
        }
    });

    say.on('click', function() {
        var text = prompt('Texte : ');
        
        text = text.toString().toLowerCase()
            .replace(/\s+/g, '_')           // Replace spaces with -
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\-\-+/g, '_')         // Replace multiple - with single -
            .replace(/^-+/, '')             // Trim - from start of text
            .replace(/-+$/, '');            // Trim - from end of text

        executeAction('say', text);
    });


    function executeAction(name, parameters) {
        var cmd = name;

        if (typeof parameters != 'undefined') {
            cmd += '-' + parameters;
        }
        actionDisabled = true;
        setTimeout(enableAction, 3000);
        return $.getJSON('/action/' + cmd);
    }

    function refreshImage() {
        var newImage = $('<img src="/image/?d=' + Date.now() + '" />');

        newImage.load(function() {
            image.html('');
            image.append(newImage);
        });

        $('#temp').append(newImage);
    }

    function enableAction(){
        actionDisabled = false;
    }
    
    function handleOrientation(event) {
        if(actionDisabled){
            return;
        }

        var x = event.beta,  // En degré sur l'interval [-180,180].
            y = event.gamma, // En degré sur l'interval [-90,90].
            z = event.alpha; // en degré sur l'interval [0, 360].

        if(x < 30 ){
            executeAction("moveforward");
        }else if(x > 145){
            executeAction("movebackward");
        }else if(y < -65){
            executeAction("turnleft");
        }else if(y > 65){
            executeAction("turnright");
        }
    }

    window.addEventListener('deviceorientation', handleOrientation);
});
