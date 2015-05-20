$.getJSON(
    '/pubbrain_app/json?query=vision',
    function(data) {
		$('ul').text('{ searchObject.query }');
        $('#tree1').tree({
            data: data
        });
    }
);