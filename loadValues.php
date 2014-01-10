<?php
	if(!isset($_SESSION)) 
    { 
        session_start(); 
    } 
//get requested page
if(isset($_GET['page'])){
	$pag_nam = mysql_real_escape_string($_GET['page']);
		
	//check level
	require 'checkLevel.inc';

	if($level >=0 && isset($pag_nam)){
		//connect to db
		require './cons/afdwaka.con';
		if($pag_nam=='bediening'){ //if bediening, then get all settings
			//get all settings
			$qry_opt = 'select settings.name, settings.type, settings.value, settings.level from RPi.settings where type IS NOT NULL order by vlgrd';
			if(!$res_opt = $db_con->query($qry_opt)){
				echo 'Fout in query options: '.$db_con->error; 
				exit();
			}
		}
		else{
			//get updated logs
			//not made yet
			//if page != bediening than a php error rises.
			//$qry_opt = 'select settings.name, settings.type, settings.value from RPi.settings where type IS NOT NULL order by vlgrd';
			//if(!$res_opt = $db_con->query($qry_opt)){
			//	echo 'Fout in query options: '.$db_con->error; 
			//	exit();
			//}

		}
		//get the values back.
		$values = array();
		//fill array with all options and values
		while($row_opt=$res_opt->fetch_assoc()){
			if($row_opt['level'] <= $level){
				$key = $row_opt['name'];
				$values[$key] = array($row_opt['type'], $row_opt['value']);
			}
		}
		echo json_encode($values);
	}
	else{
		echo 'Er is iets mis gegaan, de nieuwe waarden zijn niet opgehaald';
	}
}
else{
	echo 'Deze pagina kan niet zonder argument aangevraagd worden';
}