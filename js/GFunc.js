var SOCKET;
var retries; //how often retriet to reconnect
/*function initSliders() {
	$('.noUiSlider').noUiSlider({
		range : [00, 100],
		handles : 1,
		start : 0,
		connect : "lower",
		serialization : {
			resolution : 1
		},
		behaviour : "extend-tap",
		slide : function () {
			var name = $(this).attr('id');
			var val = $(this).val();
			var oldval = $("#" + name + "-txt").html();
			if (oldval != val) {
				sendValue(name, parseInt(val));
				$("#" + name + "-txt").html(val);
			}
		}
	});
	
}*/
//helper for timepicers
(function ( $ ) {
	$.fn.timePicker = function( options ) {
		return this.each(function(){
			$(this).data('tp', new timePicker(this, options));
		});
	};
}( jQuery ));

//helper for colorpicker
(function ( $ ) {
	$.fn.colorPicker = function( options ) {
		return this.each(function(){
			$(this).data('tp', new colorPicker(this, options));
		});
	};
}( jQuery ));

//initializes the timepickers. Sets the color, animation speed, and the popup where they are placed in. Bind the change event to the update websocket function
function initTimePickers() {
	$(".input-time").timePicker({
		color : 'orange',
		drawInterval: 20,
		animationStep: 3,
		onCenterClick : function () {
			$(this.canvas).bPopup().close();
		},
		autoStartDraw : false
	});
	$('.input-time-btn').on('click', function (e) {
		e.preventDefault();
		id = $(this).attr('id').slice(0,-4); //remove -btn;
		$('#' + id).data('tp').startDraw();
		//console.log('opening : ' + id);
		$('#' + id).bPopup({
			appendTo : 'body',
			appending : false,
			zIndex : 2,
			positionStyle : 'fixed',
			onClose : function () {
				var ts = $('#' + id).data('tp').getTimeStr();
				$('#' + id + '-btn').text(ts);
				$('#' + id).data('tp').stopDraw();
				sendValue(id, ts);
			}
		});
	});
}

//init colorpickers, bind the change event to the update websocket function
function initColorPickers(){
	$(".input-color").colorPicker({
		drawInterval: 20,
		onColorChange : function (){
			var id =$(this.canvas).attr('id');
			var clr = this.getColorHSV();
			//console.log('color:'+this.getColorHSL().h+id);
			sendValue(id,[parseFloat(clr.h.toFixed(5)),parseFloat(clr.s.toFixed(5)),parseFloat(clr.v.toFixed(5))]);
		},
		bgcolor: 'white'
	});
}

//Init all the graphs on the logbook page. It also binds the buttons that load the datapoints of the graphs
function initGraphs() {
	$.plot("div.graph", [], []);
	var start = 0;
	$(".graph-btn-4hour").click(function () {
		start = Math.round(new Date().getTime() / 1000) - 14400;
		loadData($(this).attr('id').slice(0,-3), start, 0);
	});
	$(".graph-btn-day").click(function () {
		start = Math.round(new Date().getTime() / 1000) - 86400;
		loadData($(this).attr('id').slice(0,-3), start, 0);
	});
	$(".graph-btn-week").click(function () {
		start = Math.round(new Date().getTime() / 1000) - 604800;
		loadData($(this).attr('id').slice(0,-3), start, 0);
	});
	$(".graph-btn-month").click(function () {
		start = Math.round(new Date().getTime() / 1000) - 2592000;
		loadData($(this).attr('id').slice(0,-3), start, 0);
	});
	$(".graph-btn-year").click(function () {
		start = Math.round(new Date().getTime() / 1000) - 31536000;
		loadData($(this).attr('id').slice(0,-3), start, 0);
	});
}

//update the graphs (plot them) with the supplied datapoints (data)
function updateGraph(graph, data) {
	data = eval(data);
	var l = data.length;
	for (var i = 0; i < l; i++) {
		data[i][0] = data[i][0] * 1000;
	}
	var t = '%H:%M';
	var d = 'minute';
	if (l > 2 * 24 * 2) {
		t = '%H:00';
		d = 'hour';
	}
	if (l > 2 * 24 * 4) {
		d = 'day';
		t = '%a';
	}
	if (l > 2 * 24 * 7 ) {
		t = '%e';
		d = 'day';
	}
	if (l > 2 * 24 * 7 * 5) {
		d = 'month';
		t = '%b';
	}
	console.log('Updating: ', graph, data);
	$.plot('#' + graph, [data], {
		xaxis : {
			mode : "time",
			minTickSize : [1, d],
			timeformat : t,
			timezone : 'browser'
		},
		series : {
			color : color,
			lines : {
				show : true
			},
			points : {
				show : true
			}
		},
		grid : {
			show : true,
			hoverable : true,
			autoHighlight : true
		}
	});
}

