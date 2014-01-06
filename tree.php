<?php
/*
function getDBLevel($parent){
	$qry_pag = 'Select * from '.$table.' where parent=\''.$parent.'\' order by vlgrd';
	$res_pag = $db_con->query($qry_pag);
	
	while($row_pag=$res_pag->fetch_assoc()){
		echo "<h4>$res_pag['name']</h4>";
		getDBLevel($parent);
	}
	
}*/
	$table = 'settings';
	
	require './cons/afdwaka.con';
	
	//pages
	$qry_pag = 'Select * from '.$table.' where parent is NULL order by vlgrd';
	$res_pag = $db_con->query($qry_pag);
	while($row_pag=$res_pag->fetch_assoc()){
		echo "<h1>$res_pag['name']</h1>";
		//getDBLevel($res_pag['name']);
	}
?>