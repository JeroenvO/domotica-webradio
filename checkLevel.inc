<?php
$ip = $_SERVER['REMOTE_ADDR'];
if(substr($ip,0,9)=='192.168.1')//local
{
	$local = true;
	if($ip == '192.168.1.100' || $ip == '192.168.1.101' || $ip == '192.168.1.102' || $ip == '192.168.1.103'){//a allowed local computer
		$msg = 'Lokale bediening';
		$level = 2;
		$usernm = 'local';
		$fullname = 'lokale gebruiker';
	}
	else{
		$msg = 'Lokale gast';
		$level = 0;	
		$usernm = 'localguest';
		$fullname = 'lokale gast';
	}
	
}
else{ //remote ip
	$local = false;
	if(isset($_SESSION['usernm'])){ //for remote, check session
		if ((isset($_SESSION['LAST_ACTIVITY']) && (time() - $_SESSION['LAST_ACTIVITY'] < 1800))&& //max 30 min from last change
			(time() - $_SESSION['CREATED'] < 3600)&&  //max 60 min from created.
			($_SERVER['HTTP_USER_AGENT']==$_SESSION['HTTP_USER_AGENT'])&& //use same browser
			($ip==$_SESSION['IP'])){ //use same ip

			$_SESSION['LAST_ACTIVITY'] = time(); // update last activity time stamp

			$msg = 'Buitenshuis bediening';
			$level = $_SESSION['level']; //als remote ingelogd, gebruik de level uit de session
			$usernm = $_SESSION['usernm'];
			$fullname = $_SESSION['fullname'];
		}
		else{//session no longer valid
			session_unset();     // unset $_SESSION variable for the run-time 
			session_destroy();   // destroy session data in storage.
			$msg = '1 Tijd verlopen';
			$level = -1;
		}
	}
	else{//no session, not logged in
		$msg = '2 Niet ingelogd';
		$level = -1;
	}
}

?>