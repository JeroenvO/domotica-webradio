<?php
header('Content-Type: text/html; charset=utf-8');
	if(!isset($_SESSION)) 
    { 
        session_start(); 
    } 
?>
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
		<script type="text/javascript" src="./js/jquery.widget.min.js"></script><!--also for metro ui-->
		<script type="text/javascript" src="./js/metro-input-control.js"></script>

		<link type="text/css" rel="stylesheet" href="./css/opmaak.css" />
		<link href="./css/metro-bootstrap.css" rel="stylesheet" />
<style>
.button{
	margin: 5px;
}</style>

		<!--<script type="text/javascript" src="./js/modern/input-control.js"></script>-->
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
	<body class="metro">
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
          			<p><span id="welcomeMsg"></span> <?php echo isset($fullname)?$fullname:'gast'; ?>, en welkom!</p>
          			<p> <!--Het is <span id="dateMsg"></span> en u-->Uw IP-adres is: <?php echo $_SERVER['REMOTE_ADDR']; ?></p>
                    <p>
			        <?php 
					if(isset($_SESSION['usernm'])){ //if loged in
						echo 'U bent ingelogd als '.$_SESSION['usernm'].'. U heeft niveau '.$_SESSION['level'].'. <br /><br />
						<a href="login.php?log=uit" class="button" title="Log uit">Log uit</a><br /><br />';
					}
					if($level >= 0){ //if valid user, if local or if logged in
						echo '<a href="control.php" class="button" title="ga verder">Ga naar control</a>';
						if($level > 1 && $local){ //show extra buttons if level is 2
							echo '<br /><br /><a class="button" href="http://192.168.1.104/loadPage.php?page=bediening&noCache=true" target="_blank" title="Reinit bediening">Reinit bediening</a>';
							echo '<br /><a class="button" href="http://192.168.1.104/loadPage.php?page=logboeken&noCache=true" target="_blank" title="Reinit logboeken">Reinit logboeken</a>';
							echo '<br /><a class="button" href="http://192.168.1.104/loadPage.php?page=gebruikers&noCache=true" target="_blank" title="Reinit gebruikers">Reinit gebruikers</a>';
							echo '<br /><a href="http://192.168.1.104/phpmyadmin">PhpMyAdmin</a>'; 
							 
							echo '<br /><a href="http://88.159.88.53">Bekijk website extern</a>'; 
						}
					}
					else{
						 //show the login form
						 echo 'Log hieronder in om naar de instellingen te gaan';

					?>
					<br />
                     <?php echo isset($_GET['e'])?'<br /><span style="background-color:red">Ongeldige gebruikersnaam of wachtwoord</span>':'' ?>
					  	<form action="login.php" method="post">
					    	<table>
					      		<tr id="gebruikersnaam">
					        		<td> Gebruikersnaam: </td>
					        		<td>
		   								<input type="text" name="gebruikersnaam" data-transform="input-control" />
									</td>
	            				</tr>
	          					<tr id="wachtwoord">
	            					<td> Wachtwoord: </td>
	            					<td>
	       								<input type="password" name="wachtwoord" data-transform="input-control" />
									</td>
	            				</tr>
	        				</table>
	        				<input type="submit" value="Inloggen" />
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