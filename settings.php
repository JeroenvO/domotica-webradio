<?php session_start()?>
<!DOCTYPE html>
<!--head-->
<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />

<meta name="robots" content="noindex, nofollow" />
<meta name="author" content="Jeroen van Oorschot" />
<meta name="description" content="Instellingenpagina RPI Jeroen van Oorschot" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1" />
<meta name="msapplication-tap-highlight" content="no" /> 

<!--Jquery:-->
<script type="text/javascript" src="./js/jquery-2.0.3.min.js"></script>
<script type="text/javascript" src="./js/jquery.widget.min.js"></script><!--also for metro ui-->
<!--CSS-->
<link href="./css/opmaak.css" type="text/css" rel="stylesheet" />
<!--slider-->
<link href="./css/jquery-ui-1.10.3.custom.css" rel="stylesheet" />
<script src="./js/jquery-ui-1.10.3.custom.js"></script>
<!--JS scrollto-->
<script src="./js/scrollto.js"></script>
<!--jquery datebox
<link href="./css/jqm-datebox.css" type="text/css" rel="stylesheet" />
<link href="./css/jquery.mobile.datebox.css" type="text/css" rel="stylesheet" />
-->

<!-- metro ui-->
<link href="./css/modern.css" type="text/css" rel="stylesheet" /> 
<link href="./css/modern-responsive.css" type="text/css" rel="stylesheet" />  <!---->
<link href="./css/metro-bootstrap.css" type="text/css" rel="stylesheet" />
<!--jquery timepicker circle 
    <link rel="stylesheet" type="text/css" href="css/sltime.css" media="screen" />
     
    <script type="text/javascript" src="js/jquery.sltime.min.js"></script>
    <script type="text/javascript" src="js/jquery.event.drag-1.5.min.js"></script>-->
	
<!--<script type="text/javascript" src="./js/assets/jquery.mousewheel.min.js"></script>
<script type="text/javascript" src="./js/assets/moment.js"></script>
<script type="text/javascript" src="./js/assets/moment_langs.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/dropdown.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/accordion.js"></script>
<script type="text/javascript" src="./js/metro-button-set.js"></script>
<script type="text/javascript" src="./js/metro-touch-handler.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/carousel.js"></script>
<script type="text/javascript" src="./js/metro-input-control.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/pagecontrol.js"></script> Deze wel??-->
<!--<script type="text/javascript" src="./js/modern/rating.js"></script>-->
<!--<script type="text/javascript" src="./js/metro-slider.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/tile-slider.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/tile-drag.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/calendar.js"></script>-->
<!--JS other-->
<!--<script src="js/form-functions.js"></script>-->

<?php
require 'checkLevel.inc'; 
require 'cons/afdwaka.con';

if($level >= 0){ //if valid user, init php page
	echo "<title>JvO Raspberry</title>";
//colorswatches for choosing color
	$colors = array('green', 'greenDark', 'greenLight', 'magenta', 'pink', 'pinkDark', 'yellow', 'darken', 'purple', 'teal', 'blue', 'blueDark', 'blueLight', 'orange', 'orangeDark', 'red', 'redLight');
	$colorSwatches = '';
	for($i=0;$i<count($colors);$i++){
		$colorSwatches .= '<div class="colorSwatch bg-color-'.$colors[$i].'" id="'.$colors[$i].'"></div>';
	}
}
else{
	echo '<title>Login Error</title>';
}
?>
<script type="text/javascript">
	var plugins = [
    'core',
    'touch-handler',

    //'accordion',
    'button-set',
    //'date-format',
    //'calendar',
    //'datepicker',
    //'carousel',
    //'countdown',
    'dropdown',
    'input-control',
    //'live-tile',
    //'drag-tile',
    'progressbar',
    //'rating',
    //'slider',
    //'tab-control',
    //'table',
    'times',
    //'dialog',
    //'notify',
    //'listview',
    //'treeview',
    //'fluentmenu',
    //'hint',
    //'streamer',
    'scroll'
];

$.each(plugins, function(i, plugin){
    $("<script/>").attr('src', 'js/metro-'+plugin+'.js').appendTo($('head'));
});
//Javascript input-control functions
//Jeroen van Oorschot 2013
//Used with Raspberry Pi Domotica

 ////////////////////////////////INIT
