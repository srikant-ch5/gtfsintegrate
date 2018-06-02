$(document).ready(function(){

	var $form = $('.feed-form');
	$form.submit(function(event){
		//event.preventDefault();

		var formurl		=	$("#formurl").val();		
		var formname	=	$("#formname").val();
		var formosmtag	=	$("#formosmtag").val();
		var	formgtfstag	=	$("#formgtfstag").val();
		var formfrequency=	$("#formfrequency").val();

		var formdata;

		var feed_entry_found	 = 0;
		var feed_instances_in_db = 0;
		var feed_name='';
		var form_timestamp;

		for(i=1;i<=6;i++){
			formdata = "/gtfs/formdata/"+i+"/";

			$.ajax({
				type	: "GET",
				url		: formdata,
				dataType: 'json',
				async	: false,
				success	: function(data){
					if(data.url == formurl && data.osm_tag == formosmtag && data.gtfs_tag == formgtfstag){
						feed_entry_found = 1;
						feed_instances_in_db += 1;
						feed_name = data.name;
						form_timestamp = data.timestamp;
					}
				},
				error	: function(){
					console.log("Feed is not available at "+i);
				}
			});
		}

		if(feed_entry_found > 0){
			$("#feed-status").text("->Feed is already present with name of operator " + feed_name );
		}
		else{
			$("#feed-status").text("->Feed not found Downloading the new feed wait until the feed is downloaded");	
		}

		function stateChange(newState) {
    setTimeout(function(){
        if(newState == -1){alert('VIDEO HAS STOPPED');}
    }, 5000);
}
	stateChange();

		var today = new Date();
		var dd 	 = today.getDate();
		var mm 	 = today.getMonth()+1;
		var yy   = today.getFullYear();

		dd= dd.toString()
		mm= mm.toString()
		yy= yy.toString()

		if(dd.length == 1){
			dd = '0'+dd;
		}
		if(mm.length == 1){
			mm = '0'+mm;
		}

		var current_date = yy+'-'+mm+'-'+dd;
		
		var current_date = Date.parse(current_date);
		var form_date =Date.parse(form_timestamp.substring(0,9))

		console.log(form_date)
		console.log(current_date)

		if(feed_entry_found > 0 && current_date-form_date > formfrequency){
			$("#feed-status2").text("Feed in Database is updaing to latest version");
		}
	});
/*
	var nodedata = '{% url "nodedata" %}';
    function loadmapfunction(map, options){
		//$.getJSON(waydata, function(data){
			//L.geoJson(data).addTo(map);
		//})
		$.getJSON(nodedata, function(data){
			L.geoJson(data).addTo(map);
		})
	}

*/
})
