<?php
header('Content-Type: text/html; charset=utf-8');
if(!isset($_SESSION))
{session_start();}?>
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="robots" content="noindex, nofollow"/>
<meta name="author" content="Jeroen van Oorschot"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1"/>
<meta name="msapplication-tap-highlight" content="no"/>
<style>
html {
	-ms-user-select: none;
	user-select: none;
	touch-action: pan-x;
	content-zooming: none;
}
body {
	-ms-scroll-translation: vertical-to-horizontal;
}
</style>
<link href="./css/metro-bootstrap - gloednieuw.css" type="text/css" rel="stylesheet"/>
<link href="./css/opmaak.css" type="text/css" rel="stylesheet"/>
<link href="./css/iconFont.css" rel="stylesheet">
<script type="text/javascript" src="./js/jquery-2.1.1.min.js"></script>
<!--<script type="text/javascript" src="./js/jquery.widget.min.js"></script>-->
<script src="./js/timePicker.min.js"></script>

<script src="./js/colorPicker.min.js"></script>
<script src="./js/jquery.bpopup.min.js"></script>
<!--flot graphs --><script src="./js/jquery.flot.js"></script><script src="./js/jquery.flot.time.js"></script>
<!--JS scrollto--><script src="./js/scrollto.js"></script>
<script src="./js/GFunc.js"></script>
<!--
<script src="./js/jquery.widget.min.js"></script>
<script src="./js/metro-input-control.js"></script>
-->
<title>JvO Raspberry</title>
<?php
require'checkLevel.inc';//require'cons/afdwaka.con';?>
<script type="text/javascript">
var port = 600; //normally 600
var numCat;
var usernm="<?php echo isset($usernm)?$usernm:''; ?>";
var page;
var color;
$(document).ready(function(){
	login(usernm,'<?php echo isset($_SESSION["pwdhash"])?$_SESSION["pwdhash"]:""; ?>','<?php echo $_SERVER["HTTP_HOST"]?>',port);
	});

function sendSocket(data){
	if(SOCKET.readyState==1){
		console.log("Tx: "+data);
		SOCKET.send(data);
	}else{
		console.log('Socket Status: '+SOCKET.readyState+' (Closed)');
		if(confirm("De verbinding is verloren, opnieuw proberen?")){
			login(usernm,'<?php echo isset($_SESSION["pwdhash"])?$_SESSION["pwdhash"]:""; ?>','<?php echo $_SERVER["HTTP_HOST"]?>',port)}
	}
}
</script>
</head><body onResize="setWidth()" class="metro">
<div id="container">
  <div id="page-buttons"></div>
  <div id="header">
    <div id="pagetitle">
      <h1><a href="./index.php"><i class="icon-arrow-left-3 back-button"></i></a><span id="pagetitle-title"></span></h1>
    </div>
    <div id="cat-buttons"></div>
  </div>
  <div id="contentpage"><!--<img src="./images/preloader-w8-cycle-black.min.gif" width="64" height="64" id="loader"/>-->
    <div id="cat-page"></div></div><div id="footer">
    <div class="left">Jeroen van Oorschot</div>
<div id="color-swatches"><div class="cs bg-black" id="black"></div><div class="cs bg-lime" id="lime"></div><div class="cs bg-green" id="green"></div><div class="cs bg-emerald" id="emerald"></div>
<div class="cs bg-teal" id="teal"></div><div class="cs bg-cyan" id="cyan"></div><div class="cs bg-cobalt" id="cobalt"></div><div class="cs bg-indigo" id="indigo"></div>
<div class="cs bg-violet" id="violet"></div><div class="cs bg-pink" id="pink"></div><div class="cs bg-magenta" id="magenta"></div><div class="cs bg-crimson" id="crimson"></div>
<div class="cs bg-red" id="red"></div><div class="cs bg-orange" id="orange"></div><div class="cs bg-amber" id="amber"></div><div class="cs bg-yellow" id="yellow"></div>
<div class="cs bg-brown" id="brown"></div><div class="cs bg-olive" id="olive"></div><div class="cs bg-steel" id="steel"></div><div class="cs bg-mauve" id="mauve"></div>
<div class="cs bg-taupe" id="taupe"></div><div class="cs bg-gray" id="gray"></div></div></div></div>
</body></html>