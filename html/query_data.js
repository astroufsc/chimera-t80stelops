function query_chimera_data() {
    $.getJSON("telops.json?" + new Date().getTime(), function (data) {
            var instruments = ['dome_dome40', 'telescope_paramount', 'camera_apogee_AltaU16M', 'weather_opd160', 'fan_M1',
                'weather_aag', 'scheduler_state_lna40sched', 'scheduler_msg_lna40sched', 'supervisor_telops'];
            for (var i in instruments) {
                var color = "";
                // Print in red data older than 20 minutes.
                if (typeof data[instruments[i]] != 'undefined') {
                    if (Date.now() > Date.parse(data[instruments[i]]['last_update'] + " UTC") + 20 * 60 * 1000) {   // 20 minutes
                        color = "red";
                    }
                }

                for (var key in data[instruments[i]]) {
                    $('#' + instruments[i] + '_' + key).text(data[instruments[i]][key]);

                    if (color === "" && instruments[i].startsWith("supervisor_")) {
                        var color_status = "";
                        if (data[instruments[i]][key].startsWith("READY") || data[instruments[i]][key].startsWith("OPERATING")) {
                            color_status = "green";
                        } else if (data[instruments[i]][key].startsWith("UNSET")) {
                            color_status = "blue";
                        }
                        else if (data[instruments[i]][key].startsWith("CLOSE") || data[instruments[i]][key].startsWith("LOCK")) {
                            color_status = "red";
                        }
                        $('#' + instruments[i] + '_' + key).css("color", color_status);
                    } else {
                        $('#' + instruments[i] + '_' + key).css("color", color);
                    }
                }
            }
            telescope_pointer.ra = data['telescope_paramount']['ra_deg'];
            telescope_pointer.dec = data['telescope_paramount']['dec_deg'];
            telescope_pointer.url = "http://server1.wikisky.org/v2?ra=" + (data['telescope_paramount']['ra_deg'] / 15) + "&de=" + (data['telescope_paramount']['dec_deg']) + "&zoom=6&img_source=DSS2"
            telescope_pointer.img = 'http://server7.sky-map.org/imgcut?survey=DSS2&w=128&h=128&ra=' + (data['telescope_paramount']['ra_deg'] / 15) + '&de=' + data['telescope_paramount']['dec_deg'] + '&angle=0.25&output=PNG';
            telescope_pointer.html = '<div class="virtualsky_infocredit">' +
                '<a href="' + telescope_pointer.url + '" style="color: white;">DSS2/Wikisky</a>' +
                '</div>' +
                '<a href="' + telescope_pointer.url + '" style="display:block;' + telescope_pointer.style + '">' +
                '<img src="' + telescope_pointer.img + '" style="border:0px;' + telescope_pointer.style + '"/>' + // title="'+label+'" />'+
                '</a>';
        }
    );
}

$(document).ready(function () {
    $.ajaxSetup({cache: false});
    query_chimera_data();
    setInterval(query_chimera_data, 10000);
});