//bind all the other buttons on any page. Make sure something happens when they change in value
function bindActions() {
	$(".pag-button").click(function () {
		loadPage($(this).attr('id'));
	});
	$(".cat-button").click(function () {
		var name = $(this).attr('id');
		$.scrollTo($('#' + name.substr(0, 4)), 200, {
			margin : true,
			axis : 'x'
		});
	});
	$(".input-tf").click(function () {
		sendValue($(this).attr('id'), $(this).prop("checked"));
	});
	$(".input-button").click(function () {
		sendValue($(this).attr('id'), $(this).attr('id'));
	});
	$(".input-list").change(function () {
		var name = $(this).attr('id');
		var checkedItem = 'input[name=' + name + ']:radio:checked';
		sendValue(name, $(checkedItem).attr('id'));
	});
	$('.input-dayPicker').change(function () {
		var name = $(this).attr('id')
			name = name.substring(0, name.length - 1);
		var val = '';
		for (var i = 0; i < 7; i++) {
			var checked = $("#" + name + i).prop("checked");
			val += checked.toString().substring(0, 1);
		}
		sendValue(name, val);
	});
	$(".cs").click(function () {
		var colorRGB = $(this).css('background-color');
		var data = 'U' + '{"c":"' + colorRGB + '"}';
		sendSocket(data);
		setColor(colorRGB);
	});
	$(".input-slider").change(function() {
		var id = $(this).attr('id');
		var val = $(this)[0].value;
		$("#"+id + "-txt").html(val);
		sendValue(id, parseInt(val));
	});
	$(".input-colorRGB").change(function() {
		var nameO = $(this).attr('id');
		nameO = nameO.substring(0,nameO.length-2)
		var name = "#"+nameO;
		var val = [0,0,0];
		val[0] = parseInt($(name+'-r')[0].value);
		val[1] = parseInt($(name+'-g')[0].value);
		val[2] = parseInt($(name+'-b')[0].value);
		$(name+"-r-txt").html(val[0]);
		$(name+"-g-txt").html(val[1]);
		$(name+"-b-txt").html(val[2]);
		for(var i=0;i<3;i++){
			val[i]=val[i]/100.0;
		}
		var d={};
		d[nameO] =val;
		var data = 'S'+JSON.stringify(d);
		sendSocket(data);
	});
}

//Update the value of a setting to a new value
function updateValue(name, type, value) {
	var find = '#' + name;//+" .input-" + type;
	switch (type) {
	case 'tf':
		$(find).prop("checked", value);
		break;
	case 'list':
		$("#" + value).prop('checked', true);
		break;
	case 'color':
		//console.log(value)
		$(find).data('tp').setColorHSV(value[0],value[1],value[2]);
		break;
	case 'colorRGB':
		for(var i=0;i<3;i++){
			value[i]=parseInt(value[i]*100);
		}
		$(find+'-r')[0].value = value[0];
		$(find+'-r-txt').html(value[0]);
		$(find+'-g')[0].value = value[1];
		$(find+'-g-txt').html(value[1]);
		$(find+'-b')[0].value = value[2];
		$(find+'-b-txt').html(value[2]);
		break;
	case 'slider':
		$(find + "-txt").html(value);
		$(find)[0].value = value;
		break;
	case 'time':
		$(find + '-btn').html(value);
		value = value.split(":");
		var h = parseInt(value[0]);
		var m = parseInt(value[1]);
		h = isNaN(h) ? 0 : h;
		m = isNaN(m) ? 0 : m;

		$(find).data('tp').setTime(h, m);
		break;
	case 'dayPicker':
	//console.log(value);
		for (var i = 0; i < 7; i++) {
			var tf = (value.charAt(i) == "t" ? true : false);
			//console.log(tf);
			$(find + i).prop("checked", tf);
		}
		break;
	case 'value':
		$(find).html(value);
		break;
	default:
		break;
	}
}

//set the color of some ui items
function setColor(colorRGB) {
	color = colorRGB;
	/*$(".fgColor").css("color", colorRGB);
	$(".bgColor").css("background-color", colorRGB);
	$(".noUi-connect").css("background", colorRGB);*/
	$("head").append("<style>.fgColor{color:"+colorRGB+" !important}.metro .switch.input-control input[type='checkbox']:checked ~ .check, .bgColor, .noUi-connect, input[type=range].input-slider::-ms-fill-lower{  background-color: " + colorRGB + " !important }</style>");
	
}

//sets the width and height of the page and the category divisions
function setWidth() {
	var rw = window.innerWidth;
	//var w = rw * 0.9 - 20;
	var h = window.innerHeight;
	if(rw<500){//mobile
		h -=116;
		if($(".input-color").length) 
			$(".input-color").each(function(index, element) {
           		$(element).data("tp").setWidth(300,300); 
        	});
	}else{
		if($(".input-color").length) 
			$(".input-color").each(function(index, element) {
           		$(element).data("tp").setWidth(500,500); 
        	});

		h -=180;
		if(rw>800){
			rw = 800;	
		}
	}
	$(".cat").height(h);
	$(".cat").width(rw-30);
	$("#cat-page").width(numCat * (rw+40));
}

