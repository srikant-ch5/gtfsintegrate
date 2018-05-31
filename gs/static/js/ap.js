$(document).ready(function(){

	var $form = $('.feed-form');
	$form.submit(function(event){
		event.preventDefault();
		var forms = [];
		var formdata;

		for(i=1;i<=2;i++){
			formdata = "/gtfs/formdata/"+i+"/";
			$.getJSON(formdata,function(data){
				//pdata = JSON.parse(data)
				forms.push(data);
					//console.log(forms[1]);
				//console.log(forms)
			});
		}
		
		for(obj in forms){
			console.log(obj)
		}

		//console.log(forms[0]["url"]);
		var formurl		=	$("#formurl").val();		
		var formname	=	$("#formname").val();
		var formosmtag	=	$("#formosmtag").val();
		var	formgtfstag	=	$("#formgftstag").val();
		var formfrequency=	$("#formfrequency").val();

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

	var $form = $('.feed-form');
	$form.submit(function(event){
		//event.preventDefault();
		var forms = [];

		for(i=0;i<10;i++){
			var formdata = "/gtfs/formdata/"+i+"/";
			$.getJSON(formdata,function(data){
				forms.push(data.name);
				console.log(forms)
			})

		}
	})
*/
})
