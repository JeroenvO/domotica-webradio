<?php
if($local){
	$query = "Select value from users where usernm='local'";
}
else{
	if(isset($_SESSION['usernm'])){
		$query = 'Select value from users where usernm=\''.$_SESSION['usernm'].'\''; //value is the color
	}
	else{
		echo 'error';
		$query = false;
	}
}
if(!$result = $db_con->query($query)) trigger_error('Fout in query: '.$db_con->error); 
$row = $result->fetch_assoc();
$colorRGB = $row['value'];

?>