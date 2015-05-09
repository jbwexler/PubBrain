$.getJSON(
    '/pubbrain_app/json?query=' + '{{ searchObject.query }}',
    function(data) {
        $('#tree1').tree({
            data: data
        });
    }
);