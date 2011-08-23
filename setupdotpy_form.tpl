<html>
<head>
    <title>ez-cheese: the cheese shop's setup.py generator</title>
    <link rel="stylesheet" href="static/setupdotpy.css" media="screen">
    <link rel="stylesheet" href="static/jqModal.css" media="screen">
</head>

<body>
    <h1>ez-cheese</h1>
    <h2>basic setup.py generator</h2>
    <form id="form_setupdotpy" method="post">
        <fieldset id="setup_required_fields">
            <p>
                <label for="input_package_name">Package Name</label>
                <input id="input_package_name" name="name" type="text" size="30" />
            </p>
            <p>
                <label for="input_package_version">Version</label>
                <input id="input_package_version" name="version" type="text" size="8" />
            </p>
            <p>
                <label for="input_package_summary">Description</label>
                <input id="input_package_summary" name="description" type="text" size="80" />
                <span class="field_desc">Short, summary description of the package</span>
            </p>
            <p>
                <label for="textarea_package_longdesc">Long Description</label>
                <textarea id="textarea_package_longdesc" name="long_description" cols="40" rows="4"></textarea>
                <span class="field_desc">Used by <abbr title="Python Package Index">PyPI</abbr> when you are registering a package, to build its home page.</span>
            </p>
            <p>
                <label for="textarea_package_packages">Packages to include</label>
                <textarea id="textarea_package_packages" name="packages" cols="40" rows="8"></textarea>
                <span class="field_desc">One per line</span>
            </p>
            <p>
                <label for="textarea_package_modules">Modules to include</label>
                <textarea id="textarea_package_modules" name="modules" cols="40" rows="8"></textarea>
                <span class="field_desc">One per line</span>
            </p>
        </fieldset>
        <fieldset id="actions">
            <button id="button_display">Display setup.py</button>
            <input id="submit_download" name="download" type="submit" value="Download">
        </fieldset>
    </form>

    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.6/jquery.min.js"></script>
    <script type="text/javascript" src="static/jqModal.js"></script>
    <script type="text/javascript" src="static/setupdotpy.js"></script>
</body>
</html>
