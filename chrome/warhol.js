(function(local) {
	var style = '<style id="warhol-css" type="text/css"></style>';

	var url = function(path) {
		return ['http://', local, '/', path].join('');
	};

	var js = function(hostname) {
		$.ajax({
			url: url(hostname + '.js'),
			dataType: 'text',
			success: function(source) {
				if (!source.length)
					return;

				$(function() {
					eval(source);
				});
			},
			error: function() { }  // Fail silently.
		});
	};

	var css = function(hostname) {
		$.ajax({
			url: url(hostname + '.css'),
			dataType: 'text',
			success: function(source) {
				if (!document.head || !source.length)
					return;

				var element = $(style).html(source);
				$(document.head).append(element);
			},
			error: function() { }  // Fail silently.
		});
	};

	var hostname = window.location.hostname;
	if (/^www\./i.test(hostname))
		hostname = hostname.substring(4);

	$(function() {
		js(hostname);
	});

	css(hostname);
})('localhost:1928');
