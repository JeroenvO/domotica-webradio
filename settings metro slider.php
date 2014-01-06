<?php session_start()?>
<!DOCTYPE html>
<!--head-->
<html><head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />

<meta name="robots" content="noindex, nofollow" />
<meta name="author" content="Jeroen van Oorschot" />
<meta name="description" content="Instellingenpagina RPI Jeroen van Oorschot" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1" />
<meta name="msapplication-tap-highlight" content="no" /> 
<!--windows 8 tegeltjes-->
<meta name="application-name" content="Raspberry Bediening"/>
<meta name="msapplication-tooltip" content="JvO Bedieningspaneel"/>
<meta name="msapplication-starturl" content="/"/>
<meta name="msapplication-window" content="width=800;height=600"/>

<!--Jquery:-->
<script src="js/jquery-1.10.2.min.js" type="text/javascript"></script>
<script type="text/javascript" src="./js/jquery.widget.min.js"></script>
<!--CSS-->
<link href="./css/opmaak.css" type="text/css" rel="stylesheet" />
<!--<link href="./css/jquery-ui-1.10.3.custom.css" rel="stylesheet" />--> 
 <link href="./css/modern.css" type="text/css" rel="stylesheet" /> 
<link href="./css/modern-responsive.css" type="text/css" rel="stylesheet" /><!-- -->
<link href="./css/metro-bootstrap.css" type="text/css" rel="stylesheet" />

<!--jquery datebox
<link href="./css/jqm-datebox.css" type="text/css" rel="stylesheet" />
<link href="./css/jquery.mobile.datebox.css" type="text/css" rel="stylesheet" />
-->

<!--JS metro ui-->

<!--<script type="text/javascript" src="./js/assets/jquery.mousewheel.min.js"></script>
<script type="text/javascript" src="./js/assets/moment.js"></script>
<script type="text/javascript" src="./js/assets/moment_langs.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/dropdown.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/accordion.js"></script>-->
<script type="text/javascript" src="./js/metro-button-set.js"></script>
<script type="text/javascript" src="./js/metro-touch-handler.js"></script>
<!--<script type="text/javascript" src="./js/modern/carousel.js"></script>-->
<script type="text/javascript" src="./js/metro-input-control.js"></script>
<!--<script type="text/javascript" src="./js/modern/pagecontrol.js"></script> Deze wel??-->
<!--<script type="text/javascript" src="./js/modern/rating.js"></script>-->
<script type="text/javascript" src="./js/metro-slider.js"></script>
<!--<script type="text/javascript" src="./js/modern/tile-slider.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/tile-drag.js"></script>-->
<!--<script type="text/javascript" src="./js/modern/calendar.js"></script>-->

<!--JS Other-->
<script src="./js/scrollto.js"></script>
<!--<script src="js/jquery-ui-1.10.3.custom.js"></script>-->
<?php
require 'checkLevel.inc';
require 'cons/afdwaka.con';

