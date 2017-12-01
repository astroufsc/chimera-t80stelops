function query_chimera_data(){
    $.getJSON("telops.json?"+new Date().getTime(),function(data){
        var instruments = ['dome_AshDome', 'telescope_T80S', 'camera_T80Cam', 'weather_lcogt', 'weather_blanco_ws',
        'weather_wxt520', 'weather_rasicam', 'fan_M1', 'fan_DomeFanEast', 'fan_DomeFanWest', 'seeing_blanco_seeing',
        'weather_aag',
        'scheduler_state_sequential', 'scheduler_msg_sequential']; //, 'fan_DomeFanEast'];
        for (var i in instruments){
            // Print in red data older than 20 minutes.
            if (typeof data[instruments[i]] != 'undefined'){
//                alert(instruments[i]+data[instruments[i]]['last_update']);
                if (Date.now() > Date.parse(data[instruments[i]]['last_update']+" UTC") + 10 * 60 * 1000) {   // 10 minutes
                    var color = "red";
                }else{
                    var color = "";
                }
            }

            for (var key in data[instruments[i]]){
                $('#'+instruments[i]+'_'+key).text(data[instruments[i]][key]);
                $('#'+instruments[i]+'_'+key).css("color", color);
//                if (key == "state"){
//                    alert(instruments[i]);
//                }
            }
        }
    telescope_pointer.ra = data['telescope_T80S']['ra_deg'];
    telescope_pointer.dec = data['telescope_T80S']['dec_deg'];
    telescope_pointer.url = "http://server1.wikisky.org/v2?ra="+(data['telescope_T80S']['ra_deg']/15)+"&de="+(data['telescope_T80S']['dec_deg'])+"&zoom=6&img_source=DSS2"
    telescope_pointer.img = 'http://server7.sky-map.org/imgcut?survey=DSS2&w=128&h=128&ra='+(data['telescope_T80S']['ra_deg']/15)+'&de='+data['telescope_T80S']['dec_deg']+'&angle=0.25&output=PNG';
    telescope_pointer.html =  '<div class="virtualsky_infocredit">'+
                                        '<a href="'+telescope_pointer.url+'" style="color: white;">DSS2/Wikisky</a>'+
                                '</div>'+
                                '<a href="'+telescope_pointer.url+'" style="display:block;'+telescope_pointer.style+'">'+
                                        '<img src="'+telescope_pointer.img+'" style="border:0px;'+telescope_pointer.style+'"/>' + // title="'+label+'" />'+
                                '</a>';
    }
    );
}

$(document).ready(function(){
    $.ajaxSetup({ cache: false });
    query_chimera_data();
    setInterval(query_chimera_data, 10000);
});