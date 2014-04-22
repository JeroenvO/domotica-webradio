
<?php
/*
LoadData.php, to load data from a database to a ajax client
Jeroen van Oorschot 2014
Raspberry PI domotica
*/
	if(!isset($_SESSION)) 
    { 
        session_start(); 
    } 

require 'checkLevel.inc';

//get the requested page
if( isset($_GET['log']) && isset($_GET['start']) && $level >= 0){
	$log = mysql_real_escape_string($_GET['log']);
	$start = intval(mysql_real_escape_string($_GET['start']));
	if($start < 1389123003){
		echo 'invalid start time';
		exit();
	}
	$qryEnd = '';
	if(isset($_GET['end'])){
		$end = intval(mysql_real_escape_string($_GET['end']));
		if($end < 1389123003){
			echo 'invalid end time';
			exit();
		}
		$qryEnd = ' and UNIX_TIMESTAMP(timestamp)<='.$end;
	}

	//connect to the database
	require './cons/afdwaka.con'; //also needed for color

	//pages
	$qry = 'Select UNIX_TIMESTAMP(timestamp) as ts, value from '.$log.' where UNIX_TIMESTAMP(timestamp)>='.$start . $qryEnd;
	echo $qry;
	
	$res = $db_con->query($qry);
	if(!$res){
		echo 'Fout in query page: '.$db_con->error; 
		exit();
	}
	while($row=$res->fetch_assoc()){//pages
		echo $row['ts'].'  '.$row['value'].'<br />';
	}
}
?>