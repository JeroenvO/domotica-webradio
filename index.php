<?php session_start()?>
<!DOCTYPE html>
<html>
	<head>
		<?php
		require_once 'checkLevel.inc';
		?>
		<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />

		<meta name="robots" content="noindex, nofollow" />
		<meta name="author" content="Jeroen van Oorschot" />
		<meta name="description" content="Instellingenpagina RPI Jeroen van Oorschot" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1" />

		<script type="text/javascript" src="./js/jquery-2.0.3.min.js"></script>

		<link type="text/css" rel="stylesheet" href="./css/opmaak.css" />
		<link href="./css/modern.css" rel="stylesheet" />
		<link href="./css/modern-responsive.css" rel="stylesheet" />
		<link href="./css/site.css" rel="stylesheet" type="text/css" />

		<script type="text/javascript" src="./js/modern/input-control.js"></script>
		<title>Raspberry || Home</title>


		<script type="text/javascript">
		 $(document).ready(function(){ //code uit te voeren zodra de pagina geladen is
		 	$("#welcomeMsg").text(welcomeMsg());
			/*$("#dateMsg").text(curDate());*/
		 });

		//make a welcome message
		function welcomeMsg(){
			var nowDate = new Date();   
			var msg = "";
			if ( nowDate.getHours() < 12 ){/* hour is before noon */ 
				msg = "Goedemorgen"; 
			}else{  /* Hour is from noon to 5pm (actually to 5:59 pm) */ 
				if ( nowDate.getHours() >= 12 && nowDate.getHours() <= 17 ) {
					msg = "Goedemiddag";
				}else{  /* the hour is after 5pm, so it is between 6pm and midnight */ 
					if ( nowDate.getHours() > 17 && nowDate.getHours() <= 24 ) {
					     msg = "Goedenavond"; 
					}else  /* the hour is not between 0 and 24, so something is wrong :(  */ {
						msg = "Goedendag"; 
					}
				}
			}
			return msg;
		}

		//get date
		function curDate(){ 
			var dt = new Date();
			var str = dt.getDay()+'-'+dt.getMonth()+'-'+dt.getFullYear();
			return	str;
		}

		</script>
	</head>
	<body class="metrouicss">
		<div id="container">
      		<div id="header">
    			<div id="pagetitle">
          			<h1>Jeroen van Oorschot</h1>
        		</div>
  			</div>
      		<div id="contentpage">
    			<div id="block3left">
          			<h3>links</h3>
                    <ul class="linksPanel">
                        <li> <a href="http://www.vanoorschot.biz" title="De website van de boerderij van mijn vader en mijn oom.">Akkerbouwbedrijf Bouwlust</a> </li>
                        <li> <a href="http://jeroen.vanoorschot.biz" title="Jeroens website">Website Jeroen van Oorschot</a> </li>
                        <li> <a href="http://www.vanoorschot.biz/lego" title="Lego Projecten">Lego Mindstorms projecten</a> </li>
                        <li> <a href="http://www.oase.tue.nl" title="oase">TU/e Oase</a> </li>
                        <li> <a href="http://www.tweakers.net" title="tweakers">Tweakers.net</a></li>
                        <li> <a href="http://www.facebook.com" title="facebook">Facebook</a></li>
                    </ul>
        		</div>
    			<div id="block3center">
          			<p><span id="welcomeMsg"></span> <?php echo $fullname; ?>, en welkom!</p>
          			<p> <!--Het is <span id="dateMsg"></span> en u-->Uw IP-adres is: <?php echo $_SERVER['REMOTE_ADDR']; ?></p>
                    <p>
			        <?php 
					if(isset($_SESSION['usernm'])){ //if loged in
						echo 'U bent ingelogd als '.$_SESSION['usernm'].'. U heeft niveau '.$_SESSION['level'].'. <br /><a href="login.php?log=uit" class="button" title="Log uit">Log uit</a><br /><br />';
					}
					if($level >= 0){ //if valid user, if local or if logged in
						echo '<a href="settings.php" class="button" title="ga verder">Ga naar settings</a>';
						if($level > 1){ //show extra buttons if level is 2
							echo '<a href="poweroff.php" class="button" title="Raspberry uitzetten"><i class="icon-switch"></i>Raspberry uitzetten</a>';
							echo '<br /><a href="http://192.168.1.104/phpmyadmin">PhpMyAdmin</a>'; 
						}
						if($local){ //if local user, show link for extern viewing
							echo '<br /><a href="http://88.159.88.53">Bekijk website extern</a>'; 
						}
					}
					else{
						 //show the login form
						 echo 'Log hieronder in om naar de instellingen te gaan';

					?>
					  	<form action="login.php" method="post">
					    	<table class="hovered bordered">
					      		<tr id="gebruikersnaam" <?php echo $_GET['usrnm']?'class="'.$_GET['usrnm'].'"':'' ?>>
					        		<td> Gebruikersnaam: </td>
					        		<td>
					        			<div class="input-control text">
		   									<input type="text" name="gebruikersnaam" />
					    					<button class="btn-clear"></button>
										</div>
									</td>
	            					<?php echo $_GET['usrnm']?'<td>Onbekende gebruikersnaam</td>':''; ?>
	            				</tr>
	          					<tr id="wachtwoord" <?php echo $_GET['pswd']?'class="'.$_GET['pswd'].'"':'' ?>>
	            					<td> Wachtwoord: </td>
	            					<td>
	            						<div class="input-control password">
	       									<input type="password" name="wachtwoord" />
	       									<button class="btn-reveal"></button>
	   									</div>
									</td>
	            					<?php echo $_GET['pswd']?'<td>Verkeerd wachtwoord</td>':''; ?>
	            				</tr>
	        				</table>
	        				<input class="left bg-color-blue" type="submit" value="Inloggen" />
	      				</form>
          			<?php } ?>
        		</div>
  			</div>
    	</div>
		<div id="footer">
      		<div class="left">Gemaakt door Jeroen van Oorschot. 
    Styled with <a target="_blank" href="http://metroui.org.ua" class="navigation-text">Metro UI CSS</a>
    		</div>
		</div>
	</body>
</html>