var numCat;
var usernm = "<?php echo $usernm; ?>";
var page;
$.ajaxSetup({
		cache: false
	});
	
 $(document).ready(function(){ //code uit te voeren zodra de pagina geladen is
 	buildPage('bediening', <?php $_GET['page']='bediening'; require_once 'loadPage.php'; ?>); //de eerste pagina die geladen wordt als de website opent.
	//loadPage('bediening');
	setInterval(function(){updateValues()}, 5000) //periodically update the values, every 5 secs now
 }
 );
 
function buildPage(page2load, data){

	$('#pagetitle-title').html('<h1>'+page2load.toLowerCase()+'</h1>'); //set pagetitle
	$('#page-buttons').html(data.pbt); //page buttons
	$('#cat-buttons').html(data.cbt); // cat buttons
	$('#cat-page').html(data.cnt); //  page content
	numCat = data.nmct;

	setWidth(); //set the width of the page and the categories
	initSliders(); //set the settings for all sliders, and the init values
	setDateTimePickers(); //set the settings for all datetimepicker objects
	setColor(data.color); //set the initial color, read from the db
	
	bindActions(); //bind actions to all buttons and so.
	updateValues(); //set values for all controls that arent set automatically in loadPage
	console.log('page ' + page2load + ' builded');
	page = page2load;
 };

//Init Jquery UI Sliders with given startvalue
function initSliders(){
		$('.slider').each(function(i, obj) {
			var startValue = $(this).attr("data-init-value"); //get start value
			$(".slider").slider({
				orientation: "horizontal",
				range: "min",
				max: 100,
				value: startValue
			});
		});
}
function setDateTimePickers(){

	//Connect the plug with 24-hour format:
	//$(".input-time").sltime({});

}
//////////////////////UPDATE FUNCTIONS
function setColor(colorRGB){ //update colors
	$(".fgColor").css("color",colorRGB); //foreground color
	$(".bgColor").css("background-color",colorRGB);//general class bgColor
	$(".ui-slider-range").css("background-color",colorRGB);//slider
}

function postDB(pvalue, pwhere1, pwhere2, ptable){ //post changed settings to doUpdate.php that puts the new values in the database
	$.post('doUpdate.php', { value: pvalue, where1: pwhere1, where2: pwhere2, table: ptable })//send post update
			.done(function(data){ //if succesfull post
				if(data) window.alert(data); //usually not enough rights exception. If success, nothing is returned, data=NULL
			})
			.fail(function(data){ //xmlhttprequest failed, server is not available
				window.alert("De server is niet bereikbaar, probeer later opnieuw");
			});
}

function bindActions(){ //Bind actions to events on buttons, usually call postDB()
	//navigation functions
	$(".pag-button").click(function(){  //page buttons
           var name = $(this).attr('id');
		   loadPage(name);
    });
	$(".cat-button").click(function(){  //cat buttons
           var name = $(this).attr('id');
			var cat = '#'+name.substr(0,4);
			$.scrollTo($(cat), 800, {margin:true, axis:'x'});
		   
		   
		   
    });
	//$(".input-value").html(""); //clear the text on input-value
	

	////post functions
	
	$(".input-tf").click(function() {   //on-off buttons
			var name = $(this).attr('id');
			var val = $(this).prop("checked");
			postDB(val,'name',name,'settings');
           // window.alert(val);
	});									
	$(".input-toggle").click(function() {//toggle state buttons
			var name = $(this).attr('id')
			var val = 'toggle';
			postDB(val,'name',name,'settings');
    });									
	$(".input-time").change(function() {//time input
			var name = $(this).attr('id')
			var val = $(this).val();
			if(val.indexOf(",") !== -1){ //input minute and hour separted by , so if string contains a ,
				var test=val.split(',');//split hours and seconds
				if(!isNaN(test[0])&&!isNaN(test[1])){
					if(parseInt(test[0])>=0&&parseInt(test[0])<24&&parseInt(test[1])>=0&&parseInt(test[1])<60){
						console.log(name, val, test[1], test[1].length);
						if(test[1].length==1){test[1]='0'+test[1];} //add zeros to minutes
						val = test[0]+':'+test[1]; //save with :
						
						postDB(val,'name',name,'settings');
						updateValues();
					}else{
						console.log("invalid time");
						$(this).val('');
					}
				}else{
					console.log("NaN time");
					$(this).val('');
				}
			}else{
				window.alert("Geef tijd op als h,m");
				console.log("missing ,");
				$(this).val('');
			}
    });	
	$(".input-list").change(function() {//radio list items
			var name =$(this).attr('id'); //id van de hele option
			var checkedItem = 'input[name='+name+']:radio:checked'; 
			var val = $(checkedItem).attr('id'); //id of selected element
			postDB(val,'name',name,'settings');
			//window.alert(name+' met waarde '+val);
    }); 
	$( ".slider" ).on( "slidestop", function( event, ui ) { //Jquery UI slider
		
			var name = $(this).attr('id');
			var val = (ui.value);
			$("#"+name+"-txt").html(val);
			postDB(val,'name',name,'settings');
			//console.log(event,ui);
	});
	$('.div-slider').parent().parent().on('touchstart touchmove', function(e){
		 //prevent native touch activity like scrolling
		 e.preventDefault(); 
	});
	$('.input-dayPicker').change(function(){
		var id = $(this).attr('id');
		var name = id.substring(0,id.length-1);
		val = '{';
		for(var i=0;i<7;i++){
			//console.log(name+i);
			var checked = $("#"+name+i).prop("checked");
			//console.log(checked);
			val += '\"'+i+'\":\"'+checked+'\",';
		}
		val = val.substring(0,val.length-1);
		val += '}';
		//console.log(name, val);
		postDB(val,'name',name,'settings');
	});
	$(".colorSwatch").click(function(){  //color buttons, update color
		var colorRGB = $(this).css('background-color');
		//update db
		postDB(colorRGB,'usernm',usernm,'users');
		//set color
		setColor(colorRGB);
    });
}

