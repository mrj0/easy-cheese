jQuery(document).ready(function() {
    var $ = jQuery;

    // Build the modal dialog
    var modal = $('<div>').attr('id', 'setupdotpy_modal');
    modal.append(
        $('<a>').attr({
            'id': 'modal_close',
            'href': '#'
        })
        .text('Close')
    );
    modal.append('<br>');
    modal.append(
        $('<textarea>').attr({
            'cols': 60,
            'rows': 20
        })
    );


    // Use jqModal plugin to turn it into a modal dialog
    modal.jqm().hide();
    $('body').append(modal);

    // Combine all the field values (if any) and return a setup.py skeleton
    function setupScaffold() {
        var raw_name = $('#input_package_name').val();
        var raw_version = $('#input_package_version').val();
        var raw_summary = $('#input_package_summary').val();
        var raw_longdesc = $('#textarea_package_longdesc').val();
        var raw_packages = $('#textarea_package_packages').val();
        var raw_modules = $('#textarea_package_modules').val();

        // Short strings should be no more than 200 chars
        var name = raw_name.substring(0, 200);
        var version = raw_version.substring(0, 200);
        var description = raw_summary.substring(0, 200);

        var long_description = raw_longdesc;

        // Split apps by newlines and strip cruft
        var packages = formatApps(raw_packages);        
        var modules = formatApps(raw_modules);

        var errors = [];
        if(isFieldEmpty(name)) {
            errors.push('Please add the <strong>Name</strong> of the package');
        }
        if(isFieldEmpty(version)) {
            errors.push('Please add the <strong>Version</strong> of the package');
        }
        if(allFieldsEmpty([packages, modules])) {
            errors.push('Please add <strong>Packages</strong> and/or <strong>Modules</strong>');
        }

        if(errors.length) {
            $('#errors').html('<ul><li>' + errors.join('</li><li>') + '</li></ul>');
            return false;
        }

        var scaffold = "#!/usr/bin/env python\n\n";
        scaffold += "from distutils.core import setup \n\n";
        scaffold += "setup(name='"+name+"',\n";
        scaffold += "    version='"+version+"',\n";
        scaffold += "    description='"+description+"',\n";
        scaffold += "    long_description='''"+long_description+"''',\n";
        if(modules.length) {
            scaffold += "    py_modules='["+modules+"]',\n";
        }
        if(packages.length) {
            scaffold += "    packages='["+packages+"]',\n";
        }
        scaffold += ")";

        return scaffold;
    }

    // Compile the scaffold and display it in the modal dialog
    $('#button_display').click(function(event, target) {
        event.preventDefault();

        var scaffold = setupScaffold();
        // If it didn't validate then show the errors and abort
        if(scaffold === false) {
            return false;
        }

        var content = modal.children('textarea');
        content.val(scaffold);

        // Position it at the centre of the screen horizontally
        modal.css('left', ($(window).width() - modal.width()) / 2);

        // Show it and highlight the text for easy Copy
        modal.jqmShow();
        content.focus().select();
    });

    $('#modal_close').click(function(event, target) {
        event.preventDefault();
        modal.hide();
    });

    // Format and filter the modules, packages
    function formatApps(app_string) {
        var apps = app_string.replace(/\.py|\'|\"/, '');
        apps = apps.split(/\r\n|\r|\n/);
        if (apps.length == 1 && apps[0] == '') {
            return '';
        }
        if(apps == []) {
            return '';
        }
        return "'" + apps.join("', '") + "'";
    }

    function isFieldEmpty(value) {
        return !Boolean(value.trim().length);
    }

    function allFieldsEmpty(fields) {
        var all_empty = true;

        for(i=0; i<fields.length; i++) {
            if(!fields[i].length) {
                continue;
            }
            if(fields[i].trim().length) {
                all_empty = false;
                break;
            }
        }

        return all_empty;
    }
});
