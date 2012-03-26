jQuery(document).ready(function() {
    var $ = jQuery;

    $('#setup .line').click(function(ev) {
        var line = $(ev.target).closest('.line');
        line.find('.edit').show();
        line.find('.value').hide();
    });
});
