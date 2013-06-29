(function(local) {
    var url = function(domain, extension) {
        return ['http://', local, '/', domain, '.', extension].join('');
    };

    var get = function(domain, extension) {
        return $.ajax({ url: url(domain, extension), dataType: 'text' });
    };

    var domain = window.location.hostname;
    if (/^www\./i.test(domain))
        domain = domain.substring(4);

    // Styles
    get(domain, 'css').done(function(source) {
        if (!source || !source.length)
            return;

        $(function() {
            if (!document.head)
                return;

            $("<style></style>")
                .attr('class', 'warhol-styles')
                .attr('type', 'text/css')
                .html(source)
                .appendTo(document.head);
        });
    });

    // Scripts
    get(domain, 'js').done(function(source) {
        if (!source || !source.length)
            return;

        $(eval.bind(window, source));
    });

})('localhost:1928');