function updateValues(){ //load updated values from the database. For instance if they are changed on another device.
	$.get('loadValues.php',	 { page: page}, 	function(data){
		for(var key in data){ //get data json array
			var name = "#"+key;
			var typeVal = data[key];
			var type = typeVal[0];
			var value = typeVal[1];
            var find = ".input-"+type+name;
			switch(type){
				case 'tf'://switch buttons
                    tf = (value=="true"?true:false);
                    //console.log(find+tf);
					$(find).prop("checked", tf);
                    
				break;
				case 'media': //media controls
				break;
				case 'list': //radio list items
                   // window.alert("list, value: "+value);
					$("input#"+value).prop('checked',true);	
				break;
				case 'color': //color picker
				break;
				case 'slider': //slider
					$(find+"-txt").html(value);
                    $(find).slider("value",value);
				break; 
				case 'time': //timepicker
					//console.log(find+"-txt", value);
					$(find+"-txt").html(value);
				break;
				case 'dayPicker':
					var values = eval('(' + value + ')');
					for(var i in values){
						//console.log(name+i, values[i]);
						tf = (values[i]=="true"?true:false);
						$(name+i).prop("checked", tf);
					}
				break;
				case 'value': //text box with value
					$(name).html(value);
				break;
				default:
				break;
				} //end switch*/
			}
		}, 'json');//end function
		 //end $.get*/
			console.log("Values are updated");
}//end function

function loadPage(page2load){ //load a page from loadPage.php
	$('#cat-page').html('<img src="./images/preloader-w8-cycle-black.gif" />'); // show page loader
	console.log('loading: '+page2load);
	 if(<?php echo $level ?>>=0){ //if valid user
		 $.get('loadPage.php',
		 { page: page2load},
		 	function(data){ //get returned page
				buildPage(page2load, data);
			}
		,'json');
	 }
	 else{
		$("#container").html('<div class="error-bar">Je bent niet ingelogd. <a href="index.php" title="niet ingelogd">Klik hier om in te loggen</a></div>'); //show error bar
	 }
 }
 

function setWidth(){ //change the widht of items dynamically. Also done in opmaak.css
	var w, h, rw;
	rw = window.innerWidth;
	w = rw*0.9-20;
	h = window.innerHeight-220;

	$(".cat").width(w);
	$(".cat").height(h);
	$("#cat-page").width(numCat*rw);

}


</script>
</head>
<body onResize="setWidth()" class="metrouicss">
<div id="container">
  <div id="page-buttons"></div>
  <div id="header">
    <div id="pagetitle"> <a href="./index.php" class="back-button big page-back"></a> <span id="pagetitle-title"></span> </div>
    <div id="cat-buttons"></div>
  </div>
  <div id="contentpage">
    <div id="cat-page"></div>
  </div>
  <div id="footer">
    <div class="left">Gemaakt door Jeroen van Oorschot. Styled with <a target="_blank" href="http://metroui.org.ua" class="navigation-text">Metro UI CSS</a></div>
    <div id="color-swatches"><?php echo $colorSwatches; ?></div>
  </div> 
</div>
</body>
</html>