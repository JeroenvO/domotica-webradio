<?php
session_start();

$pag_nam = $_GET['page'];

require 'checkLevel.inc';


if($level >=0 && isset($pag_nam)){

	require './cons/afdwaka.con';

	$qry_opt = 'select settings.name, settings.type, settings.value from RPi.settings where type IS NOT NULL order by vlgrd';
	if(!$res_opt = $db_con->query($qry_opt)){
		echo 'Fout in query options: '.$db_con->error; 
				exit();
	}
	
	$values = array();
	while($row_opt=$res_opt->fetch_assoc()){//each option
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