//makes a page from supplied raw page data. Also calls specific initializations per page
function buildPage(page2load, data) {
	$('#pagetitle-title').html('<h1>' + page2load.toLowerCase() + '</h1>');
	$('#page-buttons').html(data.pbt);
	$('#cat-buttons').html(data.cbt);
	$('#cat-page').html(data.cnt);
	numCat = data.nmct;
	page = page2load;
	builded = true;
	if (page2load == 'bediening') {
		sendSocket('R{"p":"'+page2load+'"}');
	//	initSliders();
		initTimePickers();
		initColorPickers();
	} else if (page2load == 'logboeken') {
		initGraphs();
	}
	setWidth();
	bindActions();
	console.log('page ' + page2load + ' builded');
}

//send a [name, value] setting pair to the server
function sendValue(name, value) {
	var d={};
	d[name] =value;
	var data = 'S'+JSON.stringify(d);
	sendSocket(data);
}

//send a request for graphdata to the server
function loadData(graph, start, end) {
	//STATE = 1;
	var data = 'D' + '{"d":"' + graph + '","s":' + start;
	if (end != 0) {
		data += ',"E":' + end;
	}
	data += '}';
	sendSocket(data);
}

//send a request for raw page data to the server
function loadPage(page) {
	if(false){ //use websockets
		//console.log('loading: '+page);
		sendSocket('P{"p":"'+page+'"}');
	}else{ //use ajax
		$.getJSON('loadPage.php', {page:page}).done(function (data){
		buildPage(page,data);
		});
	}
}

//log in to the socketserver
function login(username, password, server, port) {
	var host = "ws://" + server + ':' + port;
	console.log("Verbinden met: " + host + " ...");
	try {
		SOCKET = new WebSocket(host);
		
		SOCKET.onopen = function () {
			//log('Socket Status: ' + SOCKET.readyState+' (open)');
			retries =0;
			var logindata = {
				'username' : username,
				'password' : password,
			}
			var loginpackage = JSON.stringify(logindata);
			sendSocket(loginpackage);
		}

		SOCKET.onmessage = function (event) {
			msg = event.data;
			type = msg.substr(0, 1);
			msg = msg.substr(1);

			//console.log(msg);
			switch(type){
				case 'D': //Data, decode graph
					try {
						//log(msg);
						//var i = msg.indexOf("P:")
						//	graph = msg.substring(1, i)
						//	points = msg.substring(i );
						//log(points);
						console.log('Rx:'+msg);
						msg = eval('('+msg+')');
						updateGraph(msg.d, msg.p);
					} catch (exception) {
						console.log("error parsing incoming JSON graph points: " + exception);
					}
				break;
				case 'P': //PAGE
					try{
						msg = eval('('+msg+')'); //the json message
						console.log(msg);
						$('#cat-page').text('');
						buildPage(msg.ptl, msg);
					}catch(exception){
						console.log("error parsing incoming JSON page: " + exception);
					}
				break;
				case 'M':
					console.log('received msg: '+msg);
					alert('Bericht: ' + msg);
				break;
				case 'E':
					console.log('received error: '+msg);
					alert('Dit mag jij niet');
					window.location = "/login.php?log=uit";
				break;
				case 'W':
					console.log('received warning: '+msg);
					alert('Dit is niet mogelijk (' + msg + ')');
				break;
				case 'A':
					console.log('Login approved: '+msg);
					
					loadPage('bediening');
				break;
				case 'S':
					try {
						var values = eval('(' + msg + ')');
						//console.log("received message: " + values);
						updateValuesJSON(values);
					} catch (exception) {
						console.log("error parsing incoming JSON setting: " + exception + " message: " + msg);
					}
				break;
				case 'C': //user's color
					console.log("Color changed to "+msg);
					setColor(msg);
				break;
				default:
					alert('invalid message received');
				break;
			}
		}

		SOCKET.onclose = function () {
			console.log('Socketverbinding gesloten');
			//alert('De verbinding met de server is gesloten. Vernieuw de pagina om opnieuw te proberen.')
			if(retries<2){
				console.log('Opnieuw verbinden');
				login(username, password, server, port);
				retries++;
			}else if (confirm("De verbinding is verloren, opnieuw proberen?")) {
				login(username, password, server, port);
			}
		}
		SOCKET.onerror = function () {
			console.log('Socket fout: ' + SOCKET.readyState);
		}
	} catch (exception) {
		console.log("Error occured: " + exception);
	}
}
function updateValuesJSON(values) {
	if (builded) {
		for (var key in values) {
			name = key;
			type = values[key][0];
			value = values[key][1];
			console.log("Rx: " + name + " (" + type + ") : " + value);
			updateValue(name, type, value);
		}
	} else {
		setTimeout(function () {
			updateValuesJSON(values)
		}, 200);
	}

}
