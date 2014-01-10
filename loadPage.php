<?php
	if(!isset($_SESSION)) 
    { 
        session_start(); 
    } 

require 'checkLevel.inc';

//get the requested page
if(isset($_GET['page'])){
	$pag_nam = mysql_real_escape_string($_GET['page']);
	
	if($level >=0 && $pag_nam){
		
		/* //slowdown
		for($i=0;$i<10000;$i++){
			$t = $t.'hoi';
			}
		*/

		//the file used to cache the created page	
		$file = $pag_nam.".txt";

		//connect to the database
		require './cons/afdwaka.con'; //also needed for color
		//the users chosen color
		include 'color.inc';

		if(isset($_GET['noCache'])||!file_exists($file)){ //update cache file
			//make variables to store the created page
			$cnt = ''; //content. Categories, subcats, options
			$cbt = ''; //category buttons, to scroll to a cat
			$pbt = ''; //page buttons, to go to the next page

			$table = 'settings';

			//pages
			$qry_pag = 'Select * from '.$table.' where parent is NULL order by vlgrd';
			$res_pag = $db_con->query($qry_pag);
			if(!$res_pag){
				echo 'Fout in query page: '.$db_con->error; 
				exit();
			}
			//check all pages, to make buttons in right top (PageBuTton)
			while($row_pag=$res_pag->fetch_assoc()){//pages
				if($row_pag['level'] <= $level){
					if($row_pag['name'] != $pag_nam){
						$pbt .= '<a class="button pag-button" id="'.$row_pag['name'].'" title="'.$row_pag['desc'].'"><i class="icon-'.$row_pag['value'].'"></i><span class="paglinktxt">'.ucfirst($row_pag['desc']).'</span></a>';
					}
					else{
						$pbt = '<a class="button smallButton pag-button" id="'.$pag_nam.'" title="'.$row_pag['desc'].'"><img src="./images/reload-icon-2.png" /></a>'.$pbt;
					}
				}
				else{
					//not allowed to view page
				}
			}
		
			$qry_cat = "select * from ".$table." where parent='$pag_nam' order by vlgrd";
			$res_cat = $db_con->query($qry_cat);
		
			if(!$res_cat){
				echo 'Fout in query cat: '.$db_con->error; 
						exit();
			}
			//all the categories in the chosen page. These are horizontally shown.
			for($i=0;$row_cat=$res_cat->fetch_assoc();$i++){//cat
				if($row_cat['level'] <= $level){
					//var_dump($row_cat);
					$cat = $row_cat['desc'];		
					$Cat = ucfirst($cat);
					$cnt.='<div class="cat" id="cat'.$i.'"><h3>'.$Cat.'</h3>';//category div and title
					$cbt .= '<a class="button left cat-button" id="cat'.$i.'link" title="Ga naar '.$Cat.'"><i class="icon-'.$row_cat['value'].'"></i><span class="catlinktxt">'.$Cat.'</span></a>';//cat buttons
						//subcategories, inside a category there are subcategories, these have a colored heading
						$qry_sbc = 'select * from '.$table.' where parent=\''.$row_cat['name'].'\' order by vlgrd';
						if(!$res_sbc = $db_con->query($qry_sbc)){
							echo 'Fout in query subcat: '.$db_con->error;
							exit();
						}
						while($row_sbc=$res_sbc->fetch_assoc()){//subcat
							if($row_sbc['level'] <= $level){
								$subcat = $row_sbc['desc'];	
								$cnt.='<div class="subcat"><h4 class="fgColor">'.strtolower($subcat).'</h4>';//subcat div and title
									//retrieve the options
									$qry_opt = 'select * from '.$table.' where parent=\''.$row_sbc['name'].'\' order by vlgrd';
									if(!$res_opt = $db_con->query($qry_opt)){
										echo 'Fout in query options: '.$db_con->error; 
												exit();
									}
									//each option for a setting within a subcategory
									while($row_opt=$res_opt->fetch_assoc()){//each option
										if($row_opt['level'] <= $level){
											//most options start with a text/title
											$cnt.='<div class="setting div-'.$row_opt['type'].'"><span class="body-text">'.ucfirst($row_opt['desc']).'</span><br />';
											//make option specific HTML to show the setting.
											switch($row_opt['type']){
												case 'tf': //default, true/false
													//$checked = "";//"($row_opt['value']=='true')?'checked=""':'';
													$cnt .='<label class="input-control switch">
																<input class="input-tf" type="checkbox" id="'.$row_opt['name'].'" '.$checked.' />
																<span class="helper bgColor"><span class="switch-text" id="'.$row_opt['name'].'-txt"></span></span>
															</label>';
												break;
												case 'toggle':
													$cnt .='<a class="button input-toggle" id="'.$row_opt['name'].'" >Schakel '.$row_opt['desc'].'</a>';
												break;
												case 'media': //media controls
												break;
												case 'list':
												$cnt .=  '<form class="input-list" id="'.$row_opt['name'].'">';
													//make items
													
													$qry_dwn = 'select '.$table.'.name, '.$table.'.desc from '.$table.' where parent=\''.$row_opt['name'].'\' order by vlgrd';
													if(!$res_dwn = $db_con->query($qry_dwn))
														echo 'Fout in query list: '.$db_con->error; 
													while($row_dwn=$res_dwn->fetch_assoc()){//each option
														$checked = "";//"($row_dwn['name']===$row_opt['value'])?'checked="checked"':'';
														$cnt .= '
															<div class="input-control radio default-style">
														<label>
															<input type="radio" name="'.$row_opt['name'].'" id="'.$row_dwn['name'].'" '.$checked.' />
															<span class="check"></span>
															'.$row_dwn['desc'].'
														</label>
													</div><br />';
													/*	<label>
															<input type="radio" name="'.$row_opt['name'].'" id="'.$row_dwn['name'].'" '.$checked.' />
															<span class="helper">'.$row_dwn['desc'].'</span>
														</label><br />
					';*/
													}
													$cnt .= '</form>';
													$res_dwn->close();
					
												break;
												case 'color':
												/*http://www.script-tutorials.com/html5-color-picker-canvas/*/
												break;
												case 'slider':
												$cnt .= '	
															<div class="input-slider slider" id="'.$row_opt['name'].'" data-init-value="'.$row_opt['value'].'"></div>
															<span class="input-slider" id="'.$row_opt['name'].'-txt">'.$row_opt['value'].'</span>
														';
												break;
												case 'time':
														/*
															The code for the plugin: 
														*/
															$cnt .= '<input type="number" value="" class="input-time" id="'.$row_opt['name'].'" />
															Ingesteld op: <span class="input-time" id="'.$row_opt['name'].'-txt"></span>
															
															';

												/*for($h=0;$h<24;$h++){
													$cnt .='<input id="'.$row_opt['name'].'" class="input-time" name="scroller" />';
												}
												for($m=0;$m<60;$m++){
													$cnt .='<input id="'.$row_opt['name'].'" class="input-time" name="scroller" />';
												}*/
												break;
												case 'dayPicker':
													$days = array('Ma','Di','Wo','Do','Vr','Za','Zo');
													for($j=0;$j<7;$j++){
														$cnt .= '<div class="input-control checkbox" data-role="input-control">
												<label>
													<input type="checkbox" class="input-dayPicker" id="'.$row_opt['name'].$j.'" />
													<span class="check"></span>
													'.$days[$j].'
												</label>
											</div>

															';/*<label class="input-control checkbox">
															'.$days[$i].'
																	<input class="input-dayPicker" type="checkbox" id="'.$row_opt['name'].$i.'"/>
																	<span class="check"></span>
																</label>*/
													}
												break;
												case 'table':
													//get data from logtable
													$qry_log = 'select * from '.$row_opt['value'].' order by timestamp desc limit 100';
													if(!$res_log = $db_con->query($qry_log)){
														echo 'Fout in query table: '.$db_con->error; 
																exit();
													}
													$cnt .= '<table class="output-table" id="'.$row_opt['name'].'"><th>name</th><th>desc</th><th>value</th><th>time</th><th>action</th>';
													while($row_log=$res_log->fetch_assoc()){//each log entry
														$cnt .= '<tr><td>'.$row_log['name'].'</td><td>'.$row_log['desc'].'</td><td>'.$row_log['value'].'</td><td>'.$row_log['timestamp'].'</td><td>'.$row_log['action'].'</td></tr>';
													}
													$cnt .= '</table>';
												break;
												case 'table_users':
													$qry_log = 'select * from '.$row_opt['value'].' order by timestamp desc limit 100';
													if(!$res_log = $db_con->query($qry_log)){
														echo 'Fout in query table: '.$db_con->error; 
																exit();
													}
													$cnt .= '<table class="output-table_users" id="'.$row_opt['name'].'" ><th>Gebruikersnaam</th><th>Volledige naam</th><th>Level</th><th>Kleur</th><th>Laatst ingelogd</th>';
													while($row_log=$res_log->fetch_assoc()){//each log entry
														$cnt .= '<tr><td>'.$row_log['usernm'].'</td><td>'.$row_log['fullname'].'</td><td>'.$row_log['level'].'</td><td>'.$row_log['value'].'</td><td>'.$row_log['timestamp'].'</td></tr>';
													}
																						$cnt .= '</table>';
												break;
												case 'table_logs_users':
													$qry_log = 'select * from '.$row_opt['value'].' order by timestamp desc limit 100';
													if(!$res_log = $db_con->query($qry_log)){
														echo 'Fout in query table: '.$db_con->error; 
																exit();
													}
													$cnt .= '<table class="output-table_logs_users" id="'.$row_opt['name'].'"><th>Gebruikersnaam</th><th>Locatie</th><th>Timestamp</th><th>Level</th>';
													while($row_log=$res_log->fetch_assoc()){//each log entry
														$cnt .= '<tr><td>'.$row_log['username'].'</td><td>'.$row_log['location'].'</td><td>'.$row_log['timestamp'].'</td><td>'.$row_log['level'].'</td></tr>';
													}
																						$cnt .= '</table>';
				
												break;
												case 'value':
													$cnt .='<span class="output-value" id="'.$row_opt['name'].'" >'.$row_opt['desc'].' '.$row_opt['value'].'</span>';
												break;
											}//end switch
											$cnt.="</div>\n"; //close setting
										}
										else{	
										  //not allowed to view option
										}
									}
									$res_opt->close();
									$cnt.="</div>\n";  //close subcat
							}
							else{
								//not allowed to see subcat
							}
						}
						$cnt.="</div>\n"; //close cat
						$res_sbc->close();
					}
					else{
						//not allowed to view subcat	
					}
				}
				$res_cat->close(); //end of db operations
			
				//make json from the created vars
				$json_array =  json_encode(array( 'pbt' => $pbt, 'cbt' => $cbt, 'cnt' => $cnt, 'nmct' => $i, 'color' => $colorRGB ));
				//store json in file for later use, cache
				$handle = fopen($file, 'w') or die("can't open file");
				fwrite($handle, $json_array);
				fclose($handle);
				//echo the json array so javascript can use it.
				echo $json_array;

		}else{ //give array from cache
			if(file_exists($file)){
				$array = json_decode(file_get_contents($file), true);
				//decode the array to update the color setting
				$array['color'] = $colorRGB;
				//echo the json array so javascript can use it.
				echo json_encode($array);
			}else{
				echo json_encode(array( 'pbt' => '', 'cbt' => '', 'cnt' => 'cache file not available', 'nmct' => '1', 'color' => '' ));;
			}
		}
	}
	else{
		echo json_encode(array( 'pbt' => '', 'cbt' => '', 'cnt' => 'Ho ho! Dit mag niet!', 'nmct' => '1', 'color' => '' ));
	}
}
else{
	echo 'Deze pagina kan niet zonder argument aangevraagd worden';
}


	?>