if($level >= 0){
	echo "<title>JvO Raspberry</title>";
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
	
	var numCat;
	var usernm = "<?php echo $usernm; ?>";

// $(document).ready(function(){ //code uit te voeren zodra de pagina geladen is
 	loadPage('bediening'); //de eerste pagina die geladen wordt als de website opent.
	$.ajaxSetup({
		cache: false
	});
 //}
 //);
//Javascript input-control functions
//Jeroen van Oorschot 2013
//Used with Raspberry Pi Domotica

 ////////////////////////////////INIT

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
/*
function setDateTimePickers(){
          var curr = new Date().getFullYear();
            var opt = {

            }

      //      opt.date = {preset : 'date'};
	//opt.datetime = { preset : 'datetime', minDate: new Date(2012,3,10,9,22), maxDate: new Date(2014,7,30,15,44), stepMinute: 5  };
	opt.time = {preset : 'time'};
	//opt.tree_list = {preset : 'list', labels: ['Region', 'Country', 'City']};
	//opt.image_text = {preset : 'list', labels: ['Cars']};
	//opt.select = {preset : 'select'};
	  /*<!--Script-->

            $('select.changes').bind('change', function() {
                var demo = $('#demo').val();
                $(".demos").hide();
                if (!($("#demo_"+demo).length))
                    demo = 'default';

                $("#demo_" + demo).show();
                $('#test_'+demo).val('').scroller('destroy').scroller($.extend(opt[$('#demo').val()], { theme: $('#theme').val(), mode: $('#mode').val(), display: $('#display').val(), lang: $('#language').val() }));
            });

            $('#demo').trigger('change');
			
			*/
			
   // $(".input-time").mobiscroll().datetime();
//$(".input-time").val('').scroller($.extend(opt.time, { theme: 'wp', mode:  'scroller', display: 'modal', lang: 'nl' }));
//$('#demo').trigger('change');
  //      };*/
//////////////////////UPDATE FUNCTIONS
function setColor(colorRGB){
	$(".fgColor").css("color",colorRGB); //foreground color
	$(".bgColor").css("background-color",colorRGB);//general class bgColor
	$('.input-slider').each(function() {
		//this.slider({position: 10}) //completeColor: colorRGB
		$(this).slider({completeColor: colorRGB});
	});
}

function postDB(pvalue, pwhere1, pwhere2, ptable){
	$.post('doUpdate.php', { value: pvalue, where1: pwhere1, where2: pwhere2, table: ptable })
			.done(function(data){
				if(data) window.alert(data); //usually not enough rights exception
			})
			.fail(function(data){ //xmlhttprequest failed
				window.alert("De server is niet bereikbaar, probeer later opnieuw");
			});
}

function bindActions(){
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
	$(".input-value").html("");
	
	
	
	
	
	//post functions
	
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
	$(".input-list").change(function() {//radio list items
			var name =$(this).attr('id'); //id van de hele option
			var checkedItem = 'input[name='+name+']:radio:checked'; 
			var val = $(checkedItem).attr('id'); //id of selected element
			postDB(val,'name',name,'settings');
			//window.alert(name+' met waarde '+val);
    }); 
	$('.input-slider').click(function() {
			var name =$(this).attr('id'); //id van de hele option
				$(this).slider({
				value: function(value){
					console.log(value);
					postDB(value,'name',name,'settings');
			   }
			})
			/*this.slider({
				change: function(value, slider){
					var name = $(this).attr('id');
					postDB(value,'name',name,'settings');
				}
			});*/
	});
	$('.div-slider').parent().parent().on('touchstart touchmove', function(e){ 
		 //prevent native touch activity like scrolling
		 e.preventDefault(); 
	});
	
	
	$(".colorSwatch").click(function(){  //color buttons
		   var colorRGB = $(this).css('background-color');
		   
		   //update db
			postDB(colorRGB,'usernm',usernm,'users');
		   //set color
		   setColor(colorRGB);


    });
}



function updateValues(){
    //$(".toestand").prop("checked", "checked");
	$.get('loadValues.php',	 { page: "bediening"}, 	function(data){
	   
		for(var key in data){
			var value = data[key];
			var key = key.split('_');
			var type = key[0];     //type and name as stored in DataBase
			var name = "#"+key[1]; //# for finding ID by jquery
            var find = ".input-"+type+"#"+key[1]; //Find jquery item with class and ID
           // window.alert(key+"_"+value);
			switch(type){
				case 'tf':
                    tf = (value=="true"?true:false);
                    console.log(find+tf);
					$(find).prop("checked", tf);
                    
				break;
				case 'media': //media controls
				break;
				case 'list':
                   // window.alert("list, value: "+value);
					$("input#"+value).prop('checked',true);	
				break;
				case 'color':
				break;
				case 'slider':
					$(find).slider({value: value});
				break;
				case 'time':
				break;
				case 'dayPicker':
				break;
				case 'value':
					$(name).html(value);
				break;
				default:
				break;
				} //end switch*/
			}
		}, 'json');//end function
		 //end $.get*/
}//end function

function loadPage(page2load){
	$('#cat-page').html('<img src="./images/preloader-w8-cycle-black.gif" />'); //  page loader
	
	 if(<?php echo $level ?>>=0){
		 $.get('loadPage.php',
		 { page: page2load},
		 	function(data){
				$('#pagetitle-title').html('<h1>'+page2load.toLowerCase()+'</h1>');
				$('#page-buttons').html(data.pbt); //page buttons
				$('#cat-buttons').html(data.cbt); // cat buttons
                $('#cat-page').html(data.cnt); //  page content
				numCat = data.nmct;

				setWidth(); //set the width of the page and the categories
				//initSliders(); //set the settings for all sliders, and the init values
				//setDateTimePickers(); //set the settings for all datetimepicker objects
				setColor(data.color); //set the initial color, read from the db
				
				bindActions(); //bind actions to all buttons and so.
				updateValues(); //set values
				setInterval(function(){updateValues()}, 5000) //periodically update the values, every 5 secs
			}
		,'json');
	 }
	 else{
		$("#container").html('<div class="error-bar">Je bent niet ingelogd. <a href="index.php" title="niet ingelogd">Klik hier om in te loggen</a></div>'); //show error bar
	 }
 }
 

function setWidth(){
	var w, h, rw;
	rw = window.innerWidth;
	w = rw*0.9-20;
	h = window.innerHeight-220;

	$(".cat").width(w);
	$(".cat").height(h);
	$("#cat-page").width(numCat*rw+80);
}


</script>
</head>
<body onResize="setWidth()" class="metrouicss">


<div id="container">
  <div id="page-buttons"></div>
  <div id="header">
  <!--<a onclick="updateValues()">udv</a>-->
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