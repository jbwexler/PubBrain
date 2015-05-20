$('ul.tabs li').click(function(){
	var tab_id = $(this).attr('data-tab');
	
	$(this).css("background-color", "yellow");
	$('ul.tabs li').removeClass('current');
	$('.tab-content').removeClass('current');

	$('ul.tabs').addClass('current');
	$("#"+tab_id).addClass('current');
});
