(function(local) {
    var url = function(path) {
        return ['http://', local, '/', path].join('');
    };

    var getScript = function(domain) {
        return $.ajax({
                url: url(domain + '.js'),
                dataType: 'text'
            }).done(function(source) {
                if (!source.length)
                    return;

                $(function() {
                    console.log(source);
                });

            });
    };

    var getStyles = function(hostname) {
        return $.ajax({
                url: url(hostname + '.css'),
                dataType: 'text'
            }).done(function(source) {
                if (!document.head || !source.length)
                    return;

                $(function() {
                    $("<style></style>")
                        .attr('class', 'warhol-styles')
                        .attr('type', 'text/css')
                        .html(source)
                        .appendTo(document.head);
                });
            });
    };

    var hostname = window.location.hostname;
    if (/^www\./i.test(hostname))
        hostname = hostname.substring(4);

    getStyles(hostname);
    getScript(hostname);

})('localhost:1928');
