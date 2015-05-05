$.getJSON(
    '/pubbrain_app/json?node=700',
    function(data) {
        $('#tree1').tree({
            data: data
        });
    }
);

$(function() {
    $('#tree1').tree({
        data: data
    });
});