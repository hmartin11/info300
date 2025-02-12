window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
            const i = L.icon({
                iconUrl: `https://img.icons8.com/color/48/orca.png`,
                iconSize: [5, 5]
            });
            return L.marker(latlng, {
                icon: i
            });
        }
    }
});