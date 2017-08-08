<?php
	if(!isset($_SESSION)) 
    { 
        session_start(); 
    } 
	require './checkLevel.inc';
	if($level > 0){
		require 'cons/afdwaka.con';
		$where1 = mysql_real_escape_string($_POST['where1']);	//where string
		$where2 = mysql_real_escape_string($_POST['where2']);
		$table = mysql_real_escape_string($_POST['table']);	//table to read or put the data
		$value = mysql_real_escape_string($_POST['value']);    //the value in case of an update
		if(isset($table)&&isset($where1)&&isset($where2)&& isset($value)){
			$changetime = $table=='settings'?', changetime=\''.floor(microtime(true)*100).'\'':'';
			$qry = 'update '.$table.' set value=\''.$value.'\''.$changetime.' where '.$where1.'="'.$where2.'"';
			if(!$res = $db_con->query($qry)){
				echo 'Fout in query: '.$db_con->error; 
				exit();
			}	
		}
		else{
			echo 'Niet alle variabelen zijn aangekomen. Probeer het later opnieuw.';	
		}
	}
	else{
		echo 'U heeft niet genoeg rechten voor deze actie';
	}
		
	





?>