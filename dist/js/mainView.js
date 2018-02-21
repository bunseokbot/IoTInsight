$(function() {
	var openBtn = $('#btn'),
		slideMenu = $('#menu'),
		layer = $('<div />').addClass('layer');
	openBtn.on("click", function() {
		if (slideMenu.is(':hidden')) {
			layer.appendTo('body');
			slideMenu.slideDown(300);
		} else {
			slideMenu.slideUp(300);
			layer.remove();
		}
